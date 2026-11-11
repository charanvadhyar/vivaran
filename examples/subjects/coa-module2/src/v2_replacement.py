"""Video 2: replacement policies. LRU, FIFO, random, and the trap where FIFO beats LRU."""
import json, sys
sys.path.insert(0, "/home/claude/playlist")
from common import Script

S1, S2 = "ABCBADABA", "ABACDBACD"


def trace(seq, policy, k=3):
    """Per reference: result, evicted, ways (by position), order (LRU: least recent first; FIFO: oldest first)."""
    ways, order, rows = [None] * k, [], []
    for r in seq:
        if r in ways:
            if policy == "LRU":
                order.remove(r); order.append(r)
            rows.append(dict(ref=r, res="hit", ev=None, ways=list(ways), order=list(order)))
            continue
        if None in ways:
            i, ev = ways.index(None), None
        else:
            ev = order.pop(0); i = ways.index(ev)
        ways[i] = r; order.append(r)
        rows.append(dict(ref=r, res="miss", ev=ev, ways=list(ways), order=list(order), way=i))
    return rows


def ways_s(w):
    return " ".join(x or "–" for x in w)


L1, F1, L2, F2 = trace(S1, "LRU"), trace(S1, "FIFO"), trace(S2, "LRU"), trace(S2, "FIFO")
hits = lambda rows: sum(r["res"] == "hit" for r in rows)
assert (hits(L1), hits(F1), hits(L2), hits(F2)) == (5, 3, 1, 4)

s = Script("Replacement: LRU, FIFO and random, and when FIFO wins")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "When does the cache have to choose a victim?"],
    [2, "The LRU rule: least recently used"],
    [3, "The FIFO rule: first in, first out"],
    [4, "Reference string 1, traced with both"],
    [5, "The trap: reference string 2, where FIFO wins"],
    [6, "Random, and what each policy costs in hardware"]]})
s.obj({"id": "when", "type": "table", "region": "center", "columns": ["mapping", "on a miss, the new block can go", "choice?"], "rows": [
    ["direct-mapped", "exactly one line", "none: that line is replaced"],
    ["set-associative", "any way of its set", "yes, when every way is full"],
    ["fully associative", "any line", "yes, when the cache is full"]]})
s.obj({"id": "rules", "type": "table", "region": "center", "columns": ["policy", "evicts", "keeps", "updated on"], "rows": [
    ["LRU", "the block unused for the longest time", "an order, least recent first", "every access, hit or miss"],
    ["FIFO", "the block that arrived first", "a queue, oldest first", "misses only"],
    ["Random", "any block, chosen at random", "nothing per set", "misses only"]]})


def table(id, seq):
    return {"id": id, "type": "table", "region": "center",
            "columns": ["#", "ref", "LRU ways", "LRU order", "LRU", "FIFO ways", "FIFO queue", "FIFO"],
            "rows": [[i + 1, r, "", "", "", "", "", ""] for i, r in enumerate(seq)]}


s.obj(table("t1", S1))
s.obj(table("t2", S2))
s.obj({"id": "score", "type": "table", "region": "center", "columns": ["reference string", "LRU hits", "FIFO hits", "winner"], "rows": [
    ["1: A B C B A D B A B" if False else "1: " + " ".join(S1), "5 of 9", "3 of 9", "LRU"],
    ["2: " + " ".join(S2), "1 of 9", "4 of 9", "FIFO"]]})
s.obj({"id": "cost", "type": "table", "region": "center", "columns": ["policy", "state per set", "work on a hit", "miss rate in practice"], "rows": [
    ["LRU", "full order of the ways", "update the order", "usually lowest"],
    ["pseudo-LRU", "a few bits (a tree)", "flip a few bits", "close to LRU"],
    ["FIFO", "one pointer to the oldest way", "nothing", "a little higher"],
    ["Random", "nothing (one shared generator)", "nothing", "close to LRU in large caches"]]})


def lru_say(r, prev_order):
    if r["res"] == "hit":
        return f"LRU: {r['ref']} is there, a hit, and {r['ref']} moves to the most recent end."
    if r["ev"] is None:
        return f"LRU: {r['ref']} misses, and an empty way takes it."
    return f"LRU: {r['ref']} misses; the least recent is {r['ev']}, so {r['ev']} is evicted."


def fifo_say(r):
    if r["res"] == "hit":
        return f"FIFO: also a hit, and the queue does not change on a hit."
    if r["ev"] is None:
        return f"FIFO: a miss into an empty way, and {r['ref']} joins the back of the queue."
    return f"FIFO: a miss; the oldest arrival is {r['ev']}, so {r['ev']} is evicted."


def fill(tid, L, F, i, special=None):
    l, f = L[i], F[i]
    lsay = special[0] if special and special[0] else lru_say(l, None)
    fsay = special[1] if special and special[1] else fifo_say(f)
    if l["res"] == "hit" and f["res"] == "miss":
        fsay = f"FIFO: {f['ref']} is not there, a miss; the oldest is {f['ev']}, so {f['ev']} is evicted."
    if l["res"] == "miss" and f["res"] == "hit":
        fsay = f"FIFO: {f['ref']} is still there, so a hit, and the queue stays as it is."
    s.step(lsay, [{"action": "highlight", "target": f"{tid}[{i}]"},
                  {"action": "set", "target": f"{tid}[{i}][2]", "value": ways_s(l["ways"])},
                  {"action": "set", "target": f"{tid}[{i}][3]", "value": " ".join(l["order"]), "delay": 0.3},
                  {"action": "set", "target": f"{tid}[{i}][4]", "value": l["res"] + (f" ({l['ev']} out)" if l["ev"] else ""), "delay": 0.5}])
    s.step(fsay, [{"action": "set", "target": f"{tid}[{i}][5]", "value": ways_s(f["ways"])},
                  {"action": "set", "target": f"{tid}[{i}][6]", "value": " ".join(f["order"]), "delay": 0.3},
                  {"action": "set", "target": f"{tid}[{i}][7]", "value": f["res"] + (f" ({f['ev']} out)" if f["ev"] else ""), "delay": 0.5}])


# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("Last video, a miss brought a new block into the cache.", [s.head("Replacement: which block is thrown out?")])
s.step("But when the place it must go is already full, something has to leave.", [])
s.step("That is question three: on a miss, which block is replaced?", [s.take("Q3 replacement: on a miss with no free way, which block leaves?")])
s.step("We compare three answers: LRU, FIFO and random.", [])
s.step("Here are the six stages, with two reference strings worked by hand.", [s.untake(), {"action": "show", "target": "stages"}])
s.step("First when a choice exists, then the LRU and FIFO rules.", [{"action": "highlight", "target": "stages[0..=2]"}])
s.step("Then one string traced with both, and a second string that is a favourite exam trap.", [{"action": "highlight", "target": "stages[3..=4]"}])
s.step("Last, random replacement and the hardware cost of each.", [{"action": "highlight", "target": "stages[5]"}])

# ---------------------------------------------------------------- when
s.scene("when")
s.step("Stage 1: when does the cache have to choose?", [s.head("Stage 1 of 6: when is there a choice?"), {"action": "hide", "target": "stages"}, {"action": "show", "target": "when"}])
s.step("In a direct-mapped cache, a block has one possible line, so there is nothing to choose.", [{"action": "highlight", "target": "when[0]"}])
s.step("Whatever sits in that line is replaced, every time.", [{"action": "highlight", "target": "when[0][2]"}])
s.step("In a set-associative cache, the block may use any way of its set.", [{"action": "highlight", "target": "when[1]"}])
s.step("If a way is empty, it goes there; only when every way is full must we pick a victim.", [{"action": "highlight", "target": "when[1][2]"}])
s.step("Fully associative is the same, with the whole cache as one set.", [{"action": "highlight", "target": "when[2]"}])
s.step("For our examples, take one set with three ways, and blocks named A, B, C and D.", [s.take("one set · 3 ways · blocks A, B, C, D · all start empty")])
s.step("Four blocks and only three ways: someone will have to leave.", [])

# ---------------------------------------------------------------- rules
s.scene("rules")
s.step("Stage 2: the LRU rule.", [s.head("Stages 2 and 3 of 6: the LRU and FIFO rules"), {"action": "hide", "target": "when"}, s.untake(), {"action": "show", "target": "rules"}])
s.step("LRU stands for least recently used: evict the block that has gone unused the longest.", [{"action": "highlight", "target": "rules[0][1]"}])
s.step("To do that it keeps an order of the blocks, least recently used first.", [{"action": "highlight", "target": "rules[0][2]"}])
s.step("Every access, a hit as well as a miss, moves that block to the most recent end.", [{"action": "highlight", "target": "rules[0][3]"}])
s.step("The idea is temporal locality: a block used recently is likely to be used again soon.", [s.take("LRU bets on temporal locality: recently used → used again soon")])
s.step("Stage 3: the FIFO rule, first in, first out.", [{"action": "highlight", "target": "rules[1]"}])
s.step("FIFO evicts the block that arrived first, however often it has been used since.", [{"action": "highlight", "target": "rules[1][1]"}])
s.step("It keeps a queue by arrival time, oldest at the front.", [{"action": "highlight", "target": "rules[1][2]"}])
s.step("A hit does not change the queue; only a miss adds a block at the back.", [{"action": "highlight", "target": "rules[1][3]"}])
s.step("This one difference, whether a hit updates the order, is where the two policies part ways.", [{"action": "mark", "target": "rules.c3"}, s.take("LRU: every access reorders · FIFO: only misses enter the queue")])

# ---------------------------------------------------------------- string 1
s.scene("string1")
s.step("Stage 4: reference string one is A, B, C, B, A, D, B, A, B.", [s.head("Stage 4 of 6: reference string 1"), {"action": "hide", "target": "rules"}, s.untake(), {"action": "show", "target": "t1"}])
s.step("For each reference we write the ways, the order, and hit or miss, for LRU and then FIFO.", [{"action": "highlight", "target": "t1.c1"}])
for i in range(len(S1)):
    if i == 0:
        fill("t1", L1, F1, i, ("Reference 1, A: the set is empty, so it is a miss, and A goes into way 0.",
                               "FIFO does exactly the same: a miss, and A is first in the queue."))
    elif i == 2:
        fill("t1", L1, F1, i, (None, "FIFO: the same miss; the queue is now A, B, C, oldest first."))
    elif i == 3:
        fill("t1", L1, F1, i, ("LRU: B is there, a hit, so B moves to the most recent end: A, C, B.", None))
    elif i == 4:
        fill("t1", L1, F1, i, ("LRU: A hits too, and moves to the end: C, B, A.", "FIFO: a hit as well, and the queue is still A, B, C."))
    elif i == 5:
        fill("t1", L1, F1, i, ("D misses, the set is full, and LRU's least recent block is C, so C is evicted.",
                               "FIFO evicts the oldest arrival, A, even though A was just used."))
    else:
        fill("t1", L1, F1, i)
s.step("Count the hits: LRU has 5 of 9, FIFO has 3 of 9.", [{"action": "mark", "target": "t1.c4"}, {"action": "highlight", "target": "t1.c7", "delay": 0.5}])
s.step("Check: hits plus misses must be 9 in each column: 5 plus 4, and 3 plus 6.", [])
s.step("LRU won because A and B were reused, and FIFO threw A out by age, not by use.", [s.take("string 1: LRU 5 hits · FIFO 3 hits — reuse rewards LRU")])

# ---------------------------------------------------------------- string 2
s.scene("string2")
s.step("Stage 5, the trap: is LRU always better than FIFO?", [s.head("Stage 5 of 6: the trap — FIFO beats LRU"), {"action": "hide", "target": "t1"}, s.untake(), {"action": "show", "target": "t2"}])
s.step("Take reference string two: A, B, A, C, D, B, A, C, D, with the same three ways.", [{"action": "highlight", "target": "t2.c1"}])
for i in range(len(S2)):
    if i == 2:
        fill("t2", L2, F2, i, ("LRU: A hits, and moves to the end: B, A.", "FIFO: a hit too; the queue stays A, B."))
    elif i == 4:
        fill("t2", L2, F2, i, ("D misses; LRU's least recent is B, so B is evicted.", "FIFO evicts the oldest arrival, which is A."))
    elif i == 5:
        fill("t2", L2, F2, i, ("Now B returns: LRU just threw B out, so a miss, and A goes.", None))
    else:
        fill("t2", L2, F2, i)
s.step("Count: LRU has just 1 hit of 9, FIFO has 4 of 9.", [{"action": "mark", "target": "t2.c7"}, {"action": "highlight", "target": "t2.c4", "delay": 0.5}])
s.step("Look at LRU's first four evictions: B, A, C, D, and each is the very block needed next.", [{"action": "highlight", "target": "t2.c4"}])
s.step("The string cycles through four blocks in three ways, and LRU always throws out the next one in the cycle.", [s.take("string 2: LRU 1 hit · FIFO 4 hits — LRU is not always better")])
s.step("So the result depends on the reference string; no policy wins on every string.", [{"action": "hide", "target": "t2"}, {"action": "show", "target": "score"}])
s.step("String one rewarded reuse, so LRU won; string two punished it, so FIFO won.", [{"action": "highlight", "target": "score[0]"}, {"action": "highlight", "target": "score[1]", "delay": 0.5}])
s.step("In an exam, say LRU usually misses less on real programs, never that it always does.", [{"action": "mark", "target": "score.winner"}])

# ---------------------------------------------------------------- random and cost
s.scene("random")
s.step("Stage 6: random replacement picks any way of the set, by chance.", [s.head("Stage 6 of 6: random, and what each policy costs"), {"action": "hide", "target": "score"}, s.untake(), {"action": "show", "target": "cost"}])
s.step("It keeps no history at all, so it cannot be fooled by a pattern like string two, and cannot exploit string one.", [{"action": "highlight", "target": "cost[3]"}])
s.step("Hardware uses a pseudo-random generator, often a small shift register, shared by every set.", [{"action": "highlight", "target": "cost[3][1]"}])
s.step("LRU is the expensive one: it must track the full order of the ways and update it on every hit.", [{"action": "highlight", "target": "cost[0]"}])
s.step("For two ways that is one bit per set, but the order grows quickly with more ways.", [{"action": "highlight", "target": "cost[0][1]"}])
s.step("So real caches with many ways use pseudo-LRU, a few bits per set that approximate the true order.", [{"action": "highlight", "target": "cost[1]"}])
s.step("FIFO needs only a pointer to the oldest way, moved on each miss.", [{"action": "highlight", "target": "cost[2]"}])
s.step("And in large caches, random's miss rate comes close to LRU's, which is why it is still used.", [{"action": "highlight", "target": "cost[3][3]"}])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the six stages again.", [s.head("Recap"), {"action": "hide", "target": "cost"}, {"action": "show", "target": "stages"}, {"action": "reset", "target": "stages"}])
s.step("A choice exists only in set-associative and fully associative caches, when every way is full.", [{"action": "highlight", "target": "stages[0]"}])
s.step("LRU evicts the least recently used block and reorders on every access.", [{"action": "highlight", "target": "stages[1]"}])
s.step("FIFO evicts the oldest arrival, and a hit changes nothing.", [{"action": "highlight", "target": "stages[2]"}])
s.step("String one: LRU 5 hits, FIFO 3. String two: LRU 1 hit, FIFO 4.", [{"action": "highlight", "target": "stages[3..=4]"}])
s.step("Random is cheapest, LRU costs the most, and pseudo-LRU sits between.", [{"action": "highlight", "target": "stages[5]"}])
s.step("Next video: question four, writes, and the three kinds of miss.", [{"action": "mark", "target": "stages[0..=5]"}, s.take("Next: write policies and the three C's")])

s.save(sys.argv[1])
