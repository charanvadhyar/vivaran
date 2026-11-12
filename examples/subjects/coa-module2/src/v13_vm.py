"""Module 2, video 13: virtual machines and hypervisors."""
import sys
sys.path.insert(0, "/home/claude/playlist")
from common import Script

walk = lambda g, h: (g + 1) * h + g
assert walk(4, 4) == 24 == (4 + 1) * (4 + 1) - 1 and walk(2, 3) == 11 == 3 * 4 - 1 and walk(4, 0) == 4
assert 10 * 0.8 + 10 * 0.2 * 5 == 18 and 10 * 0.8 + 10 * 0.2 * 1.5 == 11
assert 0.7 * 20 + 0.3 * 20 * 4 == 38 and round(38 / 20, 2) == 1.9 and 0.7 * 20 + 0.3 * 20 * 2 == 26

s = Script("Virtual machines and hypervisors")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "What a virtual machine is, and why we want one"],
    [2, "Type 1 and type 2 hypervisors"],
    [3, "Trap and emulate"],
    [4, "When an instruction set is hard to virtualize"],
    [5, "Virtualizing memory: two translations"],
    [6, "Virtualizing I/O"],
    [7, "The cost, in numbers"],
    [8, "Exam question"]]})
s.obj({"id": "vm", "type": "diagram", "region": "center", "layout": "layers", "direction": "down",
       "nodes": [
           {"id": "a1", "label": "app"}, {"id": "a2", "label": "app"},
           {"id": "a3", "label": "app"}, {"id": "a4", "label": "app"},
           {"id": "g1", "label": "guest: Linux"}, {"id": "g2", "label": "guest: Windows"},
           {"id": "vmm", "label": "hypervisor"},
           {"id": "hw", "label": "hardware"}],
       "edges": [
           {"from": "a1", "to": "g1"}, {"from": "a2", "to": "g1"}, {"from": "a3", "to": "g2"}, {"from": "a4", "to": "g2"},
           {"from": "g1", "to": "vmm"}, {"from": "g2", "to": "vmm"}, {"from": "vmm", "to": "hw"}]})
s.obj({"id": "why", "type": "table", "region": "center", "columns": ["why virtual machines", "what it means"], "rows": [
    ["isolation", "a crash or an attack inside one VM cannot touch another"],
    ["consolidation", "many lightly used servers share one machine"],
    ["managing software", "a whole OS with its apps is one file: copy, snapshot, restore"],
    ["migration", "a running VM can move to another machine"],
    ["the cloud", "rent a VM by the hour on someone else's hardware"]]})
s.obj({"id": "ty", "type": "table", "region": "center", "columns": ["", "type 1: bare metal", "type 2: hosted"], "rows": [
    ["runs on", "directly on the hardware", "as a program on a host OS"],
    ["examples", "VMware ESXi, Xen, Microsoft Hyper-V", "VirtualBox, VMware Workstation"],
    ["used for", "servers and the cloud", "desktops, testing"],
    ["overhead", "lower", "higher: every request passes the host OS too"]]})
s.obj({"id": "te", "type": "table", "region": "center", "columns": ["step", "who runs", "what happens"], "rows": [
    ["1", "guest app", "runs directly on the CPU at full speed"],
    ["2", "guest OS", "also runs directly, but in user mode, not kernel mode"],
    ["3", "guest OS", "executes a privileged instruction, say: disable interrupts"],
    ["4", "CPU", "user mode cannot do that: it traps"],
    ["5", "hypervisor", "emulates it for this VM only: its virtual interrupt flag"],
    ["6", "guest OS", "resumes, unaware anything happened"]]})
s.obj({"id": "pg", "type": "math", "region": "center", "lines": [
    "\"Popek and Goldberg (1974): trap and emulate works if\"",
    "\"every sensitive instruction is privileged\"",
    "\"sensitive: reads or changes machine state · privileged: traps in user mode\""]})
s.obj({"id": "x86", "type": "table", "region": "center", "columns": ["fix", "how", "used by"], "rows": [
    ["the problem", "POPF and others: sensitive, but no trap in user mode", "old x86"],
    ["binary translation", "rewrite the bad kernel instructions on the fly", "early VMware"],
    ["paravirtualization", "the guest OS calls the hypervisor: hypercalls", "Xen"],
    ["hardware support", "a new root mode; sensitive events trap", "Intel VT-x, AMD-V"]]})
s.obj({"id": "mm", "type": "table", "region": "center", "columns": ["address", "set by", "translated by"], "rows": [
    ["guest virtual", "the guest's programs", "the guest OS page table"],
    ["guest physical", "the guest OS: what it thinks is RAM", "the hypervisor's table"],
    ["host physical", "the real memory", ""]]})
s.obj({"id": "mx", "type": "table", "region": "center", "columns": ["method", "how", "cost"], "rows": [
    ["shadow page tables", "the hypervisor builds one combined table", "guest table writes must trap"],
    ["nested tables (EPT, NPT)", "the hardware walks both tables", "a long walk on a TLB miss"]]})
s.obj({"id": "nw", "type": "math", "region": "center", "lines": [
    "\"guest table: g levels · host table: h levels\"",
    "g + 1 \"guest-physical addresses, each needing a host walk of\" h \"reads\"",
    "\"references\" = (g + 1) h + g = (g + 1)(h + 1) - 1",
    "g = h = 4 : quad 5 times 5 - 1 = 24 \"memory references\" quad \"vs 4 natively\""]})
s.obj({"id": "io", "type": "table", "region": "center", "columns": ["I/O method", "how", "speed"], "rows": [
    ["emulated device", "the hypervisor pretends to be a common disk or network card", "slow: every register access traps"],
    ["paravirtual driver", "the guest uses a driver written for VMs, such as virtio", "faster: requests in batches"],
    ["direct assignment", "a real device given to one VM, made safe by an IOMMU", "near native"]]})
s.obj({"id": "cost", "type": "math", "region": "center", "lines": [
    "\"native: 10 s, of which 20% is OS work that traps when virtualized\"",
    "\"OS work 5 times slower:\" quad 8 + 2 times 5 = 18 \"s\" quad \"slowdown 1.8\"",
    "\"with hardware support, 1.5 times slower:\" quad 8 + 2 times 1.5 = 11 \"s\"",
    "\"a pure computation:\" quad \"almost no traps, almost native speed\""]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["given", "find"], "rows": [
    ["runs 20 s natively, 30% of it OS work", "a) VM time, OS work 4 × slower"],
    ["with hardware support", "b) VM time, OS work 2 × slower"],
    ["guest table 2 levels, host table 3 levels", "c) references per nested walk"],
    ["reads a privileged flag, no trap in user mode", "d) can trap and emulate work?"]]})
s.obj({"id": "qa", "type": "math", "region": "center", "lines": [
    "\"a)\" quad 14 + 6 times 4 = 38 \"s\" quad \"slowdown\" quad 38 / 20 = 1.9",
    "\"b)\" quad 14 + 6 times 2 = 26 \"s\"",
    "\"c)\" quad (2 + 1)(3 + 1) - 1 = 11 \"references\"",
    "\"d)\" quad \"no: it is sensitive but not privileged\""]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
rv = lambda t, i: [{"action": "reveal", "target": f"{t}[{i}]"}, hl(f"{t}[{i}]")]
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

# ---------------------------------------------------------------- intro
s.scene("intro")
s.step("One physical machine, running Linux and Windows at the same time, each convinced it owns the hardware. That is a virtual machine, and it is how the whole cloud works.", [s.head("Virtual machines and hypervisors")])
s.step("Here are the eight stages.", show("stages"))
s.step("What a VM is, the two kinds of hypervisor, and the trick that makes it work, trap and emulate.", [hl("stages[0..=3]")])
s.step("Then memory and I/O, the cost in numbers, and an exam question.", [hl("stages[4..=7]")])

# ---------------------------------------------------------------- what
s.scene("what")
s.step("Stage 1: the picture. At the bottom, the real hardware.", [s.head("Stage 1 of 8: what a virtual machine is")] + hide("stages") + show("vm") + [hl("vm.hw")])
s.step("On it runs the hypervisor, also called the virtual machine monitor. It owns the real hardware.", [hl("vm.vmm"), hl("vm.vmm->hw", 0.3)])
s.step("Above it, each virtual machine runs a complete guest OS, here Linux and Windows.", [hl("vm.g1"), hl("vm.g2", 0.3), hl("vm.g1->vmm", 0.5), hl("vm.g2->vmm", 0.6)])
s.step("And the guests run their applications, unchanged.", [hl("vm.a1"), hl("vm.a2", 0.2), hl("vm.a3", 0.4), hl("vm.a4", 0.6)])
s.step("The hypervisor's job: give each guest the illusion of a whole machine, while keeping the guests apart.", [mk("vm.vmm"), s.take("hypervisor: one real machine → many virtual ones")])
s.step("Why bother? First, isolation: a crash or an attack inside one VM cannot reach another.", [s.untake()] + hide("vm") + show("why") + [hl("why[0]")])
s.step("Consolidation: many servers that each sit mostly idle can share one machine.", [hl("why[1]")])
s.step("Managing software: a whole OS with its applications becomes one file, to copy, snapshot and restore.", [hl("why[2]")])
s.step("A running VM can even migrate to another machine. And all of this is what lets cloud providers rent out VMs by the hour.", [hl("why[3]"), hl("why[4]", 0.4)])

# ---------------------------------------------------------------- types
s.scene("types")
s.step("Stage 2: there are two kinds of hypervisor.", [s.head("Stage 2 of 8: type 1 and type 2")] + hide("why") + show("ty"))
s.step("Type 1, bare metal, runs directly on the hardware. Type 2, hosted, runs as an ordinary program on a host OS.", [hl("ty[0]")])
s.step("Type 1 examples: VMware ESXi, Xen, Microsoft Hyper-V. Type 2: VirtualBox, VMware Workstation.", [hl("ty[1]")])
s.step("Type 1 runs servers and the cloud. Type 2 runs on desktops, for testing and trying other systems.", [hl("ty[2]")])
s.step("And type 2 costs more, because every request from a guest also passes through the host OS.", [hl("ty[3]"), s.take("type 1: on the hardware · type 2: on a host OS")])

# ---------------------------------------------------------------- trap and emulate
s.scene("trap")
s.step("Stage 3: how can a guest OS run at full speed, yet never take over the real machine? Trap and emulate.", [s.head("Stage 3 of 8: trap and emulate"), s.untake()] + hide("ty") + show("te"))
s.step("The guest's applications run directly on the CPU. No interpretation, full speed.", [hl("te[0]")])
s.step("The guest OS runs directly too, but in user mode, not kernel mode. It does not know that.", [hl("te[1]")])
s.step("Sooner or later it executes a privileged instruction. Say, disable interrupts.", [hl("te[2]")])
s.step("In user mode that is not allowed, so the CPU traps, and control passes to the hypervisor.", [hl("te[3]")])
s.step("The hypervisor emulates the instruction, but only for this VM. It clears that VM's virtual interrupt flag, not the real one.", [hl("te[4]")])
s.step("And the guest resumes, unaware. The real machine stays under the hypervisor's control.", [hl("te[5]"), s.take("run directly · trap the privileged instructions · emulate them")])

# ---------------------------------------------------------------- ISA
s.scene("isa")
s.step("Stage 4: this only works if the right instructions trap. Popek and Goldberg stated the condition in 1974.", [s.head("Stage 4 of 8: when an ISA is hard to virtualize"), s.untake()] + hide("te") + show("pg") + [hl("pg[0]")])
s.step("Every sensitive instruction must be privileged.", rv("pg", 1))
s.step("Sensitive means it reads or changes the machine's state. Privileged means it traps in user mode. If a sensitive instruction runs quietly in user mode, the hypervisor never sees it.", rv("pg", 2))
s.step("The classic x86 broke this rule. POPF, for example, run in user mode, silently ignores a change to the interrupt flag. No trap: the guest's request is simply lost.", hide("pg") + show("x86") + [hl("x86[0]")])
s.step("Fix one, binary translation: the hypervisor scans the guest kernel's code and rewrites the bad instructions before they run. Early VMware did this.", [hl("x86[1]")])
s.step("Fix two, paravirtualization: change the guest OS itself to call the hypervisor directly, with hypercalls. Xen did this.", [hl("x86[2]")])
s.step("Fix three, hardware support. Intel VT-x and AMD-V add a new root mode for the hypervisor. The guest runs in its own kernel mode, and the hardware traps exactly the events the hypervisor asks for.", [hl("x86[3]"), s.take("sensitive must be privileged · else translate, paravirtualize, or add hardware")])

# ---------------------------------------------------------------- memory
s.scene("memory")
s.step("Stage 5: memory. Now there are three kinds of address.", [s.head("Stage 5 of 8: virtualizing memory"), s.untake()] + hide("x86") + show("mm"))
s.step("The guest's programs use guest virtual addresses. The guest OS page table maps them to guest physical addresses, what the guest believes is RAM.", [hl("mm[0]"), hl("mm[1]", 0.4)])
s.step("But that is not real memory. The hypervisor maps guest physical to host physical, the real frames.", [hl("mm[1]"), hl("mm[2]", 0.4)])
s.step("The TLB must end up holding guest virtual to host physical. Two ways to get there.", hide("mm") + show("mx"))
s.step("Shadow page tables: the hypervisor builds the combined table itself. But then every write the guest makes to its own page table must trap, so the shadow stays in sync.", [hl("mx[0]")])
s.step("Nested, or extended, page tables: the hardware walks both tables itself. Intel calls it EPT, AMD calls it NPT. No traps, but a TLB miss becomes expensive.", [hl("mx[1]")])
s.step("How expensive? Say the guest table has g levels and the host table h levels.", hide("mx") + show("nw") + [hl("nw[0]")])
s.step("Every pointer in the guest's walk is a guest physical address, and so is the final result. That is g plus 1 addresses, and each needs its own h-level host walk.", rv("nw", 1))
s.step("Add the g guest reads themselves: g plus 1, times h, plus g. Which is g plus 1, times h plus 1, minus 1.", rv("nw", 2))
s.step("With four levels each, 24 memory references, against 4 natively. That is why large pages and big TLBs matter so much inside VMs.", rv("nw", 3) + [s.take("nested walk = (g + 1)(h + 1) − 1 references")])

# ---------------------------------------------------------------- I/O
s.scene("io")
s.step("Stage 6: I/O. Guests share the same disks and network cards.", [s.head("Stage 6 of 8: virtualizing I/O"), s.untake()] + hide("nw") + show("io"))
s.step("The simplest: the hypervisor pretends to be a well-known device. Any guest driver works, but every device register access traps.", [hl("io[0]")])
s.step("Faster: paravirtual drivers, such as virtio. The guest knows it is in a VM, and hands over requests in batches.", [hl("io[1]")])
s.step("Fastest: give a real device to one VM directly. An IOMMU translates and checks the device's memory accesses, so it cannot touch other VMs.", [hl("io[2]"), s.take("emulate · paravirtualize · assign directly with an IOMMU")])

# ---------------------------------------------------------------- cost
s.scene("cost")
s.step("Stage 7: what does a VM cost? The answer depends on how often the guest traps.", [s.head("Stage 7 of 8: the cost in numbers"), s.untake()] + hide("io") + show("cost") + [hl("cost[0]")])
s.step("A program takes 10 seconds natively, and 20 percent of that is OS work that traps in a VM. Suppose that part runs 5 times slower: 8 plus 2 times 5 is 18 seconds. A slowdown of 1.8.", rv("cost", 1))
s.step("With hardware support, say the OS part is only 1.5 times slower: 8 plus 3, 11 seconds.", rv("cost", 2))
s.step("And a pure computation hardly traps at all, so it runs at almost native speed. This is Amdahl's law again: only the part that traps is slowed.", rv("cost", 3) + [s.take("VM time = untouched part + trapping part × its slowdown")])

# ---------------------------------------------------------------- exam
s.scene("exam")
s.step("Now an exam question.", [s.head("Exam question"), s.untake()] + hide("cost") + show("q"))
s.step("A program runs 20 seconds natively, 30 percent of it OS work. Find its time in a VM where OS work is 4 times slower, and with hardware support, 2 times slower.", [hl("q[0]"), hl("q[1]", 0.4)])
s.step("Then: memory references for one nested walk, with a 2-level guest table and a 3-level host table. And can trap and emulate handle an instruction that reads a privileged flag without trapping? Pause and work it out.", [hl("q[2]"), hl("q[3]", 0.4)])
s.step("a: 70 percent, 14 seconds, is unchanged. The OS part, 6 seconds, becomes 24. 38 seconds, a slowdown of 1.9.", hide("q") + show("qa") + [hl("qa[0]")])
s.step("b: 14 plus 6 times 2: 26 seconds.", rv("qa", 1))
s.step("c: 2 plus 1, times 3 plus 1, minus 1. 11 references.", rv("qa", 2))
s.step("d: no. Reading a privileged flag makes it sensitive, and it does not trap, so it is not privileged. The hypervisor would never see it.", rv("qa", 3))
s.step("The usual slips: slowing down the whole program instead of only the trapping part, and forgetting the final address translation in a nested walk.", [s.take("only the trapping part slows down")])

# ---------------------------------------------------------------- recap
s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qa") + show("stages"))
s.step("A hypervisor runs many guest OSes on one machine. Guests run directly, and their privileged instructions trap and are emulated. That needs every sensitive instruction to be privileged.", [hl("stages[0..=3]")])
s.step("Memory needs two translations, done by shadow or nested page tables. I/O is emulated, paravirtual, or assigned directly. And the cost is Amdahl's law on the trapping part.", [hl("stages[4..=6]")])
s.step("Next video: case studies. Real caches, TLBs and memory in the ARM Cortex-A53 and the Intel Core i7.", [mk("stages[0..=7]"), s.take("Next: case studies, ARM Cortex-A53 and Intel Core i7")])

s.save("/home/claude/playlist/m2v13.json")
