//! A small expression language for plotting functions of `x`.
//!
//! Numbers, `x`, the constants `pi` and `e`, the operators `+ - * / ^`,
//! parentheses, and the functions listed in [`FUNCTIONS`]. Multiplication
//! may be left out where it is unambiguous: `2x`, `3(x - 1)`, `2 sin(x)`.

#[derive(Debug, Clone, Copy, PartialEq)]
enum Func {
    Sin,
    Cos,
    Tan,
    Exp,
    Ln,
    Log10,
    Log2,
    Sqrt,
    Abs,
    Tanh,
    Sigmoid,
    Relu,
    Floor,
}

pub const FUNCTIONS: &[&str] =
    &["sin", "cos", "tan", "exp", "ln", "log", "log2", "sqrt", "abs", "tanh", "sigmoid", "relu", "floor"];

#[derive(Debug, Clone, PartialEq)]
enum Node {
    Num(f64),
    X,
    Neg(Box<Node>),
    Bin(char, Box<Node>, Box<Node>),
    Call(Func, Box<Node>),
}

#[derive(Debug, Clone, PartialEq)]
pub struct Expr(Node);

#[derive(Debug, Clone, PartialEq)]
enum Token {
    Num(f64),
    Ident(String),
    Op(char),
    Open,
    Close,
}

fn tokens(src: &str) -> Result<Vec<Token>, String> {
    let chars: Vec<char> = src.chars().collect();
    let mut out = vec![];
    let mut i = 0;
    while i < chars.len() {
        let c = chars[i];
        if c.is_whitespace() {
            i += 1;
        } else if c.is_ascii_digit() || c == '.' {
            let start = i;
            while i < chars.len() && (chars[i].is_ascii_digit() || chars[i] == '.') {
                i += 1;
            }
            let text: String = chars[start..i].iter().collect();
            out.push(Token::Num(text.parse().map_err(|_| format!("`{text}` is not a number"))?));
        } else if c.is_ascii_alphabetic() {
            let start = i;
            while i < chars.len() && (chars[i].is_ascii_alphanumeric() || chars[i] == '_') {
                i += 1;
            }
            out.push(Token::Ident(chars[start..i].iter().collect()));
        } else if c == '*' && chars.get(i + 1) == Some(&'*') {
            out.push(Token::Op('^'));
            i += 2;
        } else if "+-*/^".contains(c) {
            out.push(Token::Op(c));
            i += 1;
        } else if c == '(' {
            out.push(Token::Open);
            i += 1;
        } else if c == ')' {
            out.push(Token::Close);
            i += 1;
        } else {
            return Err(format!("`{c}` is not allowed in a function; use numbers, x, + - * / ^ and parentheses"));
        }
    }
    Ok(out)
}

struct Parser {
    tokens: Vec<Token>,
    pos: usize,
}

impl Parser {
    fn peek(&self) -> Option<&Token> {
        self.tokens.get(self.pos)
    }

    fn eat(&mut self, op: char) -> bool {
        if self.peek() == Some(&Token::Op(op)) {
            self.pos += 1;
            return true;
        }
        false
    }

    fn sum(&mut self) -> Result<Node, String> {
        let mut left = self.product()?;
        loop {
            let op = if self.eat('+') {
                '+'
            } else if self.eat('-') {
                '-'
            } else {
                return Ok(left);
            };
            left = Node::Bin(op, Box::new(left), Box::new(self.product()?));
        }
    }

    fn product(&mut self) -> Result<Node, String> {
        let mut left = self.unary()?;
        loop {
            let op = if self.eat('*') {
                '*'
            } else if self.eat('/') {
                '/'
            } else if matches!(self.peek(), Some(Token::Num(_) | Token::Ident(_) | Token::Open)) {
                '*' // implied: 2x, 3(x - 1)
            } else {
                return Ok(left);
            };
            left = Node::Bin(op, Box::new(left), Box::new(self.unary()?));
        }
    }

    fn unary(&mut self) -> Result<Node, String> {
        if self.eat('-') {
            return Ok(Node::Neg(Box::new(self.unary()?)));
        }
        let base = self.primary()?;
        if self.eat('^') {
            // Right-associative, and the exponent may carry its own sign.
            return Ok(Node::Bin('^', Box::new(base), Box::new(self.unary()?)));
        }
        Ok(base)
    }

    fn primary(&mut self) -> Result<Node, String> {
        let token = self.tokens.get(self.pos).cloned();
        self.pos += 1;
        match token {
            Some(Token::Num(n)) => Ok(Node::Num(n)),
            Some(Token::Open) => {
                let inner = self.sum()?;
                self.close()?;
                Ok(inner)
            }
            Some(Token::Ident(name)) => {
                let func = match name.as_str() {
                    "x" => return Ok(Node::X),
                    "pi" => return Ok(Node::Num(std::f64::consts::PI)),
                    "e" => return Ok(Node::Num(std::f64::consts::E)),
                    "sin" => Func::Sin,
                    "cos" => Func::Cos,
                    "tan" => Func::Tan,
                    "exp" => Func::Exp,
                    "ln" => Func::Ln,
                    "log" => Func::Log10,
                    "log2" => Func::Log2,
                    "sqrt" => Func::Sqrt,
                    "abs" => Func::Abs,
                    "tanh" => Func::Tanh,
                    "sigmoid" => Func::Sigmoid,
                    "relu" => Func::Relu,
                    "floor" => Func::Floor,
                    _ => {
                        return Err(format!(
                            "unknown name `{name}`; the variable is `x`, the constants are pi and e, and the functions are: {}",
                            FUNCTIONS.join(", ")
                        ))
                    }
                };
                if self.peek() != Some(&Token::Open) {
                    return Err(format!("`{name}` needs its argument in parentheses, as in `{name}(x)`"));
                }
                self.pos += 1;
                let arg = self.sum()?;
                self.close()?;
                Ok(Node::Call(func, Box::new(arg)))
            }
            Some(Token::Close) => Err("there is a `)` with nothing before it".to_string()),
            Some(Token::Op(op)) => Err(format!("`{op}` has nothing to its left")),
            None => Err("the function ends too early".to_string()),
        }
    }

    fn close(&mut self) -> Result<(), String> {
        if self.peek() == Some(&Token::Close) {
            self.pos += 1;
            return Ok(());
        }
        Err("a `(` is never closed".to_string())
    }
}

impl Expr {
    pub fn parse(src: &str) -> Result<Expr, String> {
        let mut parser = Parser { tokens: tokens(src)?, pos: 0 };
        if parser.tokens.is_empty() {
            return Err("the function is empty".to_string());
        }
        let node = parser.sum()?;
        match parser.peek() {
            None => Ok(Expr(node)),
            Some(Token::Close) => Err("there is a `)` too many".to_string()),
            Some(_) => Err("the function has something left over at the end".to_string()),
        }
    }

    pub fn eval(&self, x: f64) -> f64 {
        fn go(n: &Node, x: f64) -> f64 {
            match n {
                Node::Num(v) => *v,
                Node::X => x,
                Node::Neg(a) => -go(a, x),
                Node::Bin(op, a, b) => {
                    let (a, b) = (go(a, x), go(b, x));
                    match op {
                        '+' => a + b,
                        '-' => a - b,
                        '*' => a * b,
                        '/' => a / b,
                        _ => a.powf(b),
                    }
                }
                Node::Call(f, a) => {
                    let a = go(a, x);
                    match f {
                        Func::Sin => a.sin(),
                        Func::Cos => a.cos(),
                        Func::Tan => a.tan(),
                        Func::Exp => a.exp(),
                        Func::Ln => a.ln(),
                        Func::Log10 => a.log10(),
                        Func::Log2 => a.log2(),
                        Func::Sqrt => a.sqrt(),
                        Func::Abs => a.abs(),
                        Func::Tanh => a.tanh(),
                        Func::Sigmoid => 1.0 / (1.0 + (-a).exp()),
                        Func::Relu => a.max(0.0),
                        Func::Floor => a.floor(),
                    }
                }
            }
        }
        go(&self.0, x)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn at(src: &str, x: f64) -> f64 {
        Expr::parse(src).unwrap_or_else(|e| panic!("{src}: {e}")).eval(x)
    }

    #[test]
    fn evaluates() {
        assert_eq!(at("(x - 3)^2", 5.0), 4.0);
        assert_eq!(at("-x^2", 3.0), -9.0);
        assert_eq!(at("2^-1", 0.0), 0.5);
        assert_eq!(at("2x + 1", 4.0), 9.0);
        assert_eq!(at("3(x - 1)", 2.0), 3.0);
        assert_eq!(at("2 ** 3 ** 2", 0.0), 512.0);
        assert_eq!(at("1 - 2 - 3", 0.0), -4.0);
        assert_eq!(at("8 / 4 / 2", 0.0), 1.0);
        assert_eq!(at("relu(x)", -2.0), 0.0);
        assert_eq!(at("sigmoid(0)", 0.0), 0.5);
        assert!((at("sin(pi / 2)", 0.0) - 1.0).abs() < 1e-12);
        assert!((at("ln(e)", 0.0) - 1.0).abs() < 1e-12);
    }

    #[test]
    fn explains_mistakes() {
        let err = |src: &str| Expr::parse(src).unwrap_err();
        assert!(err("y + 1").contains("unknown name `y`"));
        assert!(err("sin x").contains("needs its argument in parentheses"));
        assert!(err("(x + 1").contains("never closed"));
        assert!(err("x + 1)").contains("too many"));
        assert!(err("x +").contains("ends too early"));
        assert!(err("x = 2").contains("`=` is not allowed"));
        assert!(err("").contains("empty"));
    }
}
