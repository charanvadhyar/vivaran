//! Targets: how a script names an object or a part of one.
//!
//! | Form            | Meaning                                              |
//! | --------------- | ---------------------------------------------------- |
//! | `arr`           | the whole object                                     |
//! | `arr[3]`        | part 3, zero-based: array cell, table row, math line |
//! | `arr[0..3]`     | parts 0, 1, 2 (end exclusive, as in Rust)            |
//! | `arr[0..=3]`    | parts 0 to 3 (end inclusive)                         |
//! | `tbl[2][1]`     | table cell: row 2, column 1                          |
//! | `net.h1`        | named part: diagram node, table column               |
//! | `net.h1->out`   | diagram edge from node `h1` to node `out`            |
//!
//! Which forms an object accepts is decided by its family.

use serde::Deserialize;
use std::fmt;

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(try_from = "String")]
pub struct Target {
    pub object: String,
    pub part: Part,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Part {
    Whole,
    Index(usize),
    /// Half-open: `start..end`, with `start < end`.
    Range { start: usize, end: usize },
    Cell { row: usize, col: usize },
    Name(String),
    Edge { from: String, to: String },
}

impl Target {
    pub fn whole(object: impl Into<String>) -> Self {
        Target { object: object.into(), part: Part::Whole }
    }

    pub fn is_whole(&self) -> bool {
        self.part == Part::Whole
    }
}

pub fn is_valid_id(s: &str) -> bool {
    let mut chars = s.chars();
    matches!(chars.next(), Some(c) if c.is_ascii_lowercase() || c == '_')
        && chars.all(|c| c.is_ascii_lowercase() || c.is_ascii_digit() || c == '_')
}

/// Names of parts (nodes, columns) are a little looser than object ids:
/// capitals and a leading digit are fine, so `net.H1` and `tree.7` work.
pub fn is_valid_name(s: &str) -> bool {
    !s.is_empty() && s.chars().all(|c| c.is_ascii_alphanumeric() || c == '_')
}

impl TryFrom<String> for Target {
    type Error = String;

    fn try_from(s: String) -> Result<Self, String> {
        s.parse()
    }
}

impl std::str::FromStr for Target {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, String> {
        let bad = |why: &str| format!("invalid target `{s}`: {why}");

        let split = s.find(['[', '.']).unwrap_or(s.len());
        let (object, rest) = s.split_at(split);
        if !is_valid_id(object) {
            return Err(bad(
                "an object id must start with a lowercase letter or `_` and use only lowercase letters, digits and `_`",
            ));
        }

        let part = if rest.is_empty() {
            Part::Whole
        } else if let Some(name) = rest.strip_prefix('.') {
            match name.split_once("->") {
                Some((from, to)) if is_valid_name(from) && is_valid_name(to) => {
                    Part::Edge { from: from.to_string(), to: to.to_string() }
                }
                Some(_) => return Err(bad("an edge is written `object.from->to`")),
                None if is_valid_name(name) => Part::Name(name.to_string()),
                None => return Err(bad("a part name uses only letters, digits and `_`")),
            }
        } else {
            parse_brackets(rest).map_err(|why| bad(&why))?
        };
        Ok(Target { object: object.to_string(), part })
    }
}

/// `[i]`, `[a..b]`, `[a..=b]` or `[row][col]`.
fn parse_brackets(rest: &str) -> Result<Part, String> {
    let inner = rest
        .strip_prefix('[')
        .and_then(|r| r.strip_suffix(']'))
        .ok_or("missing closing `]`")?;

    if let Some((row, col)) = inner.split_once("][") {
        return Ok(Part::Cell { row: number(row)?, col: number(col)? });
    }
    if let Some((a, b)) = inner.split_once("..=") {
        let (start, last) = (number(a)?, number(b)?);
        if start > last {
            return Err(format!("range {start}..={last} is empty"));
        }
        Ok(Part::Range { start, end: last + 1 })
    } else if let Some((a, b)) = inner.split_once("..") {
        let (start, end) = (number(a)?, number(b)?);
        if start >= end {
            return Err(format!(
                "range {start}..{end} is empty (the end is exclusive; use {start}..={end} to include it)"
            ));
        }
        Ok(Part::Range { start, end })
    } else {
        Ok(Part::Index(number(inner)?))
    }
}

fn number(t: &str) -> Result<usize, String> {
    t.trim()
        .parse::<usize>()
        .map_err(|_| format!("`{t}` is not a non-negative whole number"))
}

impl fmt::Display for Part {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Part::Whole => Ok(()),
            Part::Index(i) => write!(f, "[{i}]"),
            Part::Range { start, end } => write!(f, "[{start}..{end}]"),
            Part::Cell { row, col } => write!(f, "[{row}][{col}]"),
            Part::Name(name) => write!(f, ".{name}"),
            Part::Edge { from, to } => write!(f, ".{from}->{to}"),
        }
    }
}

impl fmt::Display for Target {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}{}", self.object, self.part)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn t(s: &str) -> Result<Target, String> {
        s.parse()
    }

    #[test]
    fn parses_all_forms() {
        assert_eq!(t("arr").unwrap().part, Part::Whole);
        assert_eq!(t("arr[3]").unwrap().part, Part::Index(3));
        assert_eq!(t("arr[0..3]").unwrap().part, Part::Range { start: 0, end: 3 });
        assert_eq!(t("arr[0..=3]").unwrap().part, Part::Range { start: 0, end: 4 });
        assert_eq!(t("tbl[2][1]").unwrap().part, Part::Cell { row: 2, col: 1 });
        assert_eq!(t("net.h1").unwrap().part, Part::Name("h1".into()));
        assert_eq!(t("tree.7").unwrap().part, Part::Name("7".into()));
        assert_eq!(t("net.h1->out").unwrap().part, Part::Edge { from: "h1".into(), to: "out".into() });
        assert_eq!(t("my_arr2[1]").unwrap().object, "my_arr2");
    }

    #[test]
    fn rejects_malformed() {
        for bad in [
            "", "Arr", "arr[", "arr[x]", "arr[-1]", "arr[3..3]", "arr[4..=2]", "2arr", "arr[1]x", "net.", "net.a->",
            "net.a b", "tbl[1][", "tbl[1][x]",
        ] {
            assert!(t(bad).is_err(), "`{bad}` should be rejected");
        }
    }

    #[test]
    fn displays_round_trip() {
        for s in ["arr", "arr[3]", "arr[0..3]", "tbl[2][1]", "net.h1", "net.h1->out"] {
            assert_eq!(t(s).unwrap().to_string(), s);
        }
    }
}
