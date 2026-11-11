"""Module 2, video 2: GATE-style problems on tag, index and offset bits, comparators and tag memory."""
import sys
from math import log2
sys.path.insert(0, ".")
from common import Script


def split(addr_bits, cache, block, ways):
    off = int(log2(block)); lines = cache // block; sets = lines // ways
    idx = int(log2(sets)); return off, lines, sets, idx, addr_bits - idx - off


KB = 1024
assert split(32, 64 * KB, 32, 1) == (5, 2048, 2048, 11, 16)
assert split(32, 64 * KB, 32, 4) == (5, 2048, 512, 9, 18)
assert split(32, 64 * KB, 32, 2048) == (5, 2048, 1, 0, 27)
A = 0x1234ABCD
assert (A & 31, (A >> 5) & 2047, A >> 16) == (13, 1374, 4660) and ((A >> 5) & 2047) == 0x55E
B = 0x5678ABCD
assert (B & 31, (B >> 5) & 2047) == (13, 1374) and B >> 16 != A >> 16
assert 2048 * (16 + 1 + 1) == 36864 and 36864 / 8 / KB == 4.5
assert 2048 * (18 + 1 + 1 + 2) == 45056 and 45056 / 8 / KB == 5.5
off, lines = 6, 32 * KB // 64; idx = 32 - 19 - off; assert (idx, 2 ** idx, lines, lines // 2 ** idx) == (7, 128, 512, 4)
assert split(32, 256 * KB, 64, 4) == (6, 4096, 1024, 10, 16)
assert 4096 * (16 + 1 + 1 + 2) == 81920 and 81920 / 8 / KB == 10
E = 0x0040F0C4
assert (E & 63, (E >> 6) & 1023, E >> 16) == (4, 963, 64)
assert int(log2(4 * KB ** 3)) == 32 and 32 // 4 == 8 and int(log2(8)) == 3

assert split(32, 16 * KB, 16, 2) == (4, 1024, 512, 9, 19)
assert int(log2(2 ** 20 // 2)) == 19 and split(19, (8 * KB) // 2, 16 // 2, 1) == (3, 512, 512, 9, 7)
assert split(33, 64 * KB, 32, 1) == (5, 2048, 2048, 11, 17) and split(32, 64 * KB, 64, 1) == (6, 1024, 1024, 10, 16)

s = Script("GATE problems: tag, index and offset bits")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Five formulas, and where the address width comes from"],
    [2, "A direct-mapped cache"],
    [3, "The same cache, 4-way set-associative"],
    [4, "Fully associative, and counting comparators"],
    [5, "Splitting a real hex address, and spotting a conflict"],
    [6, "Tag memory size, and working backwards"],
    [7, "Exam question"]]})
s.obj({"id": "f", "type": "math", "region": "center", "lines": [
    "\"offset bits\" = log_2(\"block size\")",
    "\"lines\" = \"cache size\" / \"block size\"",
    "\"sets\" = \"lines\" / \"ways\"",
    "\"index bits\" = log_2(\"sets\")",
    "\"tag bits\" = \"address bits\" - \"index bits\" - \"offset bits\""]})
s.obj({"id": "edge", "type": "table", "region": "center", "columns": ["the question says", "address bits", "offset counts"], "rows": [
    ["\"32-bit address\"", "32", "bytes in a block"],
    ["\"4 GB byte-addressable memory\"", "log₂(2³²) = 32", "bytes in a block"],
    ["\"4 GB memory, 4-byte words, word-addressable\"", "log₂(2³⁰) = 30", "words in a block: 32 B → 8 words → 3 bits"]]})
s.obj({"id": "g1", "type": "table", "region": "left", "columns": ["given", "value"], "rows": [
    ["address", "32 bits, byte-addressable"], ["cache", "64 KB = 2¹⁶ B"], ["block", "32 B = 2⁵ B"], ["mapping", "direct-mapped"]]})
s.obj({"id": "m1", "type": "math", "region": "right", "lines": [
    "\"offset\" = log_2 32 = 5",
    "\"lines\" = 2^16 / 2^5 = 2^11 = 2048",
    "\"sets\" = 2048 / 1 = 2048 quad => quad \"index\" = 11",
    "\"tag\" = 32 - 11 - 5 = 16"]})
LANE = ["32-bit address"]
UNIT = "bit, most significant first"
for n in (1, 2, 3, 4):
    s.obj({"id": f"bar{n}", "type": "timeline", "region": "center", "lanes": LANE, "end": 32, "unit": UNIT, "now": 0, "blocks": []})
s.obj({"id": "m2", "type": "math", "region": "right", "lines": [
    "\"sets\" = 2048 / 4 = 512 = 2^9 quad => quad \"index\" = 9",
    "\"tag\" = 32 - 9 - 5 = 18",
    "\"ways\" times 2 quad => quad \"index\" - 1, quad \"tag\" + 1"]})
s.obj({"id": "m3", "type": "math", "region": "right", "lines": [
    "\"sets\" = 2048 / 2048 = 1 quad => quad \"index\" = log_2 1 = 0",
    "\"tag\" = 32 - 0 - 5 = 27"]})
s.obj({"id": "cmp", "type": "table", "region": "center", "columns": ["mapping", "offset", "index", "tag", "comparators", "each compares"], "rows": [
    ["direct-mapped", "5", "11", "16", "1", "16 bits"],
    ["4-way", "5", "9", "18", "4", "18 bits"],
    ["fully associative", "5", "0", "27", "2048", "27 bits"]]})
s.obj({"id": "hx", "type": "math", "region": "center", "lines": [
    "\"0x1234ABCD\" = 0001 thin 0010 thin 0011 thin 0100 thin 1010 thin 1011 thin 1100 thin 1101",
    "\"tag\" = \"top 16 bits\" = \"0x1234\" = 4660",
    "\"index\" = \"next 11 bits\" = 10101011110_2 = \"0x55E\" = 1374",
    "\"offset\" = \"last 5 bits\" = 01101_2 = 13",
    "\"0x5678ABCD\": quad \"index\" 1374, quad \"tag\" \"0x5678\" quad => quad \"conflict\""]})
s.obj({"id": "tagm", "type": "math", "region": "center", "lines": [
    "\"bits per line\" = \"tag\" + \"valid\" + \"dirty\" (+ \"LRU bits\")",
    "\"direct-mapped\": 2048 times (16 + 1 + 1) = 36864 \"bits\" = 4.5 \"KB\"",
    "\"4-way, 2 LRU bits\": 2048 times (18 + 1 + 1 + 2) = 45056 \"bits\" = 5.5 \"KB\"",
    "\"data part\": 64 \"KB\" quad \"total\" = 64 + 4.5 = 68.5 \"KB\""]})
s.obj({"id": "back", "type": "math", "region": "center", "lines": [
    "32 \"KB cache\", 64 \"B blocks\", \"tag\" = 19: quad \"ways?\"",
    "\"offset\" = 6 quad \"index\" = 32 - 19 - 6 = 7 quad \"sets\" = 2^7 = 128",
    "\"lines\" = 2^15 / 2^6 = 512 quad \"ways\" = 512 / 128 = 4"]})
s.obj({"id": "qf", "type": "table", "region": "center", "columns": ["variant", "offset", "index", "tag"], "rows": [
    ["16 KB, 2-way, 16 B blocks, 32-bit", "", "", ""],
    ["1 MB of 2-byte words, word-addressable; 8 KB direct-mapped, 16 B blocks", "", "", ""],
    ["the 64 KB direct-mapped cache, memory grows from 4 GB to 8 GB", "", "", ""],
    ["the 64 KB direct-mapped cache, blocks grow from 32 B to 64 B", "", "", ""]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["256 KB, 4-way, 64 B blocks, 32-bit byte addresses; each line has valid, dirty and 2 LRU bits. Find:"], "rows": [
    ["a) offset, index and tag bits"], ["b) the total tag memory, in KB"], ["c) the set and tag of address 0x0040F0C4"]]})
s.obj({"id": "qa", "type": "math", "region": "center", "lines": [
    "\"a)\" quad \"offset\" = 6, quad \"lines\" = 2^18 / 2^6 = 4096, quad \"sets\" = 1024, quad \"index\" = 10, quad \"tag\" = 16",
    "\"b)\" quad 4096 times (16 + 1 + 1 + 2) = 81920 \"bits\" = 10 \"KB\"",
    "\"c)\" quad \"0x0040F0C4\": quad \"offset\" = 4, quad \"set\" = 963, quad \"tag\" = \"0x0040\""]})


def bar(t, tag, idx, off, delay=True):
    out = [{"action": "add_block", "target": t, "id": f"{t}t", "lane": LANE[0], "start": 0, "end": tag, "label": f"tag {tag}"}]
    if idx:
        out.append({"action": "add_block", "target": t, "id": f"{t}i", "lane": LANE[0], "start": tag, "end": tag + idx, "label": f"index {idx}", "delay": 0.3})
    out.append({"action": "add_block", "target": t, "id": f"{t}o", "lane": LANE[0], "start": tag + idx, "end": 32, "label": f"offset {off}", "delay": 0.6})
    return out


# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("Last time we split one address by hand. Now we do it the way GATE asks: many caches, many traps, and every number worked out.", [s.head("GATE problems: tag, index and offset")])
s.step("Here are the seven stages.", [{"action": "show", "target": "stages"}])
s.step("The formulas, then one cache three ways: direct-mapped, set-associative, and fully associative.", [{"action": "highlight", "target": "stages[0..=3]"}])
s.step("Then a real hex address, the size of the tag memory, a question that runs backwards, and an exam question.", [{"action": "highlight", "target": "stages[4..=6]"}])

# ---------------------------------------------------------------- formulas
s.scene("formulas")
s.step("Stage 1: five formulas solve every one of these questions.", [s.head("Stage 1 of 7: the formulas"), {"action": "hide", "target": "stages"}, {"action": "show", "target": "f"}])
s.step("Offset bits pick a byte inside a block: log base 2 of the block size.", [{"action": "highlight", "target": "f[0]"}])
s.step("The number of lines is the cache size over the block size.", [{"action": "reveal", "target": "f[1]"}, {"action": "highlight", "target": "f[1]"}])
s.step("Lines are grouped into sets: lines over ways. Direct-mapped is 1 way; fully associative puts every line in one set.", [{"action": "reveal", "target": "f[2]"}, {"action": "highlight", "target": "f[2]"}])
s.step("Index bits pick the set: log base 2 of the number of sets.", [{"action": "reveal", "target": "f[3]"}, {"action": "highlight", "target": "f[3]"}])
s.step("And the tag is whatever is left of the address.", [{"action": "reveal", "target": "f[4]"}, {"action": "highlight", "target": "f[4]"}, s.take("offset → block size · index → sets · tag → the rest")])
s.step("Edge case: where does the address width come from? Sometimes it is given directly, as a 32-bit address.", [{"action": "hide", "target": "f"}, s.untake(), {"action": "show", "target": "edge"}, {"action": "highlight", "target": "edge[0]"}])
s.step("Sometimes it is the memory size: 4 gigabytes, byte-addressable, is 2 to the 32 bytes, so 32 address bits.", [{"action": "highlight", "target": "edge[1]"}])
s.step("Watch for word-addressable memory. With 4-byte words, 4 gigabytes is 2 to the 30 words, so 30 address bits. And the offset counts words: a 32 byte block is 8 words, so 3 offset bits, not 5.", [{"action": "highlight", "target": "edge[2]"}, s.take("word-addressable: count words, not bytes")])

# ---------------------------------------------------------------- direct
s.scene("direct")
s.step("Stage 2: a 64 kilobyte direct-mapped cache, 32 byte blocks, 32-bit byte addresses.", [s.head("Stage 2 of 7: direct-mapped"), {"action": "hide", "target": "edge"}, s.untake(), {"action": "show", "target": "g1"}])
s.step("Tip: write every size as a power of two first. 64 kilobytes is 2 to the 16; 32 bytes is 2 to the 5.", [{"action": "highlight", "target": "g1[1..=2]"}])
s.step("Offset: log base 2 of 32 is 5 bits.", [{"action": "show", "target": "m1"}, {"action": "highlight", "target": "m1[0]"}])
s.step("Lines: 2 to the 16 over 2 to the 5 is 2 to the 11, which is 2048 lines.", [{"action": "reveal", "target": "m1[1]"}, {"action": "highlight", "target": "m1[1]"}])
s.step("Direct-mapped, so each line is its own set: 2048 sets, and 11 index bits.", [{"action": "reveal", "target": "m1[2]"}, {"action": "highlight", "target": "m1[2]"}])
s.step("Tag: 32 minus 11 minus 5 leaves 16 bits.", [{"action": "reveal", "target": "m1[3]"}, {"action": "highlight", "target": "m1[3]"}])
s.step("Here is the address laid out: 16 tag bits on the left, 11 index bits, then 5 offset bits on the right.", [{"action": "hide", "target": "g1"}, {"action": "hide", "target": "m1"}, {"action": "show", "target": "bar1"}] + bar("bar1", 16, 11, 5))
s.step("Check: the three fields always add up to the address width. 16 plus 11 plus 5 is 32.", [s.take("direct-mapped: tag 16 · index 11 · offset 5")])

# ---------------------------------------------------------------- 4-way
s.scene("setassoc")
s.step("Stage 3: the same cache, but 4-way set-associative.", [s.head("Stage 3 of 7: 4-way set-associative"), {"action": "hide", "target": "bar1"}, s.untake(), {"action": "show", "target": "g1"}, {"action": "highlight", "target": "g1[3]"}])
s.step("The offset does not change: the block is still 32 bytes. Still 2048 lines.", [{"action": "set", "target": "g1[3][1]", "value": "4-way set-associative"}])
s.step("But now 4 lines form a set: 2048 over 4 is 512 sets, 2 to the 9. So 9 index bits.", [{"action": "show", "target": "m2"}, {"action": "highlight", "target": "m2[0]"}])
s.step("Tag: 32 minus 9 minus 5 is 18 bits.", [{"action": "reveal", "target": "m2[1]"}, {"action": "highlight", "target": "m2[1]"}])
s.step("A rule worth remembering: every time the associativity doubles, the index loses one bit and the tag gains one.", [{"action": "reveal", "target": "m2[2]"}, {"action": "highlight", "target": "m2[2]"}])
s.step("The address: 18 tag, 9 index, 5 offset.", [{"action": "hide", "target": "g1"}, {"action": "hide", "target": "m2"}, {"action": "show", "target": "bar2"}] + bar("bar2", 18, 9, 5) + [s.take("4-way: tag 18 · index 9 · offset 5")])

# ---------------------------------------------------------------- fully associative
s.scene("fully")
s.step("Stage 4: now fully associative. Any block can go in any of the 2048 lines.", [s.head("Stage 4 of 7: fully associative"), {"action": "hide", "target": "bar2"}, s.untake(), {"action": "show", "target": "g1"}, {"action": "set", "target": "g1[3][1]", "value": "fully associative"}, {"action": "highlight", "target": "g1[3]"}])
s.step("There is just one set, and log base 2 of 1 is 0: no index bits at all.", [{"action": "show", "target": "m3"}, {"action": "highlight", "target": "m3[0]"}])
s.step("So the tag takes everything but the offset: 27 bits.", [{"action": "reveal", "target": "m3[1]"}, {"action": "highlight", "target": "m3[1]"}, {"action": "hide", "target": "g1", "delay": 0.6}, {"action": "hide", "target": "m3", "delay": 0.6}, {"action": "show", "target": "bar3", "delay": 0.6}] + [dict(a, delay=0.7) for a in bar("bar3", 27, 0, 5)])
s.step("GATE also asks how many comparators the hardware needs, and how wide each one is. One comparator per way, each as wide as the tag.", [{"action": "hide", "target": "bar3"}, {"action": "show", "target": "cmp"}])
s.step("Direct-mapped: 1 comparator of 16 bits. 4-way: 4 comparators of 18 bits.", [{"action": "highlight", "target": "cmp[0..=1]"}])
s.step("Fully associative: all 2048 lines are checked at once, so 2048 comparators of 27 bits. That cost is why large caches are never fully associative.", [{"action": "highlight", "target": "cmp[2]"}, {"action": "mark", "target": "cmp[2][4]", "delay": 0.4}, s.take("comparators = ways · each compares tag bits")])

# ---------------------------------------------------------------- hex address
s.scene("hex")
s.step("Stage 5: back to the direct-mapped cache. Where does address hex 1 2 3 4 A B C D go?", [s.head("Stage 5 of 7: splitting a hex address"), {"action": "hide", "target": "cmp"}, s.untake(), {"action": "show", "target": "hx"}])
s.step("Write each hex digit as 4 bits. Do not convert to decimal first: the fields fall straight out of the binary.", [{"action": "highlight", "target": "hx[0]"}])
s.step("The tag is the top 16 bits, the first four hex digits: hex 1 2 3 4.", [{"action": "reveal", "target": "hx[1]"}, {"action": "highlight", "target": "hx[1]"}])
s.step("The index is the next 11 bits: 1 0 1 0 1 0 1 1 1 1 0, which is hex 5 5 E, or line 1374.", [{"action": "reveal", "target": "hx[2]"}, {"action": "highlight", "target": "hx[2]"}])
s.step("The offset is the last 5 bits: 0 1 1 0 1, byte 13 of the block.", [{"action": "reveal", "target": "hx[3]"}, {"action": "highlight", "target": "hx[3]"}])
s.step("Now hex 5 6 7 8 A B C D. Its last four hex digits are the same, so the same index 1374, but a different tag. In a direct-mapped cache the two fight over one line: a conflict.", [{"action": "reveal", "target": "hx[4]"}, {"action": "highlight", "target": "hx[4]"}, s.take("same index, different tag → they evict each other")])

# ---------------------------------------------------------------- tag memory, backwards
s.scene("tagmem")
s.step("Stage 6: how much extra memory do the tags need? Each line stores its tag, a valid bit, a dirty bit if the cache is write-back, and replacement bits if it is set-associative.", [s.head("Stage 6 of 7: tag memory, and working backwards"), {"action": "hide", "target": "hx"}, s.untake(), {"action": "show", "target": "tagm"}])
s.step("Direct-mapped, write-back: 2048 lines times 16 plus 1 plus 1 bits is 36864 bits, which is 4.5 kilobytes.", [{"action": "reveal", "target": "tagm[1]"}, {"action": "highlight", "target": "tagm[1]"}])
s.step("4-way with 2 LRU bits per line: 2048 times 22 is 45056 bits, 5.5 kilobytes.", [{"action": "reveal", "target": "tagm[2]"}, {"action": "highlight", "target": "tagm[2]"}])
s.step("Edge case: the 64 kilobytes of data are on top of this. And read whether the question wants only the tag bits, or the valid and dirty bits too.", [{"action": "reveal", "target": "tagm[3]"}, {"action": "highlight", "target": "tagm[3]"}])
s.step("Now backwards: a 32 kilobyte cache, 64 byte blocks, and a 19 bit tag. What is the associativity?", [{"action": "hide", "target": "tagm"}, {"action": "show", "target": "back"}, {"action": "highlight", "target": "back[0]"}])
s.step("Offset is 6, so the index is 32 minus 19 minus 6, which is 7: 128 sets.", [{"action": "reveal", "target": "back[1]"}, {"action": "highlight", "target": "back[1]"}])
s.step("The cache has 512 lines, so 512 over 128 is 4 ways. Same formulas, just solved for a different unknown.", [{"action": "reveal", "target": "back[2]"}, {"action": "highlight", "target": "back[2]"}, s.take("tag store = lines × (tag + valid + dirty + LRU)")])

# ---------------------------------------------------------------- quick fire
s.scene("quick")
s.step("Before the exam question, a quick-fire round of four variants GATE likes to ask.", [s.head("Quick-fire variants"), {"action": "hide", "target": "back"}, s.untake(), {"action": "show", "target": "qf"}])
s.step("A 16 kilobyte, 2-way cache with 16 byte blocks: offset 4, 1024 lines, 512 sets, so index 9 and tag 19.", [{"action": "highlight", "target": "qf[0]"}, {"action": "set", "target": "qf[0][1]", "value": "4", "delay": 0.2}, {"action": "set", "target": "qf[0][2]", "value": "9", "delay": 0.5}, {"action": "set", "target": "qf[0][3]", "value": "19", "delay": 0.8}])
s.step("Word-addressable: 1 megabyte of 2 byte words is 2 to the 19 words, so 19 address bits. A 16 byte block is 8 words: offset 3. The cache holds 512 blocks: index 9. Tag: 19 minus 9 minus 3, which is 7.", [{"action": "highlight", "target": "qf[1]"}, {"action": "set", "target": "qf[1][1]", "value": "3 (words)", "delay": 0.3}, {"action": "set", "target": "qf[1][2]", "value": "9", "delay": 0.6}, {"action": "set", "target": "qf[1][3]", "value": "7", "delay": 0.8}])
s.step("If main memory doubles from 4 to 8 gigabytes, addresses get one bit longer. The cache is unchanged, so offset and index stay, and only the tag grows: 17.", [{"action": "highlight", "target": "qf[2]"}, {"action": "set", "target": "qf[2][1]", "value": "5", "delay": 0.2}, {"action": "set", "target": "qf[2][2]", "value": "11", "delay": 0.5}, {"action": "set", "target": "qf[2][3]", "value": "17", "delay": 0.8}])
s.step("If the block doubles to 64 bytes, the offset gains a bit, but the number of lines halves, so the index loses one. The tag stays at 16.", [{"action": "highlight", "target": "qf[3]"}, {"action": "set", "target": "qf[3][1]", "value": "6", "delay": 0.2}, {"action": "set", "target": "qf[3][2]", "value": "10", "delay": 0.5}, {"action": "set", "target": "qf[3][3]", "value": "16", "delay": 0.8}])
s.step("So: bigger memory changes only the tag. Bigger blocks trade index bits for offset bits. More ways trade index bits for tag bits. And for a fixed cache and address, the tag depends only on the associativity.", [s.take("memory ↑ → tag ↑ · block ↑ → offset ↑ index ↓ · ways ↑ → tag ↑ index ↓")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), {"action": "hide", "target": "qf"}, s.untake(), {"action": "show", "target": "q"}])
s.step("A 256 kilobyte, 4-way cache with 64 byte blocks and 32-bit byte addresses. Each line has a valid bit, a dirty bit and 2 LRU bits.", [{"action": "highlight", "target": "q[0]"}])
s.step("Find the three fields, the total tag memory, and the set and tag of address hex 0 0 4 0 F 0 C 4. Pause and work it out.", [{"action": "highlight", "target": "q[1..=2]"}])
s.step("a: offset is log 64, 6 bits. Lines: 2 to the 18 over 2 to the 6, 4096. Sets: 4096 over 4, 1024, so 10 index bits. Tag: 32 minus 10 minus 6, 16 bits.", [{"action": "hide", "target": "q"}, {"action": "show", "target": "qa"}, {"action": "highlight", "target": "qa[0]"}])
s.step("The address, laid out: 16, 10, 6.", [{"action": "hide", "target": "qa"}, {"action": "show", "target": "bar4"}] + bar("bar4", 16, 10, 6))
s.step("b: each line stores 16 plus 1 plus 1 plus 2, which is 20 bits. 4096 lines times 20 is 81920 bits, 10 kilobytes.", [{"action": "hide", "target": "bar4"}, {"action": "show", "target": "qa"}, {"action": "reveal", "target": "qa[1]"}, {"action": "highlight", "target": "qa[1]"}])
s.step("c: the last 6 bits of hex 0 0 4 0 F 0 C 4 give offset 4. The next 10 bits give set 963. And the top 16 bits, hex 0 0 4 0, are the tag.", [{"action": "reveal", "target": "qa[2]"}, {"action": "highlight", "target": "qa[2]"}])
s.step("The usual slips: forgetting to divide lines by ways, mixing bytes and words, and leaving the LRU bits out of the tag memory.", [s.take("lines ÷ ways · bytes vs words · count every bit per line")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), {"action": "hide", "target": "qa"}, s.untake(), {"action": "show", "target": "stages"}])
s.step("Offset from the block size, index from the number of sets, tag from what is left. Doubling the ways moves one bit from index to tag.", [{"action": "highlight", "target": "stages[0..=3]"}])
s.step("Split hex addresses in binary, count every bit stored per line, and run the same formulas backwards when needed.", [{"action": "highlight", "target": "stages[4..=6]"}])
s.step("Next video: what happens on a write, step by step.", [{"action": "mark", "target": "stages[0..=6]"}, s.take("Next: write policies")])

s.save("./m2v2.json")
