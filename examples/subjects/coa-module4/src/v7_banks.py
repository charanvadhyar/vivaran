"""Module 4, video 7: memory banks and stride."""
import sys
sys.path.insert(0, "/home/claude/playlist")
sys.path.insert(0, "/home/claude/playlist/m4")
from common import Script
from banks import load_time, visited

assert load_time(64, 1, 8, 6, 12) == 76 and load_time(64, 32, 8, 6, 12) == 391
assert round(76 / 64, 2) == 1.19 and round(391 / 64, 2) == 6.11 and 12 + 1 + 6 * 63 == 391
TB = [(s, visited(s, 8), load_time(64, s, 8, 6, 12)) for s in (1, 2, 3, 4, 8)]
assert TB == [(1, 8, 76), (2, 4, 106), (3, 8, 76), (4, 2, 200), (8, 1, 391)]
assert visited(100, 8) == 2 and load_time(64, 100, 8, 6, 12) == 200
assert visited(101, 8) == 8 and load_time(64, 101, 8, 6, 12) == 76
assert visited(32, 7) == 7 and load_time(64, 32, 7, 6, 12) == 76
assert round(15 / 2.167, 2) == 6.92 and 32 * 6 * 7 == 1344
QT = [(s, visited(s, 16), load_time(64, s, 16, 8, 10)) for s in (1, 3, 4, 16)]
assert QT == [(1, 16, 74), (3, 16, 74), (4, 4, 134), (16, 1, 515)]

s = Script("Memory banks and stride")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Why memory is the hard part"],
    [2, "Memory banks"],
    [3, "How many banks"],
    [4, "Strided access"],
    [5, "Bank conflicts"],
    [6, "Which strides conflict"],
    [7, "Avoiding conflicts"],
    [8, "Exam question"]]})
s.obj({"id": "why", "type": "table", "region": "center", "columns": ["the demand", "the problem"], "rows": [
    ["a vector load wants one word per cycle", "a DRAM or SRAM bank takes several cycles per access"],
    ["several loads and stores at once", "several words per cycle"],
    ["non-sequential patterns", "columns of matrices, scattered indices"],
    ["so", "spread memory over many banks that work in parallel"]]})
s.obj({"id": "bk", "type": "table", "region": "center", "columns": ["word address", "0", "1", "2", "3", "4", "5", "6", "7"], "rows": [
    ["bank", "0", "1", "2", "3", "4", "5", "6", "7"],
    ["word address", "8", "9", "10", "11", "12", "13", "14", "15"],
    ["bank", "0", "1", "2", "3", "4", "5", "6", "7"]]})
s.obj({"id": "bkx", "type": "table", "region": "center", "columns": ["each bank", "meaning"], "rows": [
    ["independent", "its own address and data lines: banks work at the same time"],
    ["bank busy time", "after an access, the bank cannot start another for some cycles"],
    ["sequential words", "fall in different banks, so a new access can start every cycle"]]})
s.obj({"id": "cray", "type": "math", "region": "center", "lines": [
    "\"Cray T90 (textbook): 32 processors, each 4 loads + 2 stores per cycle\"",
    "\"clock\" 2.167 \"ns, SRAM busy\" 15 \"ns:\" quad 15 / 2.167 approx 6.92 -> 7 \"cycles\"",
    "\"accesses per cycle\" = 32 times 6 = 192 quad \"banks\" >= 192 times 7 = 1344"]})
s.obj({"id": "mat", "type": "code", "region": "center", "language": "c", "lines": [
    "double A[100][100];         // stored by rows: A[i][j] at word 100*i + j",
    "for (i = 0; i < 100; i++)",
    "    sum[j] += A[i][j];      // walks down column j",
    "",
    "// consecutive elements are 100 words apart: stride 100 (800 bytes)",
    "LVWS  V1,(R1,R2)            ; R2 holds the stride"]})
s.obj({"id": "cf", "type": "table", "region": "center", "columns": ["8 banks, busy 6 cycles, latency 12", "stride 1", "stride 32"], "rows": [
    ["banks used", "all 8, in turn", "32 mod 8 = 0: always bank 0"],
    ["a bank is revisited after", "8 cycles > 6: no wait", "every access: waits 6 cycles"],
    ["time for 64 elements", "12 + 64 = 76", "12 + 1 + 6 × 63 = 391"],
    ["cycles per element", "1.19", "6.11"]]})
s.obj({"id": "tb", "type": "table", "region": "center", "columns": ["stride", "banks visited = 8 / gcd(stride, 8)", "revisit gap", "cycles for 64"], "rows": [
    [str(st), str(v), f"{v} cycle{'s' if v > 1 else ''}" + (" < 6: stalls" if v < 6 else " ≥ 6: none"), str(t)] for st, v, t in TB]})
s.obj({"id": "fix", "type": "table", "region": "center", "columns": ["fix", "example", "result"], "rows": [
    ["pad the array", "A[100][101]: stride 101, gcd(101, 8) = 1", "8 banks: 76 cycles instead of 200"],
    ["a prime number of banks", "7 banks: stride 32 visits all 7", "76 cycles instead of 391"],
    ["more banks than busy time", "visited ≥ busy time", "never wait"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["16 banks, bank busy 8 cycles, latency 10, 64 elements"], "rows": [
    ["a) for strides 1, 3, 4 and 16: banks visited, and does it stall?"],
    ["b) the cycles for each"],
    ["c) a 64 × 64 matrix of doubles stored by rows: the stride of a column, and a fix"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["stride", "banks visited", "stall?", "cycles"], "rows": [
    [str(st), str(v), "no: gap ≥ 8" if v >= 8 else "yes: gap < 8", str(t)] for st, v, t in QT]})
s.obj({"id": "qb", "type": "math", "region": "center", "lines": [
    "\"stride 1:\" quad 10 + 64 = 74 quad \"stride 16:\" quad 10 + 1 + 8 times 63 = 515",
    "\"c) column stride\" = 64 \"words · gcd(64, 16) = 16: one bank\" quad \"pad to 65 columns\""]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
ml = lambda t, a, b: {"action": "mark_lines", "target": t, "from": a, "to": b}
rv = lambda t: {"action": "reveal", "target": t}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

s.scene("intro")
s.step("A vector unit can finish one element per cycle, but only if memory delivers one element per cycle. This video is about how memory keeps up, and how the wrong access pattern can make it slower by a factor of five.", [s.head("Memory banks and stride")])
s.step("Here are the eight stages.", show("stages"))
s.step("Why memory is the hard part, memory banks, how many are needed, and strided access.", [hl("stages[0..=3]")])
s.step("Then bank conflicts, which strides cause them, how to avoid them, and an exam question.", [hl("stages[4..=7]")])

s.scene("why")
s.step("Stage 1: a vector load wants a new word every cycle. But a memory chip, once accessed, needs several cycles before it can be accessed again.", [s.head("Stage 1 of 8: why memory is hard")] + hide("stages") + show("why") + [hl("why[0]")])
s.step("And a vector machine runs several loads and stores at once, so it wants several words per cycle.", [hl("why[1]")])
s.step("Not always in order, either: columns of matrices, or scattered indices.", [hl("why[2]")])
s.step("The answer, used by every vector machine: split memory into many banks that can work at the same time.", [hl("why[3]"), s.take("one word per cycle needs many banks")])

s.scene("banks")
s.step("Stage 2: with 8 banks, word 0 goes in bank 0, word 1 in bank 1, up to word 7 in bank 7. Then word 8 goes back to bank 0.", [s.head("Stage 2 of 8: memory banks"), s.untake()] + hide("why") + show("bk") + [hl("bk[0]")])
s.step("So the bank is the word address mod 8. This is called interleaving.", [hl("bk[0..=2]")])
s.step("Each bank is independent, with its own address and data lines.", hide("bk") + show("bkx") + [hl("bkx[0]")])
s.step("After an access, a bank stays busy for some cycles: the bank busy time.", [hl("bkx[1]")])
s.step("But consecutive words fall in different banks. So while bank 0 is still busy, the next access goes to bank 1, then bank 2. One access can start every cycle.", [hl("bkx[2]"), s.take("bank = address mod number of banks")])

s.scene("cray")
s.step("Stage 3: how many banks are needed? The textbook's example is the Cray T90: 32 processors, each able to issue 4 loads and 2 stores every cycle.", [s.head("Stage 3 of 8: how many banks"), s.untake()] + hide("bkx") + show("cray") + [hl("cray[0]")])
s.step("The clock is 2.167 nanoseconds, and an SRAM bank is busy for 15 nanoseconds. 15 over 2.167 is 6.92: a bank is busy for 7 cycles, rounding up.", [rv("cray[1]"), hl("cray[1]")])
s.step("32 processors times 6 accesses is 192 accesses per cycle. Each holds its bank for 7 cycles, so at least 192 times 7: 1344 banks.", [rv("cray[2]"), hl("cray[2]"), s.take("banks ≥ accesses per cycle × busy cycles")])

s.scene("stride")
s.step("Stage 4: not every vector is consecutive in memory. C stores a matrix row by row: A of i, j is at word 100 i plus j.", [s.head("Stage 4 of 8: strided access"), s.untake()] + hide("cray") + show("mat") + [ml("mat", 1, 1)])
s.step("A loop down a column touches A of 0, j, then A of 1, j: 100 words apart.", [ml("mat", 2, 3)])
s.step("The distance between consecutive elements is the stride. Here 100 words, or 800 bytes.", [ml("mat", 5, 5)])
s.step("VMIPS loads it with LVWS, load vector with stride, which takes the stride in a register. Matrix multiplication needs both rows and columns, so strided loads are everywhere.", [ml("mat", 6, 6), s.take("stride: the distance between consecutive elements")])

s.scene("conflict")
s.step("Stage 5: strides can cause bank conflicts. The textbook's example: 8 banks, a bank busy time of 6 cycles, and 12 cycles of memory latency. Load 64 elements with stride 1, and with stride 32.", [s.head("Stage 5 of 8: bank conflicts"), s.untake()] + hide("mat") + show("cf") + [hl("cf[0]")])
s.step("Stride 1 visits the banks in turn and returns to a bank after 8 cycles, longer than its busy time of 6. No waiting.", [hl("cf[1][1]")])
s.step("Stride 32: 32 mod 8 is 0, so every element is in bank 0. Each access waits 6 cycles for the one before.", [hl("cf[1][2]")])
s.step("Stride 1 takes 12 plus 64, 76 cycles. Stride 32 takes 12, plus 1, plus 6 times 63: 391 cycles.", [hl("cf[2]")])
s.step("1.19 against 6.11 cycles per element: five times slower, for the same amount of data.", [hl("cf[3]"), s.take("same bank again too soon: a conflict")])

s.scene("which")
s.step("Stage 6: which strides conflict? A stride s visits only 8 over the gcd of s and 8 banks before it comes back to the first one.", [s.head("Stage 6 of 8: which strides conflict"), s.untake()] + hide("cf") + show("tb") + [hl("tb[0]")])
s.step("Stride 1 and stride 3 have gcd 1 with 8: all 8 banks, a gap of 8 cycles, no stalls. 76 cycles.", [hl("tb[0]"), hl("tb[2]", 0.4)])
s.step("Stride 2 visits 4 banks, so it returns after 4 cycles, too soon: 106 cycles.", [hl("tb[1]")])
s.step("Stride 4 visits only 2 banks: 200 cycles. Stride 8 visits one: 391.", [hl("tb[3..=4]")])
s.step("The rule: a conflict happens when the number of banks visited is smaller than the bank busy time. Odd strides are safe with a power-of-two number of banks.", [mk("tb[2]"), s.take("conflict if 8 / gcd(s, 8) < busy time")])

s.scene("fix")
s.step("Stage 7: how to avoid conflicts. Pad the array. Our 100-column matrix has stride 100: gcd with 8 is 4, only 2 banks, 200 cycles. Declare it with 101 columns: gcd 1, all 8 banks, 76 cycles.", [s.head("Stage 7 of 8: avoiding conflicts"), s.untake()] + hide("tb") + show("fix") + [hl("fix[0]")])
s.step("Or use a prime number of banks. With 7 banks, stride 32 visits all 7, and the load takes 76 cycles instead of 391. Only strides that are multiples of 7 now conflict.", [hl("fix[1]")])
s.step("Or simply have many more banks than the busy time, as the Cray did. Then most strides never wait.", [hl("fix[2]"), s.take("pad arrays · prime banks · many banks")])

s.scene("exam")
s.step("Now an exam question: 16 banks, a bank busy time of 8 cycles, a latency of 10, and 64 elements.", [s.head("Exam question"), s.untake()] + hide("fix") + show("q") + [hl("q[0]")])
s.step("For strides 1, 3, 4 and 16, find the banks visited, whether it stalls, and the cycles. And the stride of a column in a 64 by 64 matrix of doubles, with a fix. Pause and work it out.", [hl("q[1..=2]")])
s.step("Strides 1 and 3: gcd 1 with 16, so all 16 banks, a gap of 16 cycles, never waiting. 10 plus 64: 74 cycles.", hide("q") + show("qa") + [hl("qa[0..=1]")])
s.step("Stride 4: 16 over 4 is 4 banks. A gap of 4 is less than 8: it stalls. 134 cycles.", [hl("qa[2]")])
s.step("Stride 16: always the same bank. 10, plus 1, plus 8 times 63: 515 cycles.", [hl("qa[3]")])
s.step("The formulas, for the two easy cases.", hide("qa") + show("qb") + [hl("qb[0]")])
s.step("c: a column of a 64 by 64 matrix has stride 64. gcd of 64 and 16 is 16: one bank, the worst case. Pad the rows to 65 columns, and the stride becomes 65, which is odd.", [rv("qb[1]"), hl("qb[1]")])
s.step("The usual slip: thinking that a large stride is always bad. Stride 101 is perfect with 8 banks; stride 8 is the worst. It is the gcd that matters.", [s.take("look at gcd(stride, banks), not the stride's size")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qb") + show("stages"))
s.step("Vector machines need a word per cycle, so memory is interleaved across banks, at least the accesses per cycle times the busy time.", [hl("stages[0..=3]")])
s.step("A stride s visits banks over gcd of s and banks banks. If that is less than the busy time, accesses wait. Padding or a prime number of banks fixes it.", [hl("stages[4..=6]")])
s.step("Next video: the hardest pattern of all, indexed access. Gather, scatter, and sparse matrices.", [mk("stages[0..=7]"), s.take("Next: gather-scatter")])

s.save("/home/claude/playlist/m4/m4v7.json")
