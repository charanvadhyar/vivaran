"""Infix to postfix with a trace, and postfix evaluation with a trace."""
PREC = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}
RIGHT = {'^'}
def to_postfix(expr):
    out, st, trace = [], [], []
    for ch in expr.replace(' ', ''):
        if ch.isalnum():
            out.append(ch)
        elif ch == '(':
            st.append(ch)
        elif ch == ')':
            while st[-1] != '(':
                out.append(st.pop())
            st.pop()
        else:
            while st and st[-1] != '(' and (PREC[st[-1]] > PREC[ch] or (PREC[st[-1]] == PREC[ch] and ch not in RIGHT)):
                out.append(st.pop())
            st.append(ch)
        trace.append((ch, ''.join(st), ' '.join(out)))
    while st:
        out.append(st.pop())
    trace.append(('end', '', ' '.join(out)))
    return ' '.join(out), trace

def eval_postfix(tokens):
    st, trace = [], []
    for t in tokens.split():
        if t.lstrip('-').isdigit():
            st.append(int(t))
        else:
            b, a = st.pop(), st.pop()
            st.append({'+': a + b, '-': a - b, '*': a * b, '/': a // b, '^': a ** b}[t])
        trace.append((t, st[:]))
    return st[0], trace
