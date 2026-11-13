"""Module 4, video 8: gather-scatter and sparse matrices."""
import sys
sys.path.insert(0, "/home/claude/playlist")
from common import Script


def run(A, C, K, M):
    A = list(A)
    ga = [A[k] for k in K]
    gc = [C[m] for m in M]
    sm = [a + c for a, c in zip(ga, gc)]
    for k, v in zip(K, sm):
        A[k] = v
    return ga, gc, sm, A


A0 = [5, 1, 7, 3, 9, 2, 8, 4]
C0 = [10, 20, 30, 40, 50, 60, 70, 80]
K0, M0 = [6, 1, 4, 0], [2, 7, 0, 5]
GA, GC, SM, AF = run(A0, C0, K0, M0)
assert GA == [8, 1, 9, 5] and GC == [30, 80, 10, 60] and SM == [38, 81, 19, 65]
assert AF == [65, 81, 7, 3, 19, 2, 38, 4]
QA, QC_ = [2, 4, 6, 8, 10, 12, 14, 16], [1, 1, 2, 3, 5, 8, 13, 21]
QK, QM = [3, 5, 1, 7], [0, 2, 4, 6]
qga, qgc, qsm, qaf = run(QA, QC_, QK, QM)
assert qga == [8, 12, 4, 16] and qgc == [1, 2, 5, 13] and qsm == [9, 14, 9, 29]
assert qaf == [2, 9, 6, 9, 10, 14, 14, 29]
# duplicates: K = [3, 5, 3, 7]: both lanes read A[3] = 8, scatter keeps one sum
d = run(QA, QC_, [3, 5, 3, 7], QM)
assert d[2] == [9, 14, 13, 29] and d[3][3] == 13 and 8 + 1 + 5 == 14
XV = [1, 2, 3, 4, 5, 6, 7, 8]
RV, RC = [2, 5, 1, 3], [0, 3, 4, 7]
GX = [XV[c] for c in RC]
PR = [v * x for v, x in zip(RV, GX)]
assert GX == [1, 4, 5, 8] and PR == [2, 20, 5, 24] and sum(PR) == 51
# CSR sizes
assert 1000 * 1000 * 8 == 8_000_000 and 10_000 * 8 + 10_000 * 4 + 1001 * 4 == 124_004
assert 2000 * 2000 * 8 == 32_000_000 and 2000 * 2000 // 200 == 20_000
assert 20_000 * 8 + 20_000 * 4 + 2001 * 4 == 248_004 and round(32_000_000 / 248_004) == 129

s = Script("Gather and scatter")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "Sparse data"],
    [2, "Storing a sparse matrix"],
    [3, "Gather and scatter"],
    [4, "The VMIPS code"],
    [5, "Element by element"],
    [6, "A sparse row in vector code"],
    [7, "The catch: duplicate indices"],
    [8, "Cost, and where else it appears"],
    [9, "Exam question"]]})
s.obj({"id": "sp", "type": "table", "region": "center", "columns": ["sparse data", "example"], "rows": [
    ["a matrix with mostly zeros", "a 1000 × 1000 matrix with 1% non-zero"],
    ["dense storage", "1,000,000 doubles: 8 MB, almost all zeros"],
    ["useful work", "only the 10,000 non-zeros matter"],
    ["where it appears", "circuit simulation, finite elements, graphs, recommender systems"]]})
s.obj({"id": "csr", "type": "table", "region": "center", "columns": ["CSR array", "holds", "size for 10,000 non-zeros"], "rows": [
    ["val", "the non-zero values, row by row", "10,000 × 8 B = 80,000 B"],
    ["col", "the column of each value", "10,000 × 4 B = 40,000 B"],
    ["rowptr", "where each row starts in val", "1001 × 4 B = 4,004 B"],
    ["total", "", "124,004 B ≈ 124 KB, against 8 MB dense"]]})
s.obj({"id": "spmv", "type": "code", "region": "center", "language": "c", "lines": [
    "// y = A x, A in CSR",
    "for (i = 0; i < n; i++)",
    "    for (j = rowptr[i]; j < rowptr[i+1]; j++)",
    "        y[i] += val[j] * x[col[j]];     // x is read at scattered places"]})
s.obj({"id": "gs", "type": "table", "region": "center", "columns": ["operation", "VMIPS", "does"], "rows": [
    ["gather", "LVI V1,(R1+V2)", "V1[i] = memory[R1 + V2[i]]: load from a list of addresses"],
    ["scatter", "SVI (R1+V2),V1", "memory[R1 + V2[i]] = V1[i]: store to a list of addresses"],
    ["the index vector", "V2", "loaded first, an ordinary vector of offsets"],
    ["RISC-V V", "vluxei64 · vsuxei64", "indexed load and store"]]})
s.obj({"id": "c", "type": "code", "region": "left", "language": "c", "lines": [
    "for (i = 0; i < n; i++)",
    "  A[K[i]] = A[K[i]] + C[M[i]];"]})
s.obj({"id": "code", "type": "code", "region": "center", "language": "asm", "lines": [
    "LV       Vk,Rk          ; load the index vector K",
    "LVI      Va,(Ra+Vk)     ; gather A[K[i]]",
    "LV       Vm,Rm          ; load the index vector M",
    "LVI      Vc,(Rc+Vm)     ; gather C[M[i]]",
    "ADDVV.D  Va,Va,Vc       ; add",
    "SVI      (Ra+Vk),Va     ; scatter back to A[K[i]]"]})
s.obj({"id": "ga", "type": "table", "region": "center", "columns": ["i", "0", "1", "2", "3"], "rows": [
    ["K[i]", *map(str, K0)], ["gathered A[K[i]]", "", "", "", ""],
    ["M[i]", *map(str, M0)], ["gathered C[M[i]]", "", "", "", ""],
    ["sum, scattered to A[K[i]]", "", "", "", ""]]})
s.obj({"id": "arr", "type": "table", "region": "center", "columns": ["index", "0", "1", "2", "3", "4", "5", "6", "7"], "rows": [
    ["A before", *map(str, A0)], ["C", *map(str, C0)], ["A after", *map(str, AF)]]})
s.obj({"id": "row", "type": "code", "region": "left", "language": "asm", "lines": [
    "; one row of y = A x: VLR = its non-zeros",
    "LV       V1,Rcol      ; column indices",
    "LVI      V2,(Rx+V1)   ; gather x[col[j]]",
    "LV       V3,Rval      ; the values",
    "MULVV.D  V4,V3,V2     ; products",
    "; sum V4 into y[i]: a reduction",
    "; (RISC-V: vfredusum)"]})
s.obj({"id": "rowt", "type": "table", "region": "right", "columns": ["j", "0", "1", "2", "3"], "rows": [
    ["col[j]", *map(str, RC)], ["x[col[j]]", "", "", "", ""], ["val[j]", *map(str, RV)], ["product", "", "", "", ""], ["y[i]", "", "", "", ""]]})
s.obj({"id": "dup", "type": "table", "region": "center", "columns": ["duplicate indices", "what happens"], "rows": [
    ["K = 3, 5, 3, 7", "two lanes read the same A[3]"],
    ["both add their own C value", "to the same old A[3]"],
    ["the scatter", "writes A[3] twice: one sum is lost"],
    ["a scalar loop would", "add both, one after the other"],
    ["so", "vectorize only if K has no duplicates: the programmer must promise it"]]})
s.obj({"id": "cost", "type": "table", "region": "center", "columns": ["gather and scatter", "cost"], "rows": [
    ["addresses", "random: bank conflicts are likely"],
    ["each element", "a separate memory access: no bulk transfer"],
    ["so", "much slower per element than unit stride, but far faster than a scalar loop"],
    ["also in", "AVX2 gather (2013), AVX-512 scatter, every GPU load and store"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["index", "0", "1", "2", "3", "4", "5", "6", "7"], "rows": [
    ["A", *map(str, QA)], ["C", *map(str, QC_)], ["A after", "", "", "", "", "", "", "", ""]]})
s.obj({"id": "qx", "type": "table", "region": "center", "columns": ["the same loop, K = 3, 5, 1, 7 and M = 0, 2, 4, 6. Find:"], "rows": [
    ["a) the gathered vectors, the sums, and A after the scatter"],
    ["b) what goes wrong if K were 3, 5, 3, 7"],
    ["c) CSR size for a 2000 × 2000 matrix with 0.5% non-zero, against dense"]]})
s.obj({"id": "qa", "type": "table", "region": "center", "columns": ["i", "0", "1", "2", "3"], "rows": [
    ["A[K[i]]", *map(str, qga)], ["C[M[i]]", *map(str, qgc)], ["sum → A[K[i]]", *map(str, qsm)]]})
s.obj({"id": "qb", "type": "math", "region": "center", "lines": [
    "\"b) lanes 0 and 2 both read\" A[3] = 8: quad 8 + 1 = 9, quad 8 + 5 = 13 quad \"one is lost; the loop gives\" 14",
    "\"c) non-zeros\" = 2000^2 times 0.005 = 20000",
    "20000 times 8 + 20000 times 4 + 2001 times 4 = 248004 \"B\" approx 248 \"KB\" quad \"dense\" 32 \"MB\""]})

hl = lambda t, d=0: {"action": "highlight", "target": t, **({"delay": d} if d else {})}
mk = lambda t, d=0: {"action": "mark", "target": t, **({"delay": d} if d else {})}
ml = lambda t, a, b: {"action": "mark_lines", "target": t, "from": a, "to": b}
rv = lambda t: {"action": "reveal", "target": t}
st = lambda t, v, d=0: {"action": "set", "target": t, "value": v, **({"delay": d} if d else {})}
show = lambda *ids: [{"action": "show", "target": i} for i in ids]
hide = lambda *ids: [{"action": "hide", "target": i} for i in ids]

s.scene("intro")
s.step("Unit-stride and strided loads need a regular pattern. But much real data is irregular: sparse matrices, graphs, lookup tables. This video shows how vector machines load and store through a list of addresses.", [s.head("Gather and scatter")])
s.step("Here are the nine stages.", show("stages"))
s.step("Sparse data, how a sparse matrix is stored, gather and scatter, and the VMIPS code.", [hl("stages[0..=3]")])
s.step("Then a trace element by element, a sparse row in vector code, the danger of duplicate indices, the cost, and an exam question.", [hl("stages[4..=8]")])

s.scene("sparse")
s.step("Stage 1: a sparse matrix is mostly zeros. Take a 1000 by 1000 matrix with 1 percent non-zero.", [s.head("Stage 1 of 9: sparse data")] + hide("stages") + show("sp") + [hl("sp[0]")])
s.step("Stored densely it takes a million doubles, 8 megabytes, almost all of them zero.", [hl("sp[1]")])
s.step("Only the 10,000 non-zeros do any useful work.", [hl("sp[2]")])
s.step("Such matrices are everywhere: circuit simulation, finite elements, graphs, recommender systems.", [hl("sp[3]"), s.take("store and touch only the non-zeros")])

s.scene("csr")
s.step("Stage 2: the usual format is CSR, compressed sparse row. Three arrays. val holds the non-zero values, row by row.", [s.head("Stage 2 of 9: storing it"), s.untake()] + hide("sp") + show("csr") + [hl("csr[0]")])
s.step("col holds each value's column number.", [hl("csr[1]")])
s.step("rowptr says where each row starts in val: one entry per row, plus one at the end.", [hl("csr[2]")])
s.step("With 8-byte values and 4-byte indices: 80,000 plus 40,000 plus 4,004 bytes. About 124 kilobytes, instead of 8 megabytes.", [hl("csr[3]")])
s.step("The matrix-vector product y equals A x then reads x at the column of each non-zero: x of col of j. Those reads jump around memory. No stride describes them.", hide("csr") + show("spmv") + [ml("spmv", 4, 4), s.take("CSR: val, col, rowptr · x read at col[j]")])

s.scene("gs")
s.step("Stage 3: two instructions handle such access. A gather, LVI, loads from a list of addresses: element i comes from R1 plus the i-th entry of an index vector.", [s.head("Stage 3 of 9: gather and scatter"), s.untake()] + hide("spmv") + show("gs") + [hl("gs[0]")])
s.step("A scatter, SVI, does the reverse: it stores element i to R1 plus the i-th index.", [hl("gs[1]")])
s.step("The index vector is an ordinary vector, loaded first with LV.", [hl("gs[2]")])
s.step("RISC-V calls them indexed loads and stores: vluxei and vsuxei.", [hl("gs[3]"), s.take("gather: load via indices · scatter: store via indices")])

s.scene("code")
s.step("Stage 4: the textbook's example. A of K of i gets C of M of i added to it: two index arrays, K and M.", [s.head("Stage 4 of 9: the VMIPS code"), s.untake()] + hide("gs") + show("c") + [ml("c", 1, 2)])
s.step("Load the index vector K, and gather the elements of A it points to.", hide("c") + show("code") + [ml("code", 1, 2)])
s.step("Load M, and gather the elements of C.", [ml("code", 3, 4)])
s.step("Add them as ordinary vectors.", [ml("code", 5, 5)])
s.step("And scatter the sums back to the same places in A, using K again. Six instructions for a loop no stride could express.", [ml("code", 6, 6), s.take("LV index · LVI gather · compute · SVI scatter")])

s.scene("trace")
s.step("Stage 5: four elements, step by step. Here are A and C.", [s.head("Stage 5 of 9: element by element"), s.untake()] + hide("code") + show("arr") + [hl("arr[0..=1]")])
s.step("K is 6, 1, 4, 0. The gather fetches A of 6, A of 1, A of 4 and A of 0: 8, 1, 9 and 5.", hide("arr") + show("ga") + [hl("ga[0]")] + [st(f"ga[1][{i + 1}]", str(v), round(0.15 * i, 2)) for i, v in enumerate(GA)])
s.step("M is 2, 7, 0, 5. The second gather fetches 30, 80, 10 and 60 from C.", [hl("ga[2]")] + [st(f"ga[3][{i + 1}]", str(v), round(0.15 * i, 2)) for i, v in enumerate(GC)])
s.step("Add: 38, 81, 19 and 65.", [st(f"ga[4][{i + 1}]", str(v), round(0.15 * i, 2)) for i, v in enumerate(SM)])
s.step("The scatter writes them back to positions 6, 1, 4 and 0 of A. The other positions are untouched.", hide("ga") + show("arr") + [hl("arr[2]"), s.take("gather from K · compute · scatter to K")])

s.scene("row")
s.step("Stage 6: back to the sparse matrix. One row of y equals A x, in vector code. Set VLR to the number of non-zeros in the row, here 4.", [s.head("Stage 6 of 9: a sparse row"), s.untake()] + hide("arr") + show("row", "rowt") + [ml("row", 1, 1)])
s.step("Load the row's column indices: 0, 3, 4 and 7.", [ml("row", 2, 2), hl("rowt[0]")])
s.step("Gather x at those columns. With x equal to 1 to 8, that is 1, 4, 5 and 8.", [ml("row", 3, 3)] + [st(f"rowt[1][{i + 1}]", str(v), round(0.12 * i, 2)) for i, v in enumerate(GX)])
s.step("Load the values, 2, 5, 1, 3, and multiply: 2, 20, 5 and 24.", [ml("row", 4, 5)] + [st(f"rowt[3][{i + 1}]", str(v), round(0.12 * i, 2)) for i, v in enumerate(PR)])
s.step("Finally, add the products into one number: a reduction. 51. VMIPS does it with a few vector adds of halves, and RISC-V has a reduction instruction, vfredusum. Real codes often vectorize across many rows instead, to get longer vectors.", [ml("row", 6, 7), st("rowt[4][1]", "51"), s.take("gather x · multiply · reduce")])

s.scene("dup")
s.step("Stage 7: the catch. Suppose K holds the same index twice: 3, 5, 3, 7.", [s.head("Stage 7 of 9: duplicate indices"), s.untake()] + hide("row", "rowt") + show("dup") + [hl("dup[0]")])
s.step("Lanes 0 and 2 both gather the same old A of 3, and each adds its own C value to it.", [hl("dup[1]")])
s.step("The scatter then writes A of 3 twice. Only one sum survives; the other addition is lost.", [hl("dup[2]")])
s.step("A scalar loop would have done the two additions one after the other, keeping both.", [hl("dup[3]")])
s.step("So the compiler may vectorize this loop only if K has no duplicates. It usually cannot prove that, so the programmer must promise it, with a pragma. A histogram, where many elements land in the same bin, is the classic loop that breaks.", [hl("dup[4]"), s.take("duplicate indices break scatter updates")])

s.scene("cost")
s.step("Stage 8: what does it cost? The addresses are random, so bank conflicts are likely.", [s.head("Stage 8 of 9: the cost"), s.untake()] + hide("dup") + show("cost") + [hl("cost[0]")])
s.step("Every element is a separate memory access. There is no bulk transfer of a whole block.", [hl("cost[1]")])
s.step("So a gather is much slower per element than a unit-stride load. But it is still far faster than a scalar loop, which pays instruction overhead and stalls on every element.", [hl("cost[2]")])
s.step("And the idea is everywhere: x86 added a gather in AVX2 and a scatter in AVX-512, and on a GPU, every thread's load is effectively part of a gather.", [hl("cost[3]"), s.take("gather is slow per element, still beats scalar")])

s.scene("exam")
s.step("Now an exam question: the same loop, with these A and C.", [s.head("Exam question"), s.untake()] + hide("cost") + show("q") + [hl("q[0..=1]")])
s.step("K is 3, 5, 1, 7 and M is 0, 2, 4, 6. Find the gathered vectors, the sums, and A after the scatter. Then what goes wrong if K were 3, 5, 3, 7. And the CSR size of a 2000 by 2000 matrix with half a percent non-zero. Pause and work it out.", hide("q") + show("qx") + [hl("qx")])
s.step("Gather A at 3, 5, 1, 7: 8, 12, 4, 16. Gather C at 0, 2, 4, 6: 1, 2, 5, 13. Sums: 9, 14, 9, 29.", hide("qx") + show("qa") + [hl("qa[0..=2]")])
s.step("Scatter them to positions 3, 5, 1 and 7.", hide("qa") + show("q") + [st(f"q[2][{i + 1}]", str(v), round(0.08 * i, 2)) for i, v in enumerate(qaf)])
s.step("b: with K equal to 3, 5, 3, 7, lanes 0 and 2 both read A of 3, which is 8. One computes 8 plus 1, the other 8 plus 5. The scatter keeps only one. The correct answer, from a scalar loop, is 14.", hide("q") + show("qb") + [hl("qb[0]")])
s.step("c: 2000 squared times 0.005 is 20,000 non-zeros.", [rv("qb[1]"), hl("qb[1]")])
s.step("20,000 values at 8 bytes, 20,000 columns at 4, and 2001 row pointers at 4: about 248 kilobytes, against 32 megabytes dense. About 129 times smaller.", [rv("qb[2]"), hl("qb[2]")])
s.step("The usual slip: forgetting the plus one in rowptr. n rows need n plus 1 entries, so the last row knows where it ends.", [s.take("rowptr has n + 1 entries")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("qb") + show("stages"))
s.step("Sparse data is stored compactly, as in CSR, and read through index arrays. Gather loads through an index vector; scatter stores through one. A sparse row is a gather, a multiply and a reduction.", [hl("stages[0..=5]")])
s.step("Duplicate indices break scatter updates, and random addresses make gathers slow per element, though still far faster than scalar code.", [hl("stages[6..=7]")])
s.step("Next video: the vector ideas squeezed into ordinary processors. SIMD extensions: MMX, SSE and AVX.", [mk("stages[0..=8]"), s.take("Next: SIMD extensions")])

s.save("/home/claude/playlist/m4/m4v8.json")
