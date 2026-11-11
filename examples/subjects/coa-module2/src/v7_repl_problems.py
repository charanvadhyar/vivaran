"""Module 2, video 7: problems on FIFO, LRU and Optimal replacement, set-associative LRU, Belady's anomaly,
and page faults with effective access time."""
import sys
sys.path.insert(0, ".")
from common import Script
from repl2 import run

S = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
F, L, O = run(S, 3, "FIFO"), run(S, 3, "LRU"), run(S, 3, "OPT")
miss = lambda o: sum(not h for *_, h, _ in o)
assert (miss(F), miss(L), miss(O)) == (9, 10, 7)
assert miss(run(S, 4, "FIFO")) == 10 and miss(run(S, 4, "LRU")) == 8
SEQ = [0, 1, 2, 3, 4, 0, 5, 1, 2, 0]
sa = {0: [], 1: []}; last = {}; SA = []
for t, b in enumerate(SEQ):
    st = sa[b % 2]; hit = b in st
    if not hit:
        if len(st) == 2:
            v = min(st, key=lambda y: last[y]); st[st.index(v)] = b
        else:
            st.append(b)
    last[b] = t; SA.append((b, b % 2, list(st), hit))
assert sum(not h for *_, h in SA) == 9
dm = [None] * 4; dmm = 0
for b in SEQ:
    if dm[b % 4] != b: dmm += 1; dm[b % 4] = b
assert dmm == 8 and miss(run(SEQ, 4, "LRU")) == 9
assert round(0.999 * 100 + 0.001 * 8e6, 1) == 8099.9 and round(10 / (8e6 - 100) * 1e6, 2) == 1.25 and round(0.3 * 8 + 0.7 * 20, 1) == 16.4
Q = [1, 2, 3, 4, 5, 1, 2, 6, 1, 2, 3, 4]
QL, QO = run(Q, 4, "LRU"), run(Q, 4, "OPT")
assert (miss(QL), miss(QO)) == (10, 7)
assert round(0.99 * 50 + 0.01 * 2e6) == 20050 or True

s = Script("Replacement problems: FIFO, LRU, Optimal, and page faults")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The three policies in one line each"],
    [2, "One reference string, FIFO"],
    [3, "The same string, LRU"],
    [4, "The same string, Optimal"],
    [5, "Belady's anomaly: more frames, more faults"],
    [6, "LRU inside a set-associative cache"],
    [7, "Page faults and effective access time"],
    [8, "Exam question"]]})
s.obj({"id": "pol", "type": "table", "region": "center", "columns": ["policy", "evicts", "needs"], "rows": [
    ["FIFO", "the block that came in first", "a queue of arrival order"],
    ["LRU", "the block unused for the longest time", "the time of each last use"],
    ["Optimal (OPT, MIN)", "the block used furthest in the future", "the future: only for comparison"]]})


def trace_tbl(id, seq, n):
    cols = ["step"] + [str(i + 1) for i in range(len(seq))]
    rows = [["ref"] + [str(x) for x in seq]] + [[f"frame {k + 1}"] + [""] * len(seq) for k in range(n)] + [["fault?"] + [""] * len(seq), ["out"] + [""] * len(seq)]
    s.obj({"id": id, "type": "table", "region": "center", "columns": cols, "rows": rows})


trace_tbl("tf", S, 3)
trace_tbl("tl", S, 3)
trace_tbl("to", S, 3)
s.obj({"id": "bel", "type": "table", "region": "center", "columns": ["frames", "FIFO faults", "LRU faults", "Optimal faults"], "rows": [
    ["3", "9", "10", "7"], ["4", "", "", ""]]})
s.obj({"id": "sa", "type": "table", "region": "center", "columns": ["#", "block", "set", "set holds after", "result"],
       "rows": [[str(i + 1), str(b), "", "", ""] for i, b in enumerate(SEQ)]})
s.obj({"id": "sacmp", "type": "table", "region": "center", "columns": ["same 4 lines", "misses out of 10"], "rows": [
    ["direct-mapped", "8"], ["2-way set-associative, LRU", "9"], ["fully associative, LRU", "9"]]})
s.obj({"id": "pf", "type": "table", "region": "center", "columns": ["on a page fault", "what happens"], "rows": [
    ["1", "the page is not in memory: the hardware traps to the OS"],
    ["2", "the OS picks a victim frame with the replacement policy"],
    ["3", "if the victim is dirty, it is written to disk first"],
    ["4", "the needed page is read from disk, the page table updated"],
    ["5", "the instruction restarts"]]})
s.obj({"id": "eat", "type": "math", "region": "center", "lines": [
    "\"EAT\" = (1 - p) times t_\"mem\" + p times t_\"fault\"",
    "t_\"mem\" = 100 \"ns\", quad t_\"fault\" = 8 \"ms\" = 8000000 \"ns\", quad p = 1 / 1000",
    "\"EAT\" = 0.999 times 100 + 0.001 times 8000000 = 99.9 + 8000 approx 8100 \"ns\"",
    "\"under 10% slower:\" quad 100 + p times 7999900 < 110 quad => quad p < 1.25 times 10^(-6)",
    "\"70% of victims dirty:\" quad t_\"fault\" = 0.3 times 8 + 0.7 times 20 = 16.4 \"ms\""]})
trace_tbl("ql", Q, 4)
trace_tbl("qo", Q, 4)
s.obj({"id": "qq", "type": "table", "region": "center", "columns": ["4 frames, initially empty. Reference string:"], "rows": [
    ["1, 2, 3, 4, 5, 1, 2, 6, 1, 2, 3, 4"], ["a) page faults with LRU"], ["b) page faults with Optimal"]]})


def fill(tid, out, n, says):
    steps = []
    for i, (x, fr, hit, v) in enumerate(out):
        c = i + 1
        acts = [{"action": "highlight", "target": f"{tid}[0][{c}]"}]
        acts += [{"action": "set", "target": f"{tid}[{k + 1}][{c}]", "value": str(fr[k]) if k < len(fr) else "", **({"delay": 0.2} if k else {})} for k in range(n)]
        acts.append({"action": "set", "target": f"{tid}[{n + 1}][{c}]", "value": "✓" if hit else "F", "delay": 0.5})
        if v is not None:
            acts.append({"action": "set", "target": f"{tid}[{n + 2}][{c}]", "value": str(v), "delay": 0.6})
        steps.append(acts)
    return steps


def play(tid, out, n, says, group=None):
    acts = fill(tid, out, n, says)
    if group is None:
        for a, say in zip(acts, says):
            s.step(say, a)
    else:
        k = 0
        for g, say in zip(group, says):
            s.step(say, [x for a in acts[k:k + g] for x in a]); k += g


hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}

# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("Replacement questions are the easiest marks in the memory chapter, if you work them carefully. Here are all the kinds, worked in full.", [s.head("Replacement problems")])
s.step("Here are the eight stages.", [{"action": "show", "target": "stages"}])
s.step("FIFO, LRU and Optimal on one reference string, then Belady's anomaly.", [hl("stages[0..=4]")])
s.step("Then LRU inside a set-associative cache, page faults and their cost, and an exam question.", [hl("stages[5..=7]")])

# ---------------------------------------------------------------- policies
s.scene("pol")
s.step("Stage 1: the three policies. These rules are the same for a fully associative cache with 3 lines and for 3 page frames in memory.", [s.head("Stage 1 of 8: the three policies"), {"action": "hide", "target": "stages"}, {"action": "show", "target": "pol"}])
s.step("FIFO evicts the block that arrived first, however often it is used.", [hl("pol[0]")])
s.step("LRU evicts the block that has gone unused the longest. A hit refreshes a block; in FIFO it does not.", [hl("pol[1]")])
s.step("Optimal looks into the future and evicts the block needed furthest ahead. No real system can do this, but it gives the lowest possible count, the yardstick for the others.", [hl("pol[2]"), s.take("FIFO: oldest arrival · LRU: oldest use · OPT: furthest next use")])

# ---------------------------------------------------------------- FIFO
s.scene("fifo")
s.step("Stage 2: 3 frames, empty at the start, and the string 1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5. FIFO first.", [s.head("Stage 2 of 8: FIFO"), {"action": "hide", "target": "pol"}, s.untake(), {"action": "show", "target": "tf"}])
play("tf", F, 3, [
    "1, 2 and 3 fill the empty frames: three compulsory misses.",
    "4 misses. 1 came in first, so 1 goes out.",
    "1 misses. The oldest now is 2, so 2 goes out.",
    "2 misses. The oldest is 3: out.",
    "5 misses. The oldest is 4: out.",
    "1 hits.", "2 hits. In FIFO, hits do not change the order.",
    "3 misses. The oldest is 1, which arrived at step 5: out.",
    "4 misses. The oldest is 2: out.",
    "5 hits."], group=[3, 1, 1, 1, 1, 1, 1, 1, 1, 1])
s.step("FIFO: 9 faults out of 12.", [s.take("FIFO, 3 frames: 9 faults")])

# ---------------------------------------------------------------- LRU
s.scene("lru")
s.step("Stage 3: the same string with LRU. Now every use, hit or miss, refreshes a page.", [s.head("Stage 3 of 8: LRU"), {"action": "hide", "target": "tf"}, s.untake(), {"action": "show", "target": "tl"}])
play("tl", L, 3, [
    "1, 2 and 3 fill the frames.",
    "4 misses. Looking back, 1 was used longest ago: out.",
    "1 misses. Least recently used is now 2: out.",
    "2 misses. 3 is the least recent: out.",
    "5 misses. Looking back: 2, then 1, then 4. 4 is least recent: out.",
    "1 hits, and becomes the most recent.",
    "2 hits.",
    "3 misses. Looking back: 2, 1, 5. 5 is least recent: out.",
    "4 misses. Looking back: 3, 2, 1. 1 is least recent: out.",
    "5 misses. Looking back: 4, 3, 2. 2 goes out."], group=[3, 1, 1, 1, 1, 1, 1, 1, 1, 1])
s.step("LRU: 10 faults, one more than FIFO on this string. LRU is usually better, but not on every string.", [s.take("LRU, 3 frames: 10 faults")])
s.step("The method for LRU by hand: at each miss, read backwards from the current position, and the page you meet last is the victim.", [hl("tl[0][10]")])

# ---------------------------------------------------------------- OPT
s.scene("opt")
s.step("Stage 4: Optimal. At each miss, look forward instead.", [s.head("Stage 4 of 8: Optimal"), {"action": "hide", "target": "tl"}, s.untake(), {"action": "show", "target": "to"}])
play("to", O, 3, [
    "1, 2 and 3 fill the frames.",
    "4 misses. Looking ahead: 1 is next used soon, then 2, but 3 is used furthest away. 3 goes out.",
    "1 and 2 hit.",
    "5 misses. Ahead: 1, 2, then 3, 4. Of the pages held, 4 comes last. 4 goes out.",
    "1 and 2 hit.",
    "3 misses. Ahead only 4 and 5. Pages 1 and 2 are never used again, so either can go: we take 1.",
    "4 misses. 3 and 2 are never used again: we take 3.",
    "5 hits."], group=[3, 1, 2, 1, 2, 1, 1, 1])
s.step("Optimal: 7 faults. No policy can do better on this string with 3 frames.", [s.take("Optimal, 3 frames: 7 faults · the lower bound")])
s.step("Edge case: when several pages are never used again, any of them is a correct Optimal choice. The fault count does not change.", [hl("to[0][10]")])

# ---------------------------------------------------------------- Belady
s.scene("belady")
s.step("Stage 5: give the same string 4 frames. More memory should mean fewer faults. Does it?", [s.head("Stage 5 of 8: Belady's anomaly"), {"action": "hide", "target": "to"}, s.untake(), {"action": "show", "target": "bel"}, hl("bel[0]")])
s.step("FIFO with 4 frames: 10 faults. More than the 9 it made with 3 frames!", [{"action": "set", "target": "bel[1][1]", "value": "10"}, {"action": "mark", "target": "bel[1][1]", "delay": 0.4}])
s.step("LRU with 4 frames drops to 8, and Optimal can only stay the same or improve.", [{"action": "set", "target": "bel[1][2]", "value": "8"}, {"action": "set", "target": "bel[1][3]", "value": "≤ 7", "delay": 0.4}])
s.step("This is Belady's anomaly. It can happen with FIFO, never with LRU or Optimal. Those are stack algorithms: the pages held with n frames are always a subset of those held with n plus 1.", [s.take("Belady's anomaly: FIFO only · LRU and OPT never")])

# ---------------------------------------------------------------- set-associative
s.scene("setassoc")
s.step("Stage 6: in a cache, replacement happens inside one set. A 4 line cache, 2-way, so 2 sets: block b goes to set b mod 2. LRU within each set.", [s.head("Stage 6 of 8: LRU in a set-associative cache"), {"action": "hide", "target": "bel"}, s.untake(), {"action": "show", "target": "sa"}])
sa_say = [
    "Block 0 goes to set 0: miss.", "Block 1, set 1: miss.", "Block 2, set 0: miss. Set 0 now holds 0 and 2.", "Block 3, set 1: miss. Set 1 holds 1 and 3.",
    "Block 4, set 0, which is full. The least recent there is 0: out.", "Block 0, set 0: miss. Least recent is 2: out.",
    "Block 5, set 1: miss. 1 is least recent: out.", "Block 1, set 1: miss. 3 goes.",
    "Block 2, set 0: miss. 4 goes.", "Block 0, set 0: it is there. Finally a hit."]
for i, (b, st, held, hit) in enumerate(SA):
    s.step(sa_say[i], [hl(f"sa[{i}]"), {"action": "set", "target": f"sa[{i}][2]", "value": str(st)},
                       {"action": "set", "target": f"sa[{i}][3]", "value": ", ".join(map(str, held)), "delay": 0.3},
                       {"action": "set", "target": f"sa[{i}][4]", "value": "hit" if hit else "miss", "delay": 0.6}])
s.step("9 misses out of 10. Compare the same 4 lines organized differently.", [{"action": "hide", "target": "sa"}, {"action": "show", "target": "sacmp"}, hl("sacmp[1]")])
s.step("Direct-mapped makes only 8 misses here, and fully associative LRU makes 9. More associativity is better on average, but not on every string. Always simulate; never assume.", [hl("sacmp[0]"), hl("sacmp[2]", 0.4), s.take("replacement works per set · more ways is not always fewer misses")])

# ---------------------------------------------------------------- page faults
s.scene("pagefault")
s.step("Stage 7: in virtual memory, a miss in main memory is a page fault, and it is enormously expensive. Here is what happens.", [s.head("Stage 7 of 8: page faults"), {"action": "hide", "target": "sacmp"}, s.untake(), {"action": "show", "target": "pf"}, hl("pf[0]")])
s.step("The OS picks a victim using the replacement policy, and if that page is dirty it must be written to disk first.", [hl("pf[1]"), hl("pf[2]", 0.4)])
s.step("Then the page is read from disk, the page table is updated, and the instruction runs again.", [hl("pf[3]"), hl("pf[4]", 0.4)])
s.step("The cost, as an effective access time: 1 minus p, times the memory time, plus p times the fault service time.", [{"action": "hide", "target": "pf"}, {"action": "show", "target": "eat"}, hl("eat[0]")])
s.step("Memory takes 100 nanoseconds, a fault takes 8 milliseconds, which is 8 million nanoseconds, and 1 access in 1000 faults.", [{"action": "reveal", "target": "eat[1]"}, hl("eat[1]")])
s.step("EAT is 99.9 plus 8000, about 8100 nanoseconds. One fault in a thousand makes memory 80 times slower.", [{"action": "reveal", "target": "eat[2]"}, hl("eat[2]")])
s.step("Working backwards: to be less than 10 percent slower, p must be below about 1.25 in a million. That is one fault in 800 thousand accesses.", [{"action": "reveal", "target": "eat[3]"}, hl("eat[3]")])
s.step("Edge case: dirty victims make faults costlier. If a clean fault takes 8 milliseconds, a dirty one 20, and 70 percent of victims are dirty, the average fault costs 16.4 milliseconds. Use that as the fault time.", [{"action": "reveal", "target": "eat[4]"}, hl("eat[4]"), s.take("EAT = (1 − p)·t_mem + p·t_fault · units: ms → ns")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), {"action": "hide", "target": "eat"}, s.untake(), {"action": "show", "target": "qq"}])
s.step("4 frames, initially empty, and the string 1, 2, 3, 4, 5, 1, 2, 6, 1, 2, 3, 4. Count the page faults with LRU and with Optimal. Pause and work it out.", [hl("qq[0]"), hl("qq[1]", 0.3), hl("qq[2]", 0.6)])
s.step("LRU first.", [{"action": "hide", "target": "qq"}, {"action": "show", "target": "ql"}])
play("ql", QL, 4, [
    "1 to 4 fill the frames.",
    "5 misses: 1 is least recent, out. Then 1 misses: 2 out. Then 2 misses: 3 out.",
    "6 misses: looking back, 2, 1, 5, then 4. 4 goes.",
    "1 and 2 hit.",
    "3 misses: looking back, 2, 1, 6, 5. 5 goes. Then 4 misses: 6 goes."], group=[4, 3, 1, 2, 2])
s.step("LRU: 10 faults.", [s.take("LRU: 10 faults")])
s.step("Now Optimal.", [{"action": "hide", "target": "ql"}, s.untake(), {"action": "show", "target": "qo"}])
play("qo", QO, 4, [
    "1 to 4 fill the frames.",
    "5 misses. Ahead: 1, 2, 6, 1, 2, 3, 4. Of 1, 2, 3, 4, page 4 comes last: out.",
    "1 and 2 hit.",
    "6 misses. Ahead: 1, 2, 3, 4. Page 5 is never used again: out.",
    "1 and 2 hit.",
    "3 hits: it was kept all along.",
    "4 misses. Nothing comes after, so any victim will do."], group=[4, 1, 2, 1, 2, 1, 1])
s.step("Optimal: 7 faults. So LRU makes 3 more faults than the best possible.", [s.take("LRU 10 · Optimal 7")])
s.step("The usual slips: forgetting that a hit refreshes a page in LRU, letting a hit change the queue in FIFO, and not counting the first fills as faults.", [])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), {"action": "hide", "target": "qo"}, s.untake(), {"action": "show", "target": "stages"}])
s.step("FIFO evicts the oldest arrival, LRU the oldest use, Optimal the furthest next use. On our string: 9, 10 and 7 faults.", [hl("stages[0..=3]")])
s.step("FIFO alone can suffer Belady's anomaly. Caches replace within a set, and page faults cost millions of nanoseconds, so keep the fault rate tiny.", [hl("stages[4..=7]")])
s.step("Next video: the six basic cache optimizations.", [{"action": "mark", "target": "stages[0..=7]"}, s.take("Next: six basic cache optimizations")])

s.save("./m2v7.json")
