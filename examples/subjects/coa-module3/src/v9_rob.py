"""Module 3, video 9: hardware speculation and the reorder buffer."""
import sys
sys.path.insert(0, "/home/claude/playlist")
sys.path.insert(0, "/home/claude/playlist/m3")
from common import Script
from tomasulo import run

LAT = {'L.D': 1, 'S.D': 1, 'ADD.D': 2, 'SUB.D': 2, 'MUL.D': 10, 'DIV.D': 40}
P = [('L.D    F6,34(R2)', 'L.D', 'F6', ['R2']), ('L.D    F2,45(R3)', 'L.D', 'F2', ['R3']),
     ('MUL.D  F0,F2,F4', 'MUL.D', 'F0', ['F2', 'F4']), ('SUB.D  F8,F6,F2', 'SUB.D', 'F8', ['F6', 'F2']),
     ('DIV.D  F10,F0,F6', 'DIV.D', 'F10', ['F0', 'F6']), ('ADD.D  F6,F8,F2', 'ADD.D', 'F6', ['F8', 'F2'])]
_, T = run(P, LAT)
W = [w for *_, w in T]
assert W == [3, 4, 15, 7, 56, 10]


def commits(ready):
    out, last = [], 0
    for r in ready:
        last = max(r + 1, last + 1); out.append(last)
    return out


CM = commits(W)
assert CM == [4, 5, 16, 17, 57, 58]
QR = [3, 14, 6, 7, 9, 8]
QC = commits(QR[:4])
assert QC == [4, 15, 16, 17]

s = Script("Hardware speculation and the reorder buffer")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Why speculate, and what can go wrong"],
    [2, "The reorder buffer"],
    [3, "Four steps: issue, execute, write, commit"],
    [4, "Our example with a commit column"],
    [5, "A snapshot: finished, but not committed"],
    [6, "A mispredicted branch: flushing"],
    [7, "Precise exceptions, and stores"],
    [8, "Exam question"]]})
s.obj({"id": "why", "type": "table", "region": "center", "columns": ["idea", "meaning"], "rows": [
    ["speculate", "run past a predicted branch before it is decided"],
    ["the danger", "a wrong guess must leave no trace"],
    ["also", "exceptions must be precise"],
    ["the fix", "finish out of order, commit in order"]]})
s.obj({"id": "rob", "type": "table", "region": "center", "columns": ["reorder buffer field", "holds"], "rows": [
    ["instruction type", "branch, store, or a register operation"],
    ["destination", "the register number, or the memory address for a store"],
    ["value", "the result, once it has been computed"],
    ["ready", "whether the value is there yet"]]})
s.obj({"id": "robx", "type": "table", "region": "center", "columns": ["change from Tomasulo", "why"], "rows": [
    ["results go to the ROB", "registers hold only committed values"],
    ["tags are ROB numbers", "operands can come from uncommitted entries"],
    ["a circular queue", "enter at the tail, leave from the head, in order"]]})
s.obj({"id": "st4", "type": "table", "region": "center", "columns": ["step", "what happens"], "rows": [
    ["1 Issue", "needs a free station and a free ROB entry; operands from registers, the ROB, or tags"],
    ["2 Execute", "when both operands are present"],
    ["3 Write result", "broadcast on the CDB with the ROB tag; into the ROB entry and waiting stations"],
    ["4 Commit", "when the entry at the head is ready: update the register or memory, free the entry"]]})
s.obj({"id": "is", "type": "table", "region": "center", "columns": ["instruction", "ROB", "write result", "commit"], "rows": [
    [P[i][0], f"#{i + 1}", str(W[i]), ""] for i in range(6)]})
s.obj({"id": "snap", "type": "table", "region": "center", "columns": ["ROB entry", "instruction", "destination", "value", "state at cycle 15"], "rows": [
    ["#1", "L.D", "F6", "Mem[34+R2]", "committed"],
    ["#2", "L.D", "F2", "Mem[45+R3]", "committed"],
    ["#3 ← head", "MUL.D", "F0", "#2 × F4", "written: commits next"],
    ["#4", "SUB.D", "F8", "#1 − #2", "written, waiting for #3"],
    ["#5", "DIV.D", "F10", "", "waiting for #3"],
    ["#6", "ADD.D", "F6", "#4 + #2", "written, waiting"]]})
s.obj({"id": "mp", "type": "table", "region": "center", "columns": ["ROB entry", "instruction", "state"], "rows": [
    ["#1", "L.D    F0,0(R1)", "committed"],
    ["#2", "MUL.D  F4,F0,F2", "committed"],
    ["#3", "S.D    F4,0(R1)", "committed"],
    ["#4", "DADDUI R1,R1,#-8", "committed"],
    ["#5 ← head", "BNE  (predicted taken)", "ready: actually not taken"],
    ["#6", "L.D    F0,0(R1)", "written"],
    ["#7", "MUL.D  F4,F0,F2", "executing"],
    ["#8", "S.D    F4,0(R1)", "waiting"]]})
s.obj({"id": "pe", "type": "table", "region": "center", "columns": ["case", "rule"], "rows": [
    ["an instruction faults", "record it in its ROB entry only"],
    ["it reaches the head", "raise it, flush everything behind"],
    ["it was on a wrong path", "flushed first: no exception"],
    ["a store", "writes memory only at commit"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["instruction", "ROB", "result ready"], "rows": [
    ["L.D    F2,0(R1)", "#1", "3"],
    ["MUL.D  F4,F2,F6", "#2", "14"],
    ["ADD.D  F8,F2,F10", "#3", "6"],
    ["BEQ    (predicted not taken; actually taken)", "#4", "7"],
    ["SUB.D  F12,F8,F14", "#5", "9"],
    ["L.D    F14,8(R1)", "#6", "8"]]})
s.obj({"id": "qx", "type": "table", "region": "center", "columns": ["one commit per cycle, in order. Find:"], "rows": [
    ["a) the commit cycles of #1 to #4"], ["b) what happens to #5 and #6, and to F12 and F14"], ["c) what if the MUL.D had raised an exception instead"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["instruction", "ROB", "result ready", "commit"], "rows": [
    ["L.D    F2,0(R1)", "#1", "3", "4"],
    ["MUL.D  F4,F2,F6", "#2", "14", "15"],
    ["ADD.D  F8,F2,F10", "#3", "6", "16"],
    ["BEQ    (mispredicted)", "#4", "7", "17: flush"],
    ["SUB.D  F12,F8,F14", "#5", "9", "flushed"],
    ["L.D    F14,8(R1)", "#6", "8", "flushed"]]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
st = lambda t, v, d=0: {"action": "set", "target": t, "value": v, **({"delay": d} if d else {})}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("A good predictor is right most of the time. To profit, the machine must act on its guesses: fetch, issue and even execute instructions beyond a branch before the branch is decided. That is speculation, and it needs one more structure.", [s.head("Hardware speculation and the reorder buffer")])
s.step("Here are the eight stages.", show("stages"))
s.step("Why speculate, the reorder buffer, the four steps, and our example with a commit column.", [hl("stages[0..=3]")])
s.step("Then a snapshot, a mispredicted branch, precise exceptions and stores, and an exam question.", [hl("stages[4..=7]")])

# ---------------------------------------------------------------- why
s.scene("why")
s.step("Stage 1: to speculate is to execute instructions past a predicted branch, before knowing whether the prediction is right.", [s.head("Stage 1 of 8: why speculate")] + hide("stages") + show("why") + [hl("why[0]")])
s.step("The danger: if the guess was wrong, those instructions must leave no trace. Not in the registers, not in memory.", [hl("why[1]")])
s.step("And exceptions must be precise: if an instruction faults, every earlier instruction has finished and no later one has changed anything. Plain Tomasulo cannot promise that, since it writes registers out of order.", [hl("why[2]")])
s.step("The fix: let instructions finish out of order, but make their results official in program order. That final step is called commit.", [hl("why[3]"), s.take("execute out of order · commit in order")])

# ---------------------------------------------------------------- ROB
s.scene("rob")
s.step("Stage 2: the reorder buffer, or ROB, holds every instruction between issue and commit. Each entry has four fields.", [s.head("Stage 2 of 8: the reorder buffer"), s.untake()] + hide("why") + show("rob"))
s.step("The instruction type: a branch, a store, or an operation that writes a register.", [hl("rob[0]")])
s.step("The destination: the register number, or for a store, the memory address.", [hl("rob[1]")])
s.step("The value, once computed, and a ready flag.", [hl("rob[2..=3]")])
s.step("What changes from Tomasulo? Results go into the ROB, not the register file. The registers hold only committed values.", hide("rob") + show("robx") + [hl("robx[0]")])
s.step("Tags are now ROB entry numbers. A waiting instruction can take its operand from a finished entry that has not yet committed. So the ROB does the renaming, and supplies values too.", [hl("robx[1]")])
s.step("And the ROB is a circular queue: instructions enter at the tail in program order and leave from the head in the same order.", [hl("robx[2]"), s.take("the ROB: results wait here until they commit")])

# ---------------------------------------------------------------- 4 steps
s.scene("steps")
s.step("Stage 3: now there are four steps.", [s.head("Stage 3 of 8: four steps"), s.untake()] + hide("robx") + show("st4"))
s.step("Issue needs a free reservation station and a free ROB entry. Operands come from the registers, from a finished ROB entry, or as a tag to wait for.", [hl("st4[0]")])
s.step("Execute, when both operands are present, exactly as before.", [hl("st4[1]")])
s.step("Write result: broadcast on the CDB, labelled with the ROB number. The value goes into the ROB entry and to any waiting stations.", [hl("st4[2]")])
s.step("Commit: when the instruction at the head of the ROB is ready, its value is copied to the register, or a store writes memory, and the entry is freed. One commit at a time, always from the head.", [hl("st4[3]"), s.take("issue → execute → write → commit")])

# ---------------------------------------------------------------- example
s.scene("example")
s.step("Stage 4: our six instructions, with the write cycles from the Tomasulo trace. Each gets a ROB entry, 1 to 6.", [s.head("Stage 4 of 8: adding a commit column"), s.untake()] + hide("st4") + show("is"))
s.step("The first load wrote in 3, so it commits in 4. The second wrote in 4 and commits in 5.", [st("is[0][3]", "4"), st("is[1][3]", "5", 0.4)])
s.step("The multiply wrote in 15: commit in 16.", [st("is[2][3]", "16")])
s.step("The subtract finished long ago, in cycle 7. But it must wait for the multiply ahead of it. It commits in 17.", [hl("is[3][2]"), st("is[3][3]", "17", 0.4)])
s.step("The divide writes in 56 and commits in 57. And the add, ready since cycle 10, commits last, in 58.", [st("is[4][3]", "57"), st("is[5][3]", "58", 0.4)])
s.step("Finish order: 3, 4, 7, 10, 15, 56. Commit order: strictly 1 to 6. The registers change in program order, exactly as if the machine were sequential.", [hl("is[0..=5]"), s.take("finish in any order · commit in program order")])

# ---------------------------------------------------------------- snapshot
s.scene("snap")
s.step("Stage 5: the ROB at the end of cycle 15, the moment the multiply has written its result.", [s.head("Stage 5 of 8: a snapshot at cycle 15"), s.untake()] + hide("is") + show("snap"))
s.step("Both loads have committed and left. The head is entry 3, the multiply, now ready.", [hl("snap[0..=1]"), hl("snap[2]", 0.4)])
s.step("Entries 4 and 6, the subtract and the add, already hold their values. But F8 and F6 in the register file still have their old contents.", [hl("snap[3]"), hl("snap[5]", 0.3)])
s.step("Entry 5, the divide, has just received the multiply's value from the bus and begins executing.", [hl("snap[4]")])
s.step("If anything went wrong now, the hardware would simply throw away entries 4 to 6. Nothing they computed has reached the registers.", [hl("snap[3..=5]"), s.take("finished is not committed")])

# ---------------------------------------------------------------- mispredict
s.scene("flush")
s.step("Stage 6: a mispredicted branch. A loop, with its branch predicted taken, so the next iteration has already issued behind it.", [s.head("Stage 6 of 8: flushing a wrong path"), s.untake()] + hide("snap") + show("mp"))
s.step("Entries 1 to 4, the current iteration, have committed.", [hl("mp[0..=3]")])
s.step("The branch reaches the head, and its outcome is known: not taken. The loop should have exited.", [hl("mp[4]")])
s.step("So every entry behind it, 6, 7 and 8, is on the wrong path. They are flushed: removed from the ROB and the stations, whatever stage they were in. Fetching restarts at the correct address.", [st("mp[5][2]", "flushed"), st("mp[6][2]", "flushed", 0.2), st("mp[7][2]", "flushed", 0.4), hl("mp[5..=7]", 0.5)])
s.step("The load in entry 6 had even finished. It does not matter: it never committed, so no register changed. Speculation was undone completely.", [hl("mp[5]"), s.take("a wrong guess: flush everything behind the branch")])

# ---------------------------------------------------------------- exceptions
s.scene("exc")
s.step("Stage 7: exceptions use the same mechanism.", [s.head("Stage 7 of 8: precise exceptions and stores"), s.untake()] + hide("mp") + show("pe"))
s.step("If an instruction faults, say a page fault on a load, the fault is only recorded in its ROB entry.", [hl("pe[0]")])
s.step("When that entry reaches the head, the exception is raised and everything behind it is flushed. Every earlier instruction has committed; no later one has. A precise exception.", [hl("pe[1]")])
s.step("And if the faulting instruction was on a wrong path, it is flushed before it ever reaches the head. The exception never happens, as it should not.", [hl("pe[2]")])
s.step("Stores write memory only when they commit. So a speculative store can never change memory. Loads can still take a value straight from an earlier store's ROB entry, when the addresses match.", [hl("pe[3]"), s.take("exceptions and stores both wait for commit")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("pe") + show("q"))
s.step("Six instructions with the cycle each result is ready. The branch was predicted not taken, but is actually taken. One commit per cycle, in order.", [hl("q[3]")])
s.step("Find the commit cycles of the first four, what happens to entries 5 and 6, and what would change if the multiply had raised an exception. Pause and work it out.", hide("q") + show("qx") + [hl("qx")])
s.step("a: the load commits in 4. The multiply is ready in 14: commit 15. The add was ready in 6, but must follow the multiply: 16. The branch, ready in 7, commits in 17.", hide("qx") + show("qa") + [hl("qa[0..=3]")])
s.step("b: at commit, the branch is found mispredicted. Entries 5 and 6 are flushed, though both had finished. F12 and F14 keep their old values.", [hl("qa[3..=5]")])
s.step("c: an exception in the multiply would be raised when it reaches the head, in cycle 15. The load before it has committed; the add, the branch and everything after are flushed. F4 and F8 stay unchanged, and the handler sees a precise state.", [hl("qa[1]")])
s.step("The usual slip: committing an instruction as soon as it is ready. It must also be at the head.", [s.take("commit = ready AND at the head")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Speculation executes past predicted branches. The reorder buffer holds results until they commit, in program order.", [hl("stages[0..=4]")])
s.step("A wrong guess or an exception flushes everything behind the instruction at the head, leaving a precise state.", [hl("stages[5..=6]")])
s.step("Next video: multiple issue with dynamic scheduling. Putting several of these instructions through every stage, each cycle.", [mk("stages[0..=7]"), s.take("Next: multiple issue with speculation")])

s.save("/home/claude/playlist/m3/m3v9.json")
