"""DSA Module 1, video 7: stacks, infix to postfix, postfix evaluation."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa1")
from common import Script
from h import *
from stk import to_postfix, eval_postfix

P, TR = to_postfix("A+B*(C-D)/E")
assert P == "A B C D - * E / +" and len(TR) == 12
Q1, _ = to_postfix("(A+B)*(C-D)/E^F"); assert Q1 == "A B + C D - * E F ^ /"
V, VT = eval_postfix("2 3 4 * + 5 -"); assert V == 9 and [x[1] for x in VT] == [[2], [2, 3], [2, 3, 4], [2, 12], [14], [14, 5], [9]]
Q2, Q2T = eval_postfix("8 2 3 ^ / 2 3 * + 5 1 * -"); assert Q2 == 2
assert [x[1] for x in Q2T] == [[8], [8, 2], [8, 2, 3], [8, 8], [1], [1, 2], [1, 2, 3], [1, 6], [7], [7, 5], [7, 5, 1], [7, 5], [2]]
def balanced(s):
    st = []; pair = {')': '(', ']': '[', '}': '{'}
    for ch in s:
        if ch in '([{': st.append(ch)
        elif ch in pair:
            if not st or st.pop() != pair[ch]: return False
    return not st
assert balanced("{[()]}") and not balanced("([)]") and not balanced("(()")
sk = []; popped = []
for op in ["push 1", "push 2", "push 3", "pop", "push 4", "pop", "pop"]:
    if op == "pop": popped.append(sk.pop())
    else: sk.append(int(op.split()[1]))
assert sk == [1] and popped == [3, 4, 2]
fmt = lambda r: [r[0], r[1] or "empty", r[2]]

s = Script("Stacks")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Last in, first out"],
    [2, "A stack in an array"],
    [3, "A stack as a linked list"],
    [4, "Checking brackets"],
    [5, "Infix to postfix: the rules"],
    [6, "Infix to postfix: a trace"],
    [7, "Evaluating postfix"],
    [8, "Exam question"]]})
s.obj({"id": "ops", "type": "table", "region": "center", "columns": ["operation", "does", "cost"], "rows": [
    ["push(x)", "put x on top", "Θ(1)"],
    ["pop()", "remove and return the top", "Θ(1)"],
    ["peek()", "look at the top", "Θ(1)"],
    ["isEmpty()", "is there nothing on it?", "Θ(1)"],
    ["only the top is reachable", "last in, first out: LIFO", ""]]})
s.obj({"id": "sa", "type": "array", "region": "right", "values": ["", "", "", "", ""]})
s.obj({"id": "top", "type": "pointer", "label": "top", "target": "sa[0]"})
s.obj({"id": "sc", "type": "code", "region": "left", "language": "text", "lines": [
    "PUSH(S, x)",
    "    if S.top == n - 1: error \"overflow\"",
    "    S.top = S.top + 1",
    "    S[S.top] = x",
    "POP(S)",
    "    if S.top == -1: error \"underflow\"",
    "    S.top = S.top - 1",
    "    return S[S.top + 1]"]})
s.obj({"id": "ll", "type": "table", "region": "center", "columns": ["linked stack", ""], "rows": [
    ["push", "new node at the head; head = new node"],
    ["pop", "take the head's value; head = head.next"],
    ["empty", "head is null"],
    ["overflow", "only when memory runs out"],
    ["cost", "Θ(1) each, plus one pointer per element"]]})
s.obj({"id": "br", "type": "table", "region": "center", "columns": ["input", "what happens", "result"], "rows": [
    ["{ [ ( ) ] }", "( matches ), [ matches ], { matches }", "balanced"],
    ["( [ ) ]", ") arrives while [ is on top", "not balanced"],
    ["( ( )", "input ends with ( still on the stack", "not balanced"],
    ["rule", "push openers; on a closer, pop and compare", "empty at the end"]]})
s.obj({"id": "ru", "type": "table", "region": "center", "columns": ["symbol", "action"], "rows": [
    ["operand", "write it to the output"],
    ["(", "push it"],
    [")", "pop to the output until (, then discard both"],
    ["operator", "pop while the top has higher precedence, or equal and left-associative; then push"],
    ["end", "pop everything to the output"],
    ["precedence", "^ highest (right-associative), then * /, then + −"]]})
s.obj({"id": "t1", "type": "table", "region": "center", "columns": ["symbol", "stack", "output"], "rows": [[r[0], "", ""] for r in TR[:6]]})
s.obj({"id": "t2", "type": "table", "region": "center", "columns": ["symbol", "stack", "output"], "rows": [[r[0], "", ""] for r in TR[6:]]})
s.obj({"id": "ev", "type": "array", "region": "center", "values": []})
s.obj({"id": "evin", "type": "array", "region": "center", "values": ["2", "3", "4", "*", "+", "5", "−"]})
s.obj({"id": "evp", "type": "pointer", "label": "next", "target": "evin[0]"})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["a) convert (A + B) * (C − D) / E ^ F to postfix"],
    ["b) evaluate the postfix 8 2 3 ^ / 2 3 * + 5 1 * −"],
    ["c) push 1, push 2, push 3, pop, push 4, pop, pop: what is popped, and what is left?"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "answer"], "rows": [
    ["a", "( A + B ) → A B +;  ( C − D ) → C D −;  * comes before /", "A B + C D − * E F ^ /"],
    ["a", "^ outranks /, so E F ^ is formed before /", ""],
    ["b", "8 / 2³ = 8 / 8 = 1;  1 + 2 × 3 = 7", ""],
    ["b", "7 − 5 × 1 = 2", "2"],
    ["c", "popped 3, then 4, then 2", "left: 1"]]})

s.scene("intro")
s.step("A stack lets you touch only one end. That one restriction makes it the structure behind function calls, undo buttons, the back button of your browser, and every calculator. This video builds a stack and uses it to evaluate expressions.", [s.head("Stacks")])
s.step("Here are the eight stages.", show("stages"))
s.step("What a stack is, a stack in an array, a stack as a linked list, and checking brackets.", [hl("stages[0..=3]")])
s.step("Then converting infix expressions to postfix, a full trace, evaluating postfix, and an exam question.", [hl("stages[4..=7]")])

s.scene("lifo")
s.step("Stage 1: a stack is like a pile of plates. Push puts a plate on top.", [s.head("Stage 1 of 8: last in, first out")] + hide("stages") + show("ops") + [hl("ops[0]")])
s.step("Pop removes the top plate and gives it back. Peek just looks at it.", [hl("ops[1..=2]")])
s.step("isEmpty asks whether there is anything left. Every operation costs Theta of 1.", [hl("ops[3]")])
s.step("Only the top is reachable, so the last item pushed is the first popped: LIFO, last in, first out.", [hl("ops[4]"), s.take("LIFO: push and pop at the top only")])

s.scene("array")
s.step("Stage 2: a stack in an array of size n. top holds the index of the top element, minus 1 when the stack is empty.", [s.head("Stage 2 of 8: a stack in an array"), s.untake()] + hide("ops") + show("sc", "sa") + [ml("sc", 1, 4)])
s.step("Push 5: top goes from minus 1 to 0, and 5 is stored there.", [st("sa[0]", 5)] + show("top"))
s.step("Push 8, then push 3. top is now 2.", [st("sa[1]", 8), pt("top", "sa[1]", 0.1), st("sa[2]", 3, 0.5), pt("top", "sa[2]", 0.6)])
s.step("Pop: it returns 3 and moves top back to 1. The 3 is still in the cell, but it is no longer part of the stack.", [ml("sc", 5, 8), pt("top", "sa[1]"), dim("sa[2]", 0.3)])
s.step("Push 7 overwrites that cell. Pushing when top is n minus 1 is overflow; popping when top is minus 1 is underflow. Both must be checked.", [st("sa[2]", 7), rs("sa[2]", 0.2), pt("top", "sa[2]", 0.3), ml("sc", 2, 2), s.take("top = −1 empty · top = n − 1 full")])

s.scene("ll")
s.step("Stage 3: a stack can also be a linked list, with the top at the head. Push makes a new node and points it at the old head.", [s.head("Stage 3 of 8: a linked stack"), s.untake()] + hide("sc", "sa", "top") + show("ll") + [hl("ll[0]")])
s.step("Pop takes the head's value and moves head to the next node.", [hl("ll[1]")])
s.step("Empty means head is null, and there is no fixed size: overflow happens only when memory runs out.", [hl("ll[2..=3]")])
s.step("Both operations stay Theta of 1. The cost is one extra pointer per element. Linked lists get their own video soon.", [hl("ll[4]"), s.take("array: fixed size · linked: grows, costs a pointer")])

s.scene("br")
s.step("Stage 4: a first use. Are the brackets in an expression balanced? Push every opening bracket; on a closing one, pop and check that they match.", [s.head("Stage 4 of 8: checking brackets"), s.untake()] + hide("ll") + show("br") + [hl("br[3]")])
s.step("Brace, bracket, parenthesis, then their closers in reverse order. Each closer matches the top: balanced.", [hl("br[0]")])
s.step("Parenthesis, bracket, then a closing parenthesis. The top is the bracket: mismatch, not balanced, even though the counts are right.", [hl("br[1]")])
s.step("Two opening parentheses and one closing: the input ends with one still on the stack. Not balanced. A balanced input ends with an empty stack.", [hl("br[2]"), s.take("push openers · match closers · end empty")])

s.scene("rules")
s.step("Stage 5: we write A plus B, the operator in between: infix. Postfix puts the operator after its operands: A B plus. It needs no brackets and no precedence rules, so machines evaluate it easily.", [s.head("Stage 5 of 8: infix to postfix"), s.untake()] + hide("br") + show("ru"))
s.step("Converting uses a stack of operators. An operand goes straight to the output. An opening bracket is pushed.", [hl("ru[0..=1]")])
s.step("A closing bracket pops operators to the output until the matching opening bracket, and both brackets are thrown away.", [hl("ru[2]")])
s.step("An operator first pops every operator on top with higher precedence, or equal precedence if it groups left to right. Then it is pushed.", [hl("ru[3]")])
s.step("At the end, pop whatever is left. Power is highest and groups right to left; then times and divide; then plus and minus.", [hl("ru[4..=5]"), s.take("operands out · operators wait on the stack")])

s.scene("trace")
s.step("Stage 6: convert A plus B times, bracket, C minus D, close bracket, divide E. A goes out. Plus is pushed. B goes out.", [s.head("Stage 6 of 8: a trace"), s.untake()] + hide("ru") + show("t1") + [x for i in range(3) for x in (st(f"t1[{i}][1]", fmt(TR[i])[1], round(0.25 * i, 2)), st(f"t1[{i}][2]", TR[i][2], round(0.25 * i + 0.1, 2)))])
s.step("Times has higher precedence than plus, so plus stays and times is pushed on top. The bracket is pushed.", [x for i in (3, 4) for x in (st(f"t1[{i}][1]", TR[i][1]), st(f"t1[{i}][2]", TR[i][2], 0.1))] + [hl("t1[3]")])
s.step("C goes out.", [st("t1[5][1]", TR[5][1]), st("t1[5][2]", TR[5][2], 0.1), hl("t1[5]")])
s.step("Minus is pushed: inside a bracket, nothing below the bracket is popped. D goes out.", hide("t1") + show("t2") + [x for i in (0, 1) for x in (st(f"t2[{i}][1]", TR[6 + i][1], 0.2 * i), st(f"t2[{i}][2]", TR[6 + i][2], 0.2 * i + 0.1))])
s.step("The closing bracket pops minus to the output, and the brackets vanish.", [st("t2[2][1]", TR[8][1]), st("t2[2][2]", TR[8][2], 0.2), hl("t2[2]")])
s.step("Divide has the same precedence as times, and they group left to right, so times is popped first. Plus has lower precedence, so it stays. Divide is pushed.", [st("t2[3][1]", TR[9][1]), st("t2[3][2]", TR[9][2], 0.2), hl("t2[3]")])
s.step("E goes out. At the end, pop divide, then plus. The answer: A B C D minus times E divide plus.", [st("t2[4][1]", TR[10][1]), st("t2[4][2]", TR[10][2], 0.1), st("t2[5][1]", "empty", 0.3), st("t2[5][2]", TR[11][2], 0.4), mk("t2[5][2]", 0.7), s.take("A + B * (C − D) / E → A B C D − * E / +")])

s.scene("eval")
s.step("Stage 7: evaluating postfix needs a stack of numbers. Take 2 3 4 times plus 5 minus. Numbers are pushed.", [s.head("Stage 7 of 8: evaluating postfix"), s.untake()] + hide("t2") + show("evin", "ev", "evp"))
s.step("2, 3, 4: pushed.", [ins("ev", 0, 2), pt("evp", "evin[1]", 0.2), ins("ev", 1, 3, 0.3), pt("evp", "evin[2]", 0.5), ins("ev", 2, 4, 0.6)])
s.step("Times: pop 4, pop 3, push 3 times 4, 12.", [pt("evp", "evin[3]"), rm("ev[2]", 0.2), st("ev[1]", 12, 0.5)])
s.step("Plus: pop 12 and 2, push 14.", [pt("evp", "evin[4]"), rm("ev[1]", 0.2), st("ev[0]", 14, 0.5)])
s.step("5 is pushed. Minus: pop 5, then 14. The first popped is the right operand: 14 minus 5, 9.", [pt("evp", "evin[5]"), ins("ev", 1, 5, 0.1), pt("evp", "evin[6]", 0.4), rm("ev[1]", 0.6), st("ev[0]", 9, 0.8)])
s.step("One number left: the answer, 9. Check it in infix: 2 plus 3 times 4, minus 5, is 9. Each symbol costs Theta of 1, so evaluation is Theta of n.", [mk("ev[0]"), s.take("pop right operand first, then left")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("evin", "ev", "evp") + show("q") + [hl("q[0]")])
s.step("Convert an infix expression with a power, evaluate a postfix expression, and trace a sequence of pushes and pops. Pause and work it out.", [hl("q[1..=2]")])
s.step("a: A plus B in brackets becomes A B plus. C minus D becomes C D minus. Times comes next, since the stack pops it when divide arrives.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("Then E, and power is pushed above divide, because it has higher precedence. F, then pop power and divide. A B plus C D minus times E F power divide.", [hl("qa[1]"), mk("qa[0][2]", 0.5)])
s.step("b: 8, 2, 3, power: 2 cubed is 8. Divide: 8 over 8 is 1. Then 2 times 3 is 6, and 1 plus 6 is 7.", [hl("qa[2]")])
s.step("Then 5 times 1 is 5, and 7 minus 5 is 2.", [hl("qa[3]"), mk("qa[3][2]", 0.4)])
s.step("c: the stack is 1, 2, 3; pop gives 3; push 4; pop gives 4; pop gives 2. Popped 3, 4, 2, and 1 is left.", [hl("qa[4]")])
s.step("The usual slip: in evaluation, computing second-popped minus first-popped the wrong way round. 14 minus 5, not 5 minus 14.", [s.take("left operand = second popped")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("A stack is last in, first out, with Theta of 1 push and pop, in an array with a top index or as a linked list. It checks brackets by matching each closer with the top.", [hl("stages[0..=3]")])
s.step("Infix converts to postfix with an operator stack and precedence rules, and postfix is evaluated with a stack of numbers in one pass.", [hl("stages[4..=6]")])
s.step("Next video: the opposite discipline. First in, first out: queues.", [mk("stages[0..=7]"), s.take("Next: queues")])

s.save("/home/claude/playlist/dsa1/d1v7.json")
