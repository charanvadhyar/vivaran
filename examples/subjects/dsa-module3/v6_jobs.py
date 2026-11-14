"""DSA Module 3, video 6: greedy method, job sequencing with deadlines."""
import sys
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa3")
from common import Script
from h import *
from greedy import job_seq, brute

J = [("J1", 3, 35), ("J2", 4, 30), ("J3", 4, 25), ("J4", 2, 20), ("J5", 3, 15), ("J6", 1, 12), ("J7", 2, 5)]
SL, LG = job_seq(J); assert SL == ["J4", "J3", "J1", "J2"] and brute(J) == 110 == 35 + 30 + 25 + 20
assert [x[3] for x in LG] == [3, 4, 2, 1, None, None, None]
E = [("J1", 2, 20), ("J2", 2, 15), ("J3", 1, 10), ("J4", 3, 5), ("J5", 3, 1)]
ES, EL = job_seq(E); assert ES == ["J2", "J1", "J4"] and brute(E) == 40
# earliest-slot variant fails on: J1 d2 p10, J2 d1 p9
def earliest(jobs):
    order = sorted(jobs, key=lambda j: -j[2]); D = max(j[1] for j in jobs); slot = [None] * (D + 1)
    for n, d, p in order:
        for t in range(1, d + 1):
            if slot[t] is None: slot[t] = (n, p); break
    return sum(x[1] for x in slot[1:] if x)
assert earliest([("J1", 2, 10), ("J2", 1, 9)]) == 10 and brute([("J1", 2, 10), ("J2", 1, 9)]) == 19
assert 4 + 1 + 1 == 6 and 3 + 3 == 6  # coin change counterexample {1,3,4}

s = Script("Greedy: job sequencing with deadlines")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The greedy method"],
    [2, "The problem: jobs, deadlines, profits"],
    [3, "The greedy rule"],
    [4, "Seven jobs, traced"],
    [5, "The algorithm and its cost"],
    [6, "Why greedy is optimal here"],
    [7, "Exam question"]]})
s.obj({"id": "gm", "type": "table", "region": "center", "columns": ["the greedy method", ""], "rows": [
    ["build the answer one choice at a time", "each time, take what looks best right now"],
    ["never undo a choice", "fast: usually a sort plus one pass"],
    ["it works when", "a locally best choice is always part of some optimal answer"],
    ["it can fail", "coins 1, 3, 4 for 6: greedy 4 + 1 + 1 (3 coins), best 3 + 3 (2 coins)"],
    ["this module", "job sequencing, Prim, Kruskal, Huffman: all provably optimal"]]})
s.obj({"id": "pb", "type": "table", "region": "center", "columns": ["job sequencing with deadlines", ""], "rows": [
    ["n jobs", "each takes one unit of time on a single machine"],
    ["job i", "a deadline dᵢ and a profit pᵢ"],
    ["profit", "earned only if job i finishes by time dᵢ"],
    ["goal", "choose and order jobs to maximise the total profit"],
    ["feasible set", "its jobs can all be scheduled before their deadlines"]]})
s.obj({"id": "rule", "type": "table", "region": "center", "columns": ["greedy rule", "why"], "rows": [
    ["consider jobs in decreasing order of profit", "the most valuable jobs get first claim"],
    ["put each job in the latest free slot ≤ its deadline", "keeps early slots free for jobs with tight deadlines"],
    ["no free slot at or before the deadline", "reject the job"],
    ["earliest free slot instead?", "J1 (d 2, p 10), J2 (d 1, p 9): J1 takes slot 1, J2 is lost: 10, not 19"]]})
s.obj({"id": "jt", "type": "table", "region": "left", "columns": ["job", "deadline", "profit", "slot"],
       "rows": [[n, str(d), str(p), ""] for n, d, p in J]})
s.obj({"id": "sl", "type": "table", "region": "right", "columns": ["slot 1", "slot 2", "slot 3", "slot 4"], "rows": [["", "", "", ""]]})
s.obj({"id": "ac", "type": "code", "region": "center", "language": "text", "lines": [
    "JOB-SEQUENCING(d, p, n)",
    "    sort the jobs so that p[1] ≥ p[2] ≥ … ≥ p[n]",
    "    slot[1 .. dmax] = empty",
    "    for i = 1 to n",
    "        for t = min(dmax, d[i]) downto 1",
    "            if slot[t] is empty",
    "                slot[t] = i;  break",
    "    return slot",
    "",
    "sort: O(n log n)   ·   slot search: O(n) per job   ·   total O(n²);  O(n log n) with disjoint sets"]})
s.obj({"id": "pf", "type": "table", "region": "center", "columns": ["why it is optimal (exchange argument)", ""], "rows": [
    ["let G be greedy's set, O an optimal set", "suppose they first differ at job a, the most profitable job where they disagree"],
    ["case 1: a in G, not in O", "a fits where O schedules some cheaper job b; swap b for a: profit does not drop"],
    ["case 2: a in O, not in G", "greedy rejected a only because all slots ≤ dₐ held more profitable jobs, which O also has: then O is infeasible"],
    ["repeat", "O turns into G without losing profit: G is optimal"],
    ["two ingredients", "greedy-choice property + optimal substructure"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question"], "rows": [
    ["n = 5: profits (20, 15, 10, 5, 1), deadlines (2, 2, 1, 3, 3)"],
    ["a) the slot chosen for each job, in greedy order"],
    ["b) the schedule and its total profit"],
    ["c) is ordering by deadline (earliest first) also optimal here? check"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["part", "working", "answer"], "rows": [
    ["a)", "J1 (p 20, d 2) → slot 2;  J2 (p 15, d 2) → slot 1", ""],
    ["a)", "J3 (d 1): slot 1 taken → rejected;  J4 (d 3) → slot 3;  J5 (d 3): 3, 2, 1 taken → rejected", ""],
    ["b)", "J2, J1, J4", "20 + 15 + 5 = 40"],
    ["c)", "earliest deadline first: J3, J1 (or J2), J4: 10 + 20 + 5", "35 < 40: not optimal"]]})

s.scene("intro")
s.step("A printer, a compute cluster, a freelancer with too many offers: each job pays only if it is done by its deadline, and there is time for only some of them. Which jobs should you take? This video introduces the greedy method, and solves this problem with it.", [s.head("Greedy: job sequencing with deadlines")])
s.step("Here are the seven stages.", show("stages"))
s.step("The greedy method, the problem, the greedy rule, and a full trace.", [hl("stages[0..=3]")])
s.step("Then the algorithm and its cost, why greedy is optimal here, and an exam question.", [hl("stages[4..=6]")])

s.scene("gm")
s.step("Stage 1: a greedy algorithm builds its answer one choice at a time, always taking what looks best at that moment.", [s.head("Stage 1 of 7: the greedy method")] + hide("stages") + show("gm") + [hl("gm[0]")])
s.step("It never goes back on a choice. That makes it fast: usually a sort and a single pass.", [hl("gm[1]")])
s.step("It gives the best answer only when a locally best choice is always part of some optimal solution. That has to be proved for each problem.", [hl("gm[2]")])
s.step("It can fail. Make 6 from coins of 1, 3 and 4: greedy takes 4, then 1 and 1: three coins. But 3 plus 3 uses two.", [hl("gm[3]")])
s.step("In this module, greedy is provably optimal: job sequencing, the two minimum spanning tree algorithms, and Huffman coding.", [hl("gm[4]"), s.take("greedy: best-looking choice, never undone")])

s.scene("pb")
s.step("Stage 2: n jobs share one machine. Each job takes one unit of time.", [s.head("Stage 2 of 7: the problem"), s.untake()] + hide("gm") + show("pb") + [hl("pb[0]")])
s.step("Job i has a deadline d i and a profit p i.", [hl("pb[1]")])
s.step("The profit is earned only if the job finishes by its deadline. A job with deadline 2 must run in slot 1 or slot 2.", [hl("pb[2]")])
s.step("Choose which jobs to run, and when, to make the total profit as large as possible. A set of jobs that can all meet their deadlines is called feasible.", [hl("pb[3..=4]"), s.take("unit jobs, deadlines, maximise profit")])
s.step("Trying every subset is hopeless: 7 jobs give 128 subsets, but 50 jobs give over a thousand million million. Greedy needs one sort and one pass.", [hl("pb[3]")])
s.step("One useful fact: a set of jobs is feasible exactly when, run in order of deadline, each one finishes in time. So we never need to try every order, only to check the sorted one.", [hl("pb[4]")])

s.scene("rule")
s.step("Stage 3: the greedy rule. Consider the jobs from the most profitable down.", [s.head("Stage 3 of 7: the greedy rule"), s.untake()] + hide("pb") + show("rule") + [hl("rule[0]")])
s.step("Put each one in the latest free slot at or before its deadline. That leaves the early slots for jobs whose deadlines are tighter.", [hl("rule[1]")])
s.step("If every slot up to its deadline is taken, reject the job.", [hl("rule[2]")])
s.step("Why the latest slot? Suppose J1 has deadline 2 and profit 10, and J2 has deadline 1 and profit 9. Putting J1 in the earliest slot, 1, leaves no room for J2: profit 10. In slot 2, both fit: 19.", [hl("rule[3]"), s.take("highest profit first, latest free slot")])

s.scene("trace")
s.step("Stage 4: seven jobs, already sorted by profit, from 35 down to 5. The largest deadline is 4, so there are four slots.", [s.head("Stage 4 of 7: seven jobs"), s.untake()] + hide("rule") + show("jt", "sl"))
say = ["J1, profit 35, deadline 3: slot 3 is free. Take it.",
       "J2, profit 30, deadline 4: slot 4 is free. Take it.",
       "J3, profit 25, deadline 4: slot 4 is taken, slot 3 is taken, slot 2 is free. Take it.",
       "J4, profit 20, deadline 2: slot 2 is taken, slot 1 is free. Take it. All four slots are full now.",
       "J5, profit 15, deadline 3: slots 3, 2 and 1 are all taken. Rejected.",
       "J6, deadline 1, and J7, deadline 2: no room either. Rejected."]
for k, (n, d, p, t) in enumerate(LG[:5]):
    acts = [hl(f"jt[{k}]")]
    if t:
        tries = list(range(min(d, 4), t - 1, -1))
        acts += [hl(f"sl[0][{x - 1}]", round(0.15 * i, 2)) for i, x in enumerate(tries)]
        acts += [st(f"sl[0][{t - 1}]", n, 0.6), mk(f"sl[0][{t - 1}]", 0.7), st(f"jt[{k}][3]", str(t), 0.8)]
    else:
        acts += [hl(f"sl[0][{x - 1}]", round(0.15 * i, 2)) for i, x in enumerate(range(d, 0, -1))] + [st(f"jt[{k}][3]", "rejected", 0.7), dim(f"jt[{k}]", 0.8)]
    s.step(say[k], acts)
s.step(say[5], [st("jt[5][3]", "rejected"), dim("jt[5]", 0.2), st("jt[6][3]", "rejected", 0.4), dim("jt[6]", 0.6)])
s.step("The schedule runs J4, J3, J1, J2, in slots 1 to 4. Each meets its deadline. Total profit: 35 plus 30 plus 25 plus 20, 110.", [hl("sl[0]"), s.take("schedule J4 J3 J1 J2: profit 110")])
s.step("Notice that J5, worth 15, is lost even though its deadline is 3: the four slots went to jobs worth more. Checking all 128 subsets by brute force confirms that 110 is the best possible.", [hl("jt[4]")])

s.scene("algo")
s.step("Stage 5: the algorithm. Sort the jobs by profit, largest first, and mark every slot empty.", [s.head("Stage 5 of 7: the algorithm"), s.untake()] + hide("jt", "sl") + show("ac") + [ml("ac", 1, 3)])
s.step("For each job, search downwards from its deadline for an empty slot, and take the first one found.", [ml("ac", 4, 7)])
s.step("Sorting costs n log n. Each search may scan up to n slots, so the simple version is O of n squared.", [ml("ac", 10, 10)])
s.step("With a disjoint-set structure that jumps straight to the latest free slot, the searches become nearly constant, and sorting dominates: O of n log n.", [s.take("O(n²) simple; O(n log n) with disjoint sets")])

s.scene("pf")
s.step("Stage 6: why is this optimal? Compare greedy's set G with an optimal set O.", [s.head("Stage 6 of 7: why it is optimal"), s.untake()] + hide("ac") + show("pf") + [hl("pf[0]")])
s.step("If greedy took job a and O did not, a fits where O runs some less profitable job b. Swapping b for a does not lower O's profit.", [hl("pf[1]")])
s.step("If O took a and greedy rejected it, then every slot up to a's deadline held a more profitable job, all of which O also has. There would be no room for a in O either: impossible.", [hl("pf[2]")])
s.step("Repeating the swap turns O into G without losing profit, so G is optimal too.", [hl("pf[3]")])
s.step("This is the standard proof pattern for greedy algorithms: show that the greedy choice can always be swapped into an optimal solution, and that what remains is a smaller problem of the same kind.", [hl("pf[4]"), s.take("exchange argument: swap greedy's choice in")])

s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("pf") + show("q") + [hl("q[0]")])
s.step("Assign the slots, give the schedule and its profit, and test a different greedy order. Pause and work it out.", [hl("q[1..=3]")])
s.step("a: J1, profit 20, deadline 2: slot 2. J2, profit 15, deadline 2: slot 2 is taken, so slot 1.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("J3 has deadline 1, and slot 1 is taken: rejected. J4, deadline 3: slot 3. J5, deadline 3: every slot is full: rejected.", [hl("qa[1]")])
s.step("b: the schedule is J2, J1, J4, with profit 20 plus 15 plus 5: 40.", [hl("qa[2]"), mk("qa[2][2]", 0.5)])
s.step("c: earliest deadline first runs J3 first, then one of J1 and J2, then J4: 10 plus 20 plus 5, 35. Less than 40, so that order is not optimal.", [hl("qa[3]")])
s.step("The usual slip: placing each job in the earliest free slot. Always search down from the deadline.", [s.take("search from the deadline downwards")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Greedy takes the best-looking choice and never undoes it. For job sequencing: highest profit first, latest free slot before the deadline.", [hl("stages[0..=3]")])
s.step("It costs O of n squared simply, O of n log n with disjoint sets, and an exchange argument proves it optimal.", [hl("stages[4..=5]")])
s.step("Next video: greedy on graphs. Connecting every vertex as cheaply as possible with Prim's algorithm.", [mk("stages[0..=6]"), s.take("Next: Prim's minimum spanning tree")])

s.save("/home/claude/playlist/dsa3/d3v6.json")
