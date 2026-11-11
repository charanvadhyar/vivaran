"""Video 1: cache basics. Four questions, mapping, and splitting an address."""
import json, sys

A, B = 0x1A7C, 0x2A70
bitsA = [int(c) for c in format(A, "016b")]
bitsB = [int(c) for c in format(B, "016b")]
assert (A >> 4) % 16 == 7 and A >> 8 == 26 and (A >> 4) % 8 == 7 and A >> 7 == 52 and A >> 4 == 423
assert (B >> 4) % 16 == 7 and B >> 8 == 42 and (B >> 4) % 8 == 7 and B >> 7 == 84 and B >> 4 == 679

objects = [
    {"id": "head", "type": "text", "region": "title", "text": "Cache basics: where a block goes, and how it is found"},
    {"id": "takeaway", "type": "text", "region": "bottom", "text": " "},
    # stage list
    {"id": "stages", "type": "table", "region": "center", "columns": ["stage", "question it answers"], "rows": [
        [1, "The four questions every cache must answer"],
        [2, "Our example cache, in numbers"],
        [3, "Q1 placement: direct, set-associative, fully associative"],
        [4, "Splitting an address into tag, index, offset"],
        [5, "Q2 identification: valid bit and tag compare"],
        [6, "The same address in 2-way and fully associative"],
        [7, "A conflict: why associativity helps"],
    ]},
    # four questions
    {"id": "four", "type": "table", "region": "center", "columns": ["question", "what it asks", "this video?"], "rows": [
        ["Q1 placement", "Where can a block be placed in the cache?", "yes"],
        ["Q2 identification", "How is a block found if it is in the cache?", "yes"],
        ["Q3 replacement", "Which block is thrown out on a miss?", "video 2"],
        ["Q4 write strategy", "What happens on a write?", "video 3"],
    ]},
    # numbers
    {"id": "spec", "type": "table", "region": "left", "columns": ["given", "value"], "rows": [
        ["address size", "16 bits"], ["byte addressable", "yes"], ["cache size", "256 bytes"], ["block size", "16 bytes"]]},
    {"id": "calc", "type": "math", "region": "right", "lines": [
        "\"blocks in cache\" = \"cache size\" / \"block size\"",
        "= 256 / 16 = 16 \"lines\"",
        "\"block number\" = floor(\"address\" / \"block size\")",
        "\"offset\" = \"address\" mod \"block size\""]},
    # placement
    {"id": "place", "type": "table", "region": "left", "columns": ["mapping", "a block can go", "rule"], "rows": [
        ["direct-mapped", "exactly one line", "block mod 16"],
        ["2-way set-assoc.", "either way of one set", "block mod 8"],
        ["fully associative", "any of the 16 lines", "no rule"]]},
    {"id": "placemath", "type": "math", "region": "right", "lines": [
        "\"sets\" = \"blocks\" / \"ways\"",
        "\"direct-mapped\": 16 / 1 = 16 \"sets\"",
        "\"2-way\": 16 / 2 = 8 \"sets\"",
        "\"fully associative\": 16 / 16 = 1 \"set\""]},
    # split formula
    {"id": "split", "type": "math", "region": "center", "lines": [
        "\"offset bits\" = log_2(\"block size\") = log_2(16) = 4",
        "\"index bits\" = log_2(\"sets\") = log_2(16) = 4",
        "\"tag bits\" = 16 - 4 - 4 = 8",
        "\"check\": 8 + 4 + 4 = 16 \"address bits\""]},
    # address bits
    {"id": "hex", "type": "math", "region": "title", "lines": ["\"0x1A7C\" = 0001 thin 1010 thin 0111 thin 1100"]},
    {"id": "bits", "type": "array", "region": "center", "values": bitsA},
    {"id": "p_tag", "type": "pointer", "label": "tag (8)", "target": "bits[3]"},
    {"id": "p_idx", "type": "pointer", "label": "index (4)", "target": "bits[9]"},
    {"id": "p_off", "type": "pointer", "label": "offset (4)", "target": "bits[13]"},
    {"id": "fields", "type": "table", "region": "center", "columns": ["field", "bits", "binary", "value"], "rows": [
        ["tag", "15 to 8", "0001 1010", ""], ["index", "7 to 4", "0111", ""], ["offset", "3 to 0", "1100", ""]]},
    # lookup
    {"id": "lines", "type": "table", "region": "left", "columns": ["line", "valid", "tag", "data (16 bytes)"], "rows": [
        [5, 0, "", ""], [6, 0, "", ""], [7, 0, "", ""], [8, 0, "", ""], [9, 0, "", ""]]},
    {"id": "lookup", "type": "diagram", "region": "right", "layout": "layers", "direction": "down", "nodes": [
        {"id": "addr", "label": "0x1A7C"},
        {"id": "idx", "label": "line 7"},
        {"id": "cmp", "label": "valid and tag = 26?"},
        {"id": "hit", "label": "hit: byte 12", "shape": "pill"},
        {"id": "miss", "label": "miss: fetch 423", "shape": "pill"}],
     "edges": [{"from": "addr", "to": "idx"}, {"from": "idx", "to": "cmp"},
               {"from": "cmp", "to": "hit", "label": "yes"}, {"from": "cmp", "to": "miss", "label": "no"}]},
    # 2-way and fully associative
    {"id": "cmp3", "type": "table", "region": "center", "columns": ["mapping", "sets", "index bits", "tag bits", "offset bits", "0x1A7C goes to", "tag stored"], "rows": [
        ["direct-mapped", 16, 4, 8, 4, "line 7", 26],
        ["2-way", 8, "", "", 4, "", ""],
        ["fully assoc.", 1, "", "", 4, "", ""]]},
    {"id": "math2", "type": "math", "region": "bottom", "lines": [
        "\"2-way index\" = log_2(8) = 3 quad \"tag\" = 16 - 3 - 4 = 9",
        "\"fully associative index\" = log_2(1) = 0 quad \"tag\" = 16 - 0 - 4 = 12"]},
    # conflict
    {"id": "trace", "type": "table", "region": "center", "columns": ["access", "address", "block", "direct: line", "direct", "2-way: set", "2-way"], "rows": [
        [1, "0x1A7C", "", "", "", "", ""],
        [2, "0x2A70", "", "", "", "", ""],
        [3, "0x1A7C", "", "", "", "", ""],
        [4, "0x2A70", "", "", "", "", ""]]},
    # trade-offs
    {"id": "trade", "type": "table", "region": "center", "columns": ["", "direct-mapped", "2-way", "fully associative"], "rows": [
        ["tag comparators per lookup", "1", "2", "16 (all lines)"],
        ["conflict misses", "most", "fewer", "none"],
        ["hit time", "fastest", "a little slower", "slowest"],
        ["tag bits per line", "8", "9", "12"]]},
]

S = []  # scenes


def flat(d):
    out = []
    for a in d:
        out.extend(a if isinstance(a, list) else [a])
    return out


def scene(id, steps):
    S.append({"id": id, "steps": [{"say": {"en": s}, **({"do": flat(d)} if d else {})} for s, d in steps]})


def head(t):
    return {"action": "replace", "target": "head", "text": t}


_take = {"shown": False}


def take(t):
    if _take["shown"]:
        return {"action": "replace", "target": "takeaway", "text": t}
    _take["shown"] = True
    return [{"action": "write", "target": "takeaway"}, {"action": "replace", "target": "takeaway", "text": t}]


def untake():
    _take["shown"] = False
    return {"action": "hide", "target": "takeaway"}


scene("intro", [
    ("Every time the processor reads memory, the cache answers first.", [{"action": "write", "target": "head"}]),
    ("To do that, every cache must answer four questions.", [{"action": "show", "target": "four"}]),
    ("Question one, placement: where can a block be placed in the cache?", [{"action": "highlight", "target": "four[0]"}]),
    ("Question two, identification: how do we find a block if it is there?", [{"action": "highlight", "target": "four[1]"}]),
    ("Question three, replacement: on a miss, which block do we throw out?", [{"action": "highlight", "target": "four[2]"}]),
    ("Question four, write strategy: what happens when the processor writes?", [{"action": "highlight", "target": "four[3]"}]),
    ("This video answers the first two; replacement and writes get their own videos next.", [{"action": "mark", "target": "four[0..=1]"}, {"action": "dim", "target": "four[2..=3]", "delay": 0.5}]),
    ("Here is the plan, in seven stages, with one worked example all the way through.", [{"action": "hide", "target": "four"}, {"action": "show", "target": "stages"}]),
    ("We start with the four questions, then fix one small cache in numbers.", [{"action": "highlight", "target": "stages[0..=1]"}]),
    ("Then placement, splitting an address, and finding a block by its tag.", [{"action": "highlight", "target": "stages[2..=4]"}]),
    ("Finally the same address in other mappings, and a conflict that shows why associativity helps.", [{"action": "highlight", "target": "stages[5..=6]"}]),
])

scene("numbers", [
    ("Stage 2: our example cache.", [head("Stage 2 of 7: our example cache"), {"action": "hide", "target": "stages"}, {"action": "show", "target": "spec"}]),
    ("Addresses are 16 bits long, and every byte has its own address.", [{"action": "highlight", "target": "spec[0..=1]"}]),
    ("The cache holds 256 bytes, moved in blocks of 16 bytes.", [{"action": "highlight", "target": "spec[2..=3]"}]),
    ("A block is the unit the cache copies from memory, never a single byte.", [{"action": "highlight", "target": "spec[3]"}]),
    ("First question: how many blocks fit in the cache?", [{"action": "show", "target": "calc"}]),
    ("Divide the cache size by the block size.", [{"action": "highlight", "target": "calc[0]"}]),
    ("256 divided by 16 is 16, so the cache has 16 lines, each holding one block.", [{"action": "reveal", "target": "calc[1]"}, {"action": "highlight", "target": "calc[1]"}]),
    ("Memory is split into blocks the same way: the block number is the address divided by 16, rounded down.", [{"action": "reveal", "target": "calc[2]"}, {"action": "highlight", "target": "calc[2]"}]),
    ("And the remainder, the offset, says which byte inside the block we want.", [{"action": "reveal", "target": "calc[3]"}, {"action": "highlight", "target": "calc[3]"}]),
    ("Keep these numbers: 16 lines, 16 bytes per block, 16 bit addresses.", [take("16 lines · 16-byte blocks · 16-bit addresses")]),
])

scene("placement", [
    ("Stage 3, question one: where can a block be placed?", [head("Stage 3 of 7: Q1 placement"), {"action": "hide", "target": "spec"}, {"action": "hide", "target": "calc"}, {"action": "show", "target": "place"}]),
    ("In a direct-mapped cache, each block has exactly one line it may use.", [{"action": "highlight", "target": "place[0]"}]),
    ("That line is the block number mod 16, the number of lines.", [{"action": "highlight", "target": "place[0][2]"}]),
    ("In a set-associative cache, lines are grouped into sets, and a block may use any line of one set.", [{"action": "highlight", "target": "place[1]"}]),
    ("With two lines per set, we call it two-way set-associative.", [{"action": "highlight", "target": "place[1][0]"}]),
    ("In a fully associative cache, a block may go in any line at all.", [{"action": "highlight", "target": "place[2]"}]),
    ("All three are the same idea: the number of sets is the number of blocks divided by the number of ways.", [{"action": "show", "target": "placemath"}]),
    ("Direct-mapped is one way: 16 divided by 1 gives 16 sets of one line.", [{"action": "reveal", "target": "placemath[1]"}, {"action": "highlight", "target": "placemath[1]"}]),
    ("Two-way: 16 divided by 2 gives 8 sets, so the rule is block mod 8.", [{"action": "reveal", "target": "placemath[2]"}, {"action": "highlight", "target": "placemath[2]"}, {"action": "highlight", "target": "place[1][2]", "delay": 0.5}]),
    ("Fully associative: 16 ways, so there is just one set, and no rule to follow.", [{"action": "reveal", "target": "placemath[3]"}, {"action": "highlight", "target": "placemath[3]"}]),
    ("So direct-mapped and fully associative are just the two ends of set-associative.", [take("direct-mapped = 1-way · fully associative = one set with every line")]),
])

scene("split", [
    ("Stage 4: the cache finds the set from the address bits themselves, so we split the address.", [head("Stage 4 of 7: splitting an address (direct-mapped)"), {"action": "hide", "target": "place"}, {"action": "hide", "target": "placemath"}, {"action": "show", "target": "split"}]),
    ("The lowest bits are the offset: they pick a byte inside the block.", [{"action": "highlight", "target": "split[0]"}]),
    ("A block has 16 bytes, and log base 2 of 16 is 4, so the offset is 4 bits.", [{"action": "highlight", "target": "split[0]"}]),
    ("The next bits are the index: they pick the set.", [{"action": "reveal", "target": "split[1]"}, {"action": "highlight", "target": "split[1]"}]),
    ("Direct-mapped has 16 sets, and log base 2 of 16 is 4, so the index is 4 bits.", [{"action": "highlight", "target": "split[1]"}]),
    ("Whatever is left over is the tag: 16 minus 4 minus 4 leaves 8 bits.", [{"action": "reveal", "target": "split[2]"}, {"action": "highlight", "target": "split[2]"}]),
    ("Check: 8 plus 4 plus 4 must give back all 16 address bits.", [{"action": "reveal", "target": "split[3]"}, {"action": "highlight", "target": "split[3]"}]),
    ("Now take one address, hex 1A7C, and write it in binary, four bits per hex digit.", [{"action": "hide", "target": "split"}, {"action": "hide", "target": "head"}, {"action": "show", "target": "hex"}, {"action": "show", "target": "bits", "delay": 0.4}, take("tag 8 · index 4 · offset 4")]),
    ("1 is 0001, A is 1010, 7 is 0111, and C is 1100.", [{"action": "highlight", "target": "bits[0..=15]"}]),
    ("The top 8 bits are the tag.", [{"action": "highlight", "target": "bits[0..=7]"}, {"action": "show", "target": "p_tag"}]),
    ("The next 4 bits are the index.", [{"action": "highlight", "target": "bits[8..=11]"}, {"action": "show", "target": "p_idx"}]),
    ("And the lowest 4 bits are the offset.", [{"action": "highlight", "target": "bits[12..=15]"}, {"action": "show", "target": "p_off"}]),
    ("Now read each field as a number.", [untake(), {"action": "show", "target": "fields"}]),
    ("The offset 1100 is 8 plus 4, which is 12: byte 12 of the block.", [{"action": "highlight", "target": "fields[2]"}, {"action": "set", "target": "fields[2][3]", "value": "12"}]),
    ("The index 0111 is 4 plus 2 plus 1, which is 7: line 7.", [{"action": "highlight", "target": "fields[1]"}, {"action": "set", "target": "fields[1][3]", "value": "7"}]),
    ("The tag 0001 1010 is 16 plus 8 plus 2, which is 26.", [{"action": "highlight", "target": "fields[0]"}, {"action": "set", "target": "fields[0][3]", "value": "26"}]),
    ("Check with arithmetic: the block number is 6780 divided by 16, which is 423, and 423 mod 16 is 7.", [{"action": "mark", "target": "fields[1]"}]),
    ("So the index really is the block number mod 16, read straight from the bits.", [{"action": "mark", "target": "fields[0..=2]"}]),
])

scene("identify", [
    ("Stage 5, question two: how does the cache know the block in line 7 is ours?", [{"action": "hide", "target": "hex"}, {"action": "hide", "target": "bits"}, {"action": "hide", "target": "fields"}, {"action": "write", "target": "head"}, head("Stage 5 of 7: Q2 identification"), {"action": "show", "target": "lines"}]),
    ("Many blocks share line 7: every block whose number mod 16 is 7.", [{"action": "highlight", "target": "lines[2]"}]),
    ("So each line stores a tag, the part of the address the index did not use.", [{"action": "highlight", "target": "lines.tag"}]),
    ("It also stores a valid bit, which says whether the line holds anything real at all.", [{"action": "highlight", "target": "lines.valid"}]),
    ("At power on, every valid bit is 0, so every lookup misses.", [{"action": "highlight", "target": "lines.valid"}]),
    ("Here is the lookup for 0x1A7C.", [{"action": "show", "target": "lookup"}, {"action": "highlight", "target": "lookup.addr"}]),
    ("The index, 7, takes us straight to line 7, with no searching.", [{"action": "highlight", "target": "lookup.idx"}, {"action": "highlight", "target": "lines[2]", "delay": 0.4}]),
    ("Then one comparison: is the valid bit 1, and is the stored tag equal to 26?", [{"action": "highlight", "target": "lookup.cmp"}]),
    ("Line 7 is not valid yet, so this is a miss.", [{"action": "highlight", "target": "lookup.miss"}]),
    ("The cache fetches block 423 from memory, sets valid to 1, and stores tag 26.", [{"action": "set", "target": "lines[2][1]", "value": "1"}, {"action": "set", "target": "lines[2][2]", "value": "26", "delay": 0.3}, {"action": "set", "target": "lines[2][3]", "value": "block 423", "delay": 0.6}]),
    ("The next read of 0x1A7C finds valid 1 and tag 26, so it is a hit, and byte 12 is returned.", [{"action": "highlight", "target": "lookup.hit"}, {"action": "mark", "target": "lines[2]"}]),
    ("Notice the offset is never compared: it only picks the byte after a hit.", [take("index finds the line · tag + valid bit confirm it · offset picks the byte")]),
])

scene("other-mappings", [
    ("Stage 6: the same address in a two-way and a fully associative cache.", [head("Stage 6 of 7: the same address, other mappings"), {"action": "hide", "target": "lines"}, {"action": "hide", "target": "lookup"}, untake(), {"action": "show", "target": "cmp3"}]),
    ("Direct-mapped, from before: 16 sets, index 4 bits, tag 8 bits, line 7, tag 26.", [{"action": "highlight", "target": "cmp3[0]"}]),
    ("Two-way has 8 sets, so the index is log base 2 of 8, which is 3 bits.", [{"action": "show", "target": "math2"}, {"action": "set", "target": "cmp3[1][2]", "value": "3"}]),
    ("The tag grows by one bit: 16 minus 3 minus 4 is 9.", [{"action": "set", "target": "cmp3[1][3]", "value": "9"}]),
    ("The set is block 423 mod 8: 8 times 52 is 416, leaving 7, so set 7.", [{"action": "set", "target": "cmp3[1][5]", "value": "set 7, either way"}]),
    ("The tag is the top 9 bits, which is 423 divided by 8, rounded down: 52.", [{"action": "set", "target": "cmp3[1][6]", "value": "52"}]),
    ("Fully associative has one set, so the index is log base 2 of 1, which is zero bits.", [{"action": "reveal", "target": "math2[1]"}, {"action": "set", "target": "cmp3[2][2]", "value": "0"}]),
    ("Everything above the offset is tag: 16 minus 4 gives 12 bits.", [{"action": "set", "target": "cmp3[2][3]", "value": "12"}]),
    ("The block may go in any line, and the stored tag is the whole block number, 423.", [{"action": "set", "target": "cmp3[2][5]", "value": "any line"}, {"action": "set", "target": "cmp3[2][6]", "value": "423"}]),
    ("Check the pattern: each time the ways double, the index loses a bit and the tag gains one.", [{"action": "highlight", "target": "cmp3.c2"}, {"action": "highlight", "target": "cmp3.c3", "delay": 0.4}]),
    ("The offset never changes, because the block size did not change.", [{"action": "highlight", "target": "cmp3.c4"}]),
])

scene("conflict", [
    ("Stage 7: why pay for associativity? Watch two addresses fight over one line.", [head("Stage 7 of 7: a conflict"), {"action": "hide", "target": "cmp3"}, {"action": "hide", "target": "math2"}, {"action": "show", "target": "trace"}]),
    ("The processor reads 0x1A7C, then 0x2A70, then each again.", [{"action": "highlight", "target": "trace.address"}]),
    ("0x1A7C is block 423, as we found.", [{"action": "set", "target": "trace[0][2]", "value": "423"}, {"action": "set", "target": "trace[2][2]", "value": "423"}]),
    ("0x2A70 is 10864, and 10864 divided by 16 is block 679.", [{"action": "set", "target": "trace[1][2]", "value": "679"}, {"action": "set", "target": "trace[3][2]", "value": "679"}]),
    ("Direct-mapped: 423 mod 16 is 7, and 679 mod 16 is also 7.", [{"action": "set", "target": "trace[0][3]", "value": "7"}, {"action": "set", "target": "trace[1][3]", "value": "7"}, {"action": "set", "target": "trace[2][3]", "value": "7"}, {"action": "set", "target": "trace[3][3]", "value": "7"}]),
    ("Access one misses, and line 7 gets block 423.", [{"action": "highlight", "target": "trace[0]"}, {"action": "set", "target": "trace[0][4]", "value": "miss"}]),
    ("Access two also needs line 7, so it misses and throws block 423 out.", [{"action": "highlight", "target": "trace[1]"}, {"action": "set", "target": "trace[1][4]", "value": "miss"}]),
    ("Access three wants 423 back: miss again, and 679 is thrown out.", [{"action": "highlight", "target": "trace[2]"}, {"action": "set", "target": "trace[2][4]", "value": "miss"}]),
    ("Access four misses too: four accesses, four misses, while the other 15 lines sit empty.", [{"action": "highlight", "target": "trace[3]"}, {"action": "set", "target": "trace[3][4]", "value": "miss"}, {"action": "mark", "target": "trace.c4", "delay": 0.5}]),
    ("These are conflict misses: the cache had room, but the mapping forced both blocks into one line.", [take("conflict miss: room in the cache, but two blocks map to the same line")]),
    ("Now two-way: 423 mod 8 is 7, and 679 mod 8 is also 7, the same set.", [{"action": "set", "target": "trace[0][5]", "value": "7"}, {"action": "set", "target": "trace[1][5]", "value": "7"}, {"action": "set", "target": "trace[2][5]", "value": "7"}, {"action": "set", "target": "trace[3][5]", "value": "7"}]),
    ("But set 7 has two ways, so access one misses into way 0, and access two misses into way 1.", [{"action": "set", "target": "trace[0][6]", "value": "miss"}, {"action": "set", "target": "trace[1][6]", "value": "miss", "delay": 0.5}]),
    ("Both blocks now live side by side, so accesses three and four hit.", [{"action": "set", "target": "trace[2][6]", "value": "hit"}, {"action": "set", "target": "trace[3][6]", "value": "hit", "delay": 0.4}, {"action": "mark", "target": "trace.c6", "delay": 0.6}]),
    ("Check: direct-mapped scored 0 hits out of 4, two-way scored 2 out of 4.", [{"action": "highlight", "target": "trace.c4"}, {"action": "highlight", "target": "trace.c6", "delay": 0.5}]),
])

scene("tradeoffs", [
    ("So why not always use fully associative? Because every way costs hardware and time.", [head("The trade-off"), {"action": "hide", "target": "trace"}, untake(), {"action": "show", "target": "trade"}]),
    ("Direct-mapped compares one tag per lookup; two-way compares two at once; fully associative compares all 16.", [{"action": "highlight", "target": "trade[0]"}]),
    ("More ways means fewer conflict misses.", [{"action": "highlight", "target": "trade[1]"}]),
    ("But more comparators and a final choice between ways make the hit time longer.", [{"action": "highlight", "target": "trade[2]"}]),
    ("And every line stores a longer tag: 8, 9, then 12 bits in our cache.", [{"action": "highlight", "target": "trade[3]"}]),
    ("That is why real first-level caches are usually 2 to 8 way set-associative: a balance between the two ends.", [take("real L1 caches: 2-way to 8-way set-associative")]),
])

scene("recap", [
    ("Let us walk the stages once more.", [head("Recap"), {"action": "hide", "target": "trade"}, untake(), {"action": "show", "target": "stages"}]),
    ("Four questions: placement, identification, replacement and write strategy.", [{"action": "highlight", "target": "stages[0]"}]),
    ("Lines equal cache size over block size; sets equal lines over ways.", [{"action": "highlight", "target": "stages[1..=2]"}]),
    ("Offset bits are log of the block size, index bits are log of the sets, and the tag is what is left.", [{"action": "highlight", "target": "stages[3]"}]),
    ("The index finds the set, the valid bit and tag confirm the block, and the offset picks the byte.", [{"action": "highlight", "target": "stages[4]"}]),
    ("More ways: fewer index bits, longer tags, fewer conflict misses, but a slower hit.", [{"action": "highlight", "target": "stages[5..=6]"}]),
    ("Next video: question three, which block to throw out, with LRU, FIFO and random.", [{"action": "mark", "target": "stages[0..=6]"}, take("Next: Q3 replacement — LRU, FIFO, random")]),
])

script = {"version": 1, "title": "Cache basics: placement, mapping and finding a block",
          "canvas": {"width": 1920, "height": 1080, "fps": 30, "theme": "dark"},
          "objects": objects, "scenes": S}
json.dump(script, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
print(sum(len(s["steps"]) for s in S), "steps")
