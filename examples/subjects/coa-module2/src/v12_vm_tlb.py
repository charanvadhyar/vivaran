"""Module 2, video 12: virtual memory, page tables and the TLB."""
import sys
sys.path.insert(0, "/home/claude/playlist")
from common import Script

r = lambda x, n=2: round(x, n)
# translation example
va = 0x00403ABC
assert va >> 12 == 0x403 and va & 0xFFF == 0xABC and (0x1F2 << 12) | 0xABC == 0x1F2ABC
# page table size
assert (1 << 20) * 4 == 4 << 20
# x86-64
assert 9 * 4 + 12 == 48
# EAT
assert r(0.98 * 101 + 0.02 * 201) == 103.0 and r(0.98 * 101 + 0.02 * 501) == 109.0
# TLB reach
assert 64 * 4 == 256 and 64 * 2 == 128
# exam
assert 32 - 12 == 20 and (1 << 30) >> 12 == 1 << 18
assert r(0.95 * (2 + 50) + 0.05 * (2 + 100 + 50)) == 57.0
assert 0x00005A3C >> 12 == 5 and (0x2A << 12) | 0xA3C == 0x2AA3C

s = Script("Virtual memory and the TLB")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Why virtual memory"],
    [2, "Pages and the page table"],
    [3, "Translating an address, step by step"],
    [4, "Multilevel page tables"],
    [5, "The TLB: a cache for translations"],
    [6, "Effective access time and TLB reach"],
    [7, "Protection and process switches"],
    [8, "Exam question"]]})
s.obj({"id": "why", "type": "table", "region": "center", "columns": ["what it gives", "how"], "rows": [
    ["each program its own address space", "addresses start at 0, as if it owned the machine"],
    ["protection", "one process cannot read or write another's memory"],
    ["more memory than RAM", "pages not in use wait on disk, loaded on demand"],
    ["easy loading and sharing", "any page in any frame; frames can be shared"]]})
s.obj({"id": "va", "type": "timeline", "region": "center", "lanes": ["virtual address", "physical address"], "end": 32, "unit": "bit", "now": 0, "blocks": []})
s.obj({"id": "ptm", "type": "math", "region": "center", "lines": [
    "\"32-bit address, 4 KB pages:\" quad \"offset\" = log_2 4096 = 12 \"bits\" quad \"VPN\" = 32 - 12 = 20 \"bits\"",
    "\"page table:\" quad 2^20 \"entries\" times 4 \"B\" = 4 \"MB per process\""]})
s.obj({"id": "pte", "type": "table", "region": "center", "columns": ["page table entry field", "meaning"], "rows": [
    ["frame number (PFN)", "where the page sits in physical memory"],
    ["valid", "1: in memory · 0: on disk, a page fault"],
    ["dirty", "written since loaded: must be saved before eviction"],
    ["reference", "used recently: helps the OS approximate LRU"],
    ["protection", "read, write, execute; user or kernel only"]]})
s.obj({"id": "pt", "type": "table", "region": "right", "columns": ["VPN", "valid", "PFN"], "rows": [
    ["0x00401", "1", "0x0A7"], ["0x00402", "0", "disk"], ["0x00403", "1", "0x1F2"], ["0x00404", "1", "0x035"]]})
s.obj({"id": "tr", "type": "table", "region": "left", "columns": ["step", "value"], "rows": [
    ["virtual address", "0x00403ABC"], ["VPN (top 20 bits)", ""], ["offset (low 12 bits)", ""], ["PFN from the table", ""], ["physical address", ""]]})
s.obj({"id": "ml", "type": "table", "region": "center", "columns": ["level", "bits of the address", "picks"], "rows": [
    ["1", "47 to 39 (9 bits)", "one of 512 entries in the top table"],
    ["2", "38 to 30 (9 bits)", "an entry in a second-level table"],
    ["3", "29 to 21 (9 bits)", "an entry in a third-level table"],
    ["4", "20 to 12 (9 bits)", "the page table entry: the PFN"],
    ["offset", "11 to 0 (12 bits)", "the byte inside the 4 KB page"]]})
s.obj({"id": "mlm", "type": "math", "region": "bottom", "lines": [
    "9 + 9 + 9 + 9 + 12 = 48 \"bits\" quad \"a miss in the TLB costs 4 memory reads\""]})
s.obj({"id": "tlb", "type": "table", "region": "left", "columns": ["TLB: VPN", "PFN", "valid"], "rows": [
    ["0x00401", "0x0A7", "1"], ["0x00403", "0x1F2", "1"], ["0x7FFF0", "0x2C0", "1"], ["", "", "0"]]})
s.obj({"id": "tlbx", "type": "table", "region": "right", "columns": ["lookup", "result"], "rows": [
    ["VPN 0x00403", ""], ["VPN 0x00404", ""]]})
s.obj({"id": "tlbt", "type": "table", "region": "center", "columns": ["typical TLB", "value"], "rows": [
    ["entries", "16 to 512 for L1, a few thousand for L2"],
    ["organization", "fully associative or highly set-associative"],
    ["hit time", "under 1 cycle, in parallel with the L1 cache index"],
    ["hit rate", "usually over 99%"]]})
s.obj({"id": "eat", "type": "math", "region": "center", "lines": [
    "\"TLB 1 ns, memory 100 ns, TLB hit rate 98%\"",
    "\"hit:\" quad 1 + 100 = 101 \"ns\" quad \"miss, 1-level table:\" quad 1 + 100 + 100 = 201 \"ns\"",
    "\"EAT\" = 0.98 times 101 + 0.02 times 201 = 103 \"ns\"",
    "\"4-level table:\" quad 0.98 times 101 + 0.02 times (1 + 400 + 100) = 109 \"ns\"",
    "\"TLB reach\" = \"entries\" times \"page size:\" quad 64 times 4 \"KB\" = 256 \"KB\" quad 64 times 2 \"MB\" = 128 \"MB\""]})
s.obj({"id": "pr", "type": "table", "region": "center", "columns": ["problem", "solution"], "rows": [
    ["a user program writes to kernel memory", "user/kernel bit in each entry: the access traps"],
    ["code overwritten by a bug, data run as code", "read, write, execute bits per page"],
    ["process switch: old translations in the TLB", "flush the TLB, or tag entries with a process ID (ASID)"],
    ["the page is not in memory", "valid = 0: page fault, the OS loads it from disk"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["given", "find"], "rows": [
    ["32-bit virtual addresses, 4 KB pages, 1 GB physical memory", "a) offset, VPN and PFN bits"],
    ["4-byte page table entries, one-level table", "b) the page table size"],
    ["TLB 2 ns, hit rate 95%; memory 50 ns; two-level table", "c) the effective access time"],
    ["page table: VPN 5 → PFN 0x2A", "d) the physical address of 0x00005A3C"]]})
s.obj({"id": "qa", "type": "math", "region": "center", "lines": [
    "\"a)\" quad \"offset\" = 12 quad \"VPN\" = 32 - 12 = 20 quad \"PFN\" = log_2 (2^30 / 2^12) = 18 \"bits\"",
    "\"b)\" quad 2^20 times 4 \"B\" = 4 \"MB\"",
    "\"c)\" quad 0.95 times (2 + 50) + 0.05 times (2 + 2 times 50 + 50) = 49.4 + 7.6 = 57 \"ns\"",
    "\"d)\" quad \"VPN\" = 5 , \"offset\" = \"A3C\" quad -> quad \"2A\" | \"A3C\" = \"0x2AA3C\""]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
st = lambda t, v, d=0: {"action": "set", "target": t, "value": v, **({"delay": d} if d else {})}
rv = lambda t, i: [{"action": "reveal", "target": f"{t}[{i}]"}, hl(f"{t}[{i}]")]
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]


def blk(id, lane, a, b, label, d=0):
    return {"action": "add_block", "target": "va", "id": id, "lane": lane, "start": a, "end": b, "label": label, **({"delay": d} if d else {})}


# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("Every address a program uses is a lie. It is a virtual address, and the hardware translates it, on every single load and store. This video shows how, and how the TLB makes it fast.", [s.head("Virtual memory and the TLB")])
s.step("Here are the eight stages.", show("stages"))
s.step("Why we want it, how pages and page tables work, and a translation done by hand.", [hl("stages[0..=3]")])
s.step("Then the TLB, the effective access time, protection, and an exam question.", [hl("stages[4..=7]")])

# ---------------------------------------------------------------- why
s.scene("why")
s.step("Stage 1: why virtual memory?", [s.head("Stage 1 of 8: why virtual memory")] + hide("stages") + show("why"))
s.step("Each program gets its own address space starting at 0, as if it owned the whole machine. The compiler and linker never need to know where it will really sit.", [hl("why[0]")])
s.step("Protection: one process simply has no address that reaches another's memory.", [hl("why[1]")])
s.step("Programs can be bigger than RAM. Pages not in use wait on disk, and are loaded only when touched.", [hl("why[2]")])
s.step("And any page can go into any free frame, so loading is easy, and two processes can share a frame, like a shared library.", [hl("why[3]"), s.take("main memory acts as a cache for the disk")])

# ---------------------------------------------------------------- pages
s.scene("pages")
s.step("Stage 2: memory is split into fixed-size pages, typically 4 kilobytes. Physical memory is split into frames of the same size.", [s.head("Stage 2 of 8: pages and the page table"), s.untake()] + hide("why") + show("va"))
s.step("A 32-bit virtual address splits in two. The low 12 bits are the offset inside the page, because 2 to the 12 is 4096.", [blk("o1", "virtual address", 0, 12, "offset: bits 11 to 0")])
s.step("The top 20 bits are the virtual page number, the VPN.", [blk("v1", "virtual address", 12, 32, "VPN: bits 31 to 12 (20 bits)")])
s.step("Translation replaces the VPN with a physical frame number, the PFN. The offset is copied unchanged.", [blk("o2", "physical address", 0, 12, "offset: copied"), blk("p2", "physical address", 12, 32, "PFN: from the page table", 0.4)])
s.step("The page table holds one entry per virtual page. 20 bits of VPN means 2 to the 20 entries, about a million. At 4 bytes each, 4 megabytes, for every process.", hide("va") + show("ptm") + [hl("ptm[0]")] + rv("ptm", 1))
s.step("What is in an entry? First, the frame number.", hide("ptm") + show("pte") + [hl("pte[0]")])
s.step("A valid bit. If it is 0, the page is on disk, and touching it causes a page fault.", [hl("pte[1]")])
s.step("A dirty bit, set on a write, so the OS knows the page must be saved before it is evicted. Virtual memory is always write-back.", [hl("pte[2]")])
s.step("A reference bit, that the OS clears and checks to approximate LRU. And protection bits.", [hl("pte[3]"), hl("pte[4]", 0.4), s.take("page table entry: PFN, valid, dirty, reference, protection")])

# ---------------------------------------------------------------- translate
s.scene("translate")
s.step("Stage 3: a translation by hand. The program loads from virtual address hex 0 0 4 0 3 A B C.", [s.head("Stage 3 of 8: translating an address"), s.untake()] + hide("pte") + show("tr", "pt") + [hl("tr[0]")])
s.step("The low 12 bits, three hex digits, are the offset: A B C.", [st("tr[2][1]", "0xABC"), hl("tr[2]", 0.3)])
s.step("The rest is the VPN: hex 0 0 4 0 3.", [st("tr[1][1]", "0x00403"), hl("tr[1]", 0.3)])
s.step("The hardware indexes the page table with the VPN. Entry 4 0 3 is valid, and holds frame hex 1 F 2.", [hl("pt[2]"), st("tr[3][1]", "0x1F2", 0.5)])
s.step("Put the frame number in front of the unchanged offset: hex 1 F 2 A B C. That is the physical address sent to the cache.", [st("tr[4][1]", "0x1F2ABC"), mk("tr[4]", 0.3)])
s.step("Had the program touched page 4 0 2, the valid bit would be 0: a page fault. The OS loads the page from disk, updates the entry, and restarts the instruction.", [hl("pt[1]"), s.take("physical address = PFN followed by the same offset")])

# ---------------------------------------------------------------- multilevel
s.scene("multilevel")
s.step("Stage 4: 4 megabytes per process is too much, and a 64-bit address would need far more. The fix is a multilevel page table.", [s.head("Stage 4 of 8: multilevel page tables"), s.untake()] + hide("tr", "pt") + show("ml"))
s.step("x86-64 uses 48-bit virtual addresses and four levels. Each level uses 9 bits, picking one of 512 entries.", [hl("ml[0..=3]")])
s.step("Level 1 points to a level 2 table, which points to level 3, then level 4, whose entry holds the frame number.", [hl("ml[0]"), hl("ml[1]", 0.25), hl("ml[2]", 0.5), hl("ml[3]", 0.75)])
s.step("The low 12 bits stay the offset. 9 times 4 plus 12 is 48.", [hl("ml[4]")] + show("mlm") + [hl("mlm[0]")])
s.step("The win: tables are created only for the parts of the address space a program uses. A small program needs a handful of 4 kilobyte tables, not megabytes.", [mk("ml[0..=3]")])
s.step("The cost: one translation now takes 4 memory reads, a page walk, before the real access. Without help, every load would be five times slower.", [s.take("multilevel: small tables, but a 4-read page walk")])

# ---------------------------------------------------------------- TLB
s.scene("tlb")
s.step("Stage 5: the help is the TLB, the translation lookaside buffer. It is a small cache that holds recent translations.", [s.head("Stage 5 of 8: the TLB"), s.untake()] + hide("ml", "mlm") + show("tlb", "tlbx"))
s.step("Each entry holds a VPN as its tag, the frame number, and the valid, dirty and protection bits copied from the page table.", [hl("tlb[0..=2]")])
s.step("Lookup VPN hex 0 0 4 0 3. All entries are compared at once. Entry 2 matches: a TLB hit, and the frame number comes out within the cycle.", [hl("tlbx[0]"), hl("tlb[1]", 0.3), st("tlbx[0][1]", "hit: PFN 0x1F2", 0.6)])
s.step("Lookup VPN hex 0 0 4 0 4. No entry matches: a TLB miss.", [hl("tlbx[1]"), st("tlbx[1][1]", "miss", 0.4)])
s.step("The page table is walked, in hardware on x86 and ARM, finding frame hex 0 3 5. The translation goes into a free TLB entry, and the access is retried.", [st("tlb[3][0]", "0x00404"), st("tlb[3][1]", "0x035", 0.3), st("tlb[3][2]", "1", 0.5), mk("tlb[3]", 0.6), st("tlbx[1][1]", "miss → walk → filled", 0.6)])
s.step("Why does a tiny TLB work? Locality again: one entry covers a whole 4 kilobyte page, so a loop touches the same few pages over and over.", hide("tlb", "tlbx") + show("tlbt") + [hl("tlbt[0]")])
s.step("TLBs are small and highly associative, so conflicts are rare.", [hl("tlbt[1]")])
s.step("The lookup runs in parallel with the L1 cache index, the VIPT trick from the previous videos, so a hit adds no time at all.", [hl("tlbt[2]")])
s.step("And hit rates are usually above 99 percent.", [hl("tlbt[3]"), s.take("TLB: a cache of page table entries")])

# ---------------------------------------------------------------- EAT
s.scene("eat")
s.step("Stage 6: putting numbers on it. The TLB takes 1 nanosecond, memory 100, and the TLB hit rate is 98 percent.", [s.head("Stage 6 of 8: effective access time"), s.untake()] + hide("tlbt") + show("eat") + [hl("eat[0]")])
s.step("A TLB hit costs 1 plus 100: 101 nanoseconds. A miss with a one-level table adds a page table read: 201.", rv("eat", 1))
s.step("Effective access time: 0.98 times 101, plus 0.02 times 201. 103 nanoseconds, only 3 percent above perfect.", rv("eat", 2))
s.step("With a 4-level table, a miss costs 1 plus 400 plus 100. The average rises to 109 nanoseconds. Still fine, because misses are rare.", rv("eat", 3))
s.step("TLB reach is how much memory the TLB covers: entries times page size. 64 entries of 4 kilobytes cover only 256 kilobytes. With 2 megabyte huge pages, 128 megabytes.", rv("eat", 4) + [s.take("EAT = h × (TLB + mem) + (1 − h) × (TLB + walk + mem)")])

# ---------------------------------------------------------------- protection
s.scene("protect")
s.step("Stage 7: protection, checked on every access by the same hardware.", [s.head("Stage 7 of 8: protection and process switches"), s.untake()] + hide("eat") + show("pr"))
s.step("A user/kernel bit in each entry: if a user program touches a kernel page, the access traps to the OS.", [hl("pr[0]")])
s.step("Read, write and execute bits per page stop a bug from overwriting code, or data from being run as code.", [hl("pr[1]")])
s.step("On a process switch, the TLB holds the old process's translations. Either flush it, or tag each entry with an address space ID, so entries of several processes can live side by side.", [hl("pr[2]")])
s.step("And a valid bit of 0 is a page fault, handled in software by the OS, as we counted in the replacement video.", [hl("pr[3]"), s.take("every access is translated and checked: TLB hit, walk, or fault")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("pr") + show("q"))
s.step("32-bit virtual addresses, 4 kilobyte pages, 1 gigabyte of physical memory, 4-byte page table entries.", [hl("q[0][0]"), hl("q[1][0]", 0.4)])
s.step("A TLB of 2 nanoseconds with a 95 percent hit rate, memory of 50 nanoseconds, and a two-level page table. The table maps page 5 to frame hex 2 A.", [hl("q[2][0]"), hl("q[3][0]", 0.4)])
s.step("Find the field widths, the page table size, the effective access time, and the physical address of hex 0 0 0 0 5 A 3 C. Pause and work it out.", [hl("q[0][1]"), hl("q[1][1]", 0.2), hl("q[2][1]", 0.4), hl("q[3][1]", 0.6)])
s.step("a: the offset is 12 bits, so the VPN is 20. 1 gigabyte is 2 to the 30 bytes, over 2 to the 12 per frame: 2 to the 18 frames, so the PFN is 18 bits.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("b: 2 to the 20 entries, times 4 bytes: 4 megabytes.", rv("qa", 1))
s.step("c: a hit costs 2 plus 50. A miss costs 2, plus two table reads of 50 each, plus the access: 152. 0.95 times 52, plus 0.05 times 152: 57 nanoseconds.", rv("qa", 2))
s.step("d: the VPN is 5 and the offset A 3 C. Frame hex 2 A followed by A 3 C gives hex 2 A A 3 C.", rv("qa", 3))
s.step("The usual slips: counting one page table read for a multilevel table, and changing the offset during translation. The offset never changes.", [s.take("a k-level table costs k reads on a TLB miss")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("Virtual memory gives each process its own pages. The page table maps each VPN to a frame, keeping the offset.", [hl("stages[0..=2]")])
s.step("Multilevel tables save space but need a walk. The TLB caches translations, so the walk is rare. And every access is checked for protection.", [hl("stages[3..=6]")])
s.step("Next video: virtual machines and hypervisors.", [mk("stages[0..=7]"), s.take("Next: virtual machines and hypervisors")])

s.save("/home/claude/playlist/m2v12.json")
