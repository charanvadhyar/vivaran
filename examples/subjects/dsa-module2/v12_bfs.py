"""DSA Module 2, video 12: breadth-first search on the lab network."""
import sys
from collections import deque
sys.path.insert(0, "/home/claude/playlist"); sys.path.insert(0, "/home/claude/playlist/dsa2")
from common import Script
from h import *

V = list("ABCDEFGHIJ")
E = [("A", "B"), ("A", "C"), ("B", "D"), ("B", "E"), ("C", "E"), ("C", "F"), ("D", "G"), ("E", "H"), ("F", "I"), ("G", "J"), ("H", "J"), ("I", "J")]
def adj(rem=()):
    a = {v: [] for v in V if v not in rem}
    for x, y in E:
        if x in rem or y in rem: continue
        a[x].append(y); a[y].append(x)
    for v in a: a[v].sort()
    return a
def bfs(s, rem=()):
    a = adj(rem); d = {s: 0}; q = deque([s]); order = []; par = {s: None}; qlog = []
    while q:
        u = q.popleft(); order.append(u); new = []
        for w in a[u]:
            if w not in d: d[w] = d[u] + 1; par[w] = u; q.append(w); new.append(w)
        qlog.append((u, new))
    return d, order, par, qlog
D, ORD, PAR, QLOG = bfs("A")
assert D == {"A": 0, "B": 1, "C": 1, "D": 2, "E": 2, "F": 2, "G": 3, "H": 3, "I": 3, "J": 4} and ORD == V
assert QLOG == [("A", ["B", "C"]), ("B", ["D", "E"]), ("C", ["F"]), ("D", ["G"]), ("E", ["H"]), ("F", ["I"]), ("G", ["J"]), ("H", []), ("I", []), ("J", [])]
def bridges(s, t):
    base = bfs(s)[0][t]; return [v for v in V if v not in (s, t) and bfs(s, (v,))[0].get(t, 99) > base]
assert bridges("A", "J") == [] and bridges("A", "H") == ["E"] and bridges("A", "I") == ["C", "F"] and bridges("D", "I") == ["G", "J"]
ecc = {v: max(bfs(v)[0].values()) for v in V}; assert max(ecc.values()) == 4 and ecc["E"] == 3
DE, ORDE, _, _ = bfs("E")
assert DE == {"E": 0, "B": 1, "C": 1, "H": 1, "A": 2, "D": 2, "F": 2, "J": 2, "G": 3, "I": 3} and ORDE == list("EBCHADFJGI")
path_AJ = []; x = "J"
while x: path_AJ.append(x); x = PAR[x]
assert path_AJ[::-1] == ["A", "B", "D", "G", "J"]

POS = {"A": (2, 0), "B": (1, 1), "C": (3, 1), "D": (0, 2), "E": (2, 2), "F": (4, 2), "G": (0, 3), "H": (2, 3), "I": (4, 3), "J": (2, 4)}
s = Script("Breadth-first search")
s.obj({"id": "stages", "type": "table", "region": "center", "columns": ["stage", "what we do"], "rows": [
    [1, "The idea: ripples outward"],
    [2, "The algorithm"],
    [3, "A trace from A"],
    [4, "Minimum hops and the path"],
    [5, "Devices within k hops"],
    [6, "Bridge devices"],
    [7, "The diameter"],
    [8, "Exam question"]]})
s.obj({"id": "g", "type": "diagram", "region": "left", "layout": "grid", "directed": False,
       "nodes": [{"id": v, "at": list(POS[v]), "shape": "circle"} for v in V], "edges": [{"from": a, "to": b} for a, b in E]})
s.obj({"id": "code", "type": "code", "region": "right", "language": "text", "lines": [
    "BFS(G, s)",
    "  for each vertex u: u.d = ∞;  u.π = nil",
    "  s.d = 0;  Q = [s]",
    "  while Q is not empty",
    "      u = DEQUEUE(Q)",
    "      for each v adjacent to u",
    "          if v.d == ∞                // not yet discovered",
    "              v.d = u.d + 1;  v.π = u",
    "              ENQUEUE(Q, v)"]})
s.obj({"id": "qq", "type": "array", "region": "right", "values": []})
s.obj({"id": "dt", "type": "table", "region": "right", "columns": ["vertex"] + V, "rows": [["d"] + [""] * 10, ["π"] + [""] * 10]})
s.obj({"id": "kh", "type": "table", "region": "right", "columns": ["query", "answer from one BFS of A"], "rows": [
    ["hops A → J", "J.d = 4"],
    ["the path", "follow π back: J ← G ← D ← B ← A"],
    ["within 2 hops of A", "every v with v.d ≤ 2: B, C, D, E, F"],
    ["unreachable", "v.d stays ∞: report 'no path'"]]})
s.obj({"id": "br", "type": "table", "region": "right", "columns": ["pair", "hops", "after removing", "bridges"], "rows": [
    ["A → H", "3", "E: 5", "E"],
    ["A → I", "3", "C or F: 5", "C, F"],
    ["A → J", "4", "any one: still 4", "none"]]})
s.obj({"id": "dm", "type": "table", "region": "right", "columns": ["start", "farthest", "eccentricity"], "rows": [
    ["A", "J", "4"], ["E", "G, I", "3"], ["H", "A, F, …", "3"], ["…", "", ""], ["diameter", "max over all starts", "4"]]})
s.obj({"id": "co", "type": "table", "region": "center", "columns": ["BFS costs, adjacency lists", ""], "rows": [
    ["each vertex", "enqueued and dequeued once: O(n)"],
    ["each list", "scanned once when its vertex is dequeued: O(m) in all"],
    ["total", "O(n + m)"],
    ["bridge devices by removal", "one BFS per device: O(n (n + m))"],
    ["diameter", "one BFS per vertex: O(n (n + m))"]]})
s.obj({"id": "q", "type": "table", "region": "center", "columns": ["exam question: the same network, now starting at E"], "rows": [
    ["a) the BFS order and every distance, taking neighbours alphabetically"],
    ["b) minimum hops from E to G, and devices within 1 hop of E"],
    ["c) the bridge devices between D and I"]]})
s.obj({"id": "qa", "type": "table", "region": "right", "columns": ["part", "answer"], "rows": [
    ["order", "E B C H A D F J G I"],
    ["d = 1", "B, C, H"],
    ["d = 2", "A, D, F, J"],
    ["d = 3", "G, I"],
    ["b", "E → G: 3 hops · within 1: B, C, H"],
    ["c) D → I", "3 hops: D G J I only · bridges G, J"]]})

def visit(u, new):
    out = [rm("qq[0]"), mk(f"g.{u}", 0.1)]
    for k, w in enumerate(new):
        out += [st(f"dt[0][{V.index(w) + 1}]", str(D[w]), round(0.3 + 0.1 * k, 2)), st(f"dt[1][{V.index(w) + 1}]", u, round(0.3 + 0.1 * k, 2)),
                {"action": "insert", "target": "qq", "index": 0, "value": w, "delay": round(0.35 + 0.1 * k, 2)}]
    return out
qstate = ["A"]
def visit2(u, new):
    global qstate
    out = [rm("qq[0]"), mk(f"g.{u}", 0.1)]; qstate = qstate[1:]
    for k, w in enumerate(new):
        out += [st(f"dt[0][{V.index(w) + 1}]", str(D[w]), round(0.3 + 0.1 * k, 2)), st(f"dt[1][{V.index(w) + 1}]", u, round(0.3 + 0.1 * k, 2)),
                {"action": "insert", "target": "qq", "index": len(qstate), "value": w, "delay": round(0.35 + 0.1 * k, 2)}]
        qstate = qstate + [w]
    return out

s.scene("intro")
s.step("Breadth-first search explores a graph the way ripples spread on water: first everything one step away, then everything two steps away, and so on. That order makes it the tool for shortest paths in unweighted networks. This video runs it on the lab's network and answers all four lab queries.", [s.head("Breadth-first search")])
s.step("Here are the eight stages.", show("stages"))
s.step("The idea, the algorithm, a full trace, and minimum hops with the path itself.", [hl("stages[0..=3]")])
s.step("Then devices within k hops, bridge devices, the diameter, and an exam question.", [hl("stages[4..=7]")])

s.scene("idea")
s.step("Stage 1: start at device A. Its neighbours B and C are 1 hop away.", [s.head("Stage 1 of 8: ripples outward")] + hide("stages") + show("g") + [mk("g.A"), hl("g.B", 0.4)])
s.step("Their unvisited neighbours, D, E and F, are 2 hops away; then G, H and I at 3; then J at 4.", [hl("g.E")])
s.step("BFS finishes every vertex at distance k before touching any at distance k plus 1. A first-in, first-out queue enforces exactly that order.", [s.take("level by level, with a queue")])

s.scene("algo")
s.step("Stage 2: Cormen's BFS. Every vertex starts undiscovered, with distance infinity and no parent.", [s.head("Stage 2 of 8: the algorithm"), s.untake(), rs("g")] + show("code") + [ml("code", 1, 2)])
s.step("The source gets distance 0 and goes into the queue.", [ml("code", 3, 3)])
s.step("Repeatedly take the front vertex u, and look at each neighbour v.", [ml("code", 4, 6)])
s.step("If v is still undiscovered, its distance is u's plus 1, its parent is u, and it joins the back of the queue.", [ml("code", 7, 9), s.take("discover, set d and π, enqueue")])

s.scene("trace")
s.step("Stage 3: BFS from A, taking neighbours in alphabetical order. A has distance 0 and waits in the queue.", [s.head("Stage 3 of 8: a trace from A"), s.untake()] + hide("code") + show("qq", "dt") + [ins("qq", 0, "A"), st("dt[0][1]", "0", 0.3), st("dt[1][1]", "–", 0.3)])
s.step("Dequeue A. Its neighbours B and C are new: distance 1, parent A. Enqueue them.", visit2("A", ["B", "C"]))
s.step("Dequeue B: A is already seen; D and E are new, distance 2, parent B.", visit2("B", ["D", "E"]))
s.step("Dequeue C: A and E are already seen; F is new, distance 2.", visit2("C", ["F"]))
s.step("Dequeue D: G is new, distance 3. Dequeue E: H is new, distance 3.", visit2("D", ["G"]) + [x for x in visit2("E", ["H"]) if True])
s.step("Dequeue F: I, distance 3. Dequeue G: J, distance 4.", visit2("F", ["I"]) + visit2("G", ["J"]))
s.step("H, I and J find nothing new. The queue empties. The order of visits was A to J alphabetically, here by coincidence of the drawing; the distances are 0, 1, 1, 2, 2, 2, 3, 3, 3, 4.", visit2("H", []) + visit2("I", []) + visit2("J", []) + [s.take("each vertex enters the queue once")])

s.scene("hops")
s.step("Stage 4: the lab's first query, the minimum hops between two devices, is just the distance: from A to J, 4.", [s.head("Stage 4 of 8: minimum hops"), s.untake()] + hide("qq", "dt") + show("kh") + [hl("kh[0]")])
s.step("The path itself comes from the parents: J's parent is G, G's is D, D's is B, B's is A. Reversed: A, B, D, G, J.", [hl("kh[1]"), hl("g.J", 0.2), hl("g.G", 0.4), hl("g.D", 0.6), hl("g.B", 0.8)])
s.step("If a device was never discovered, its distance stays infinite: there is no path, and the program should say so.", [hl("kh[3]"), s.take("d = hops · π = the route back")])

s.scene("khops")
s.step("Stage 5: the second query: every device within max hops of a start, the reach of a broadcast or a virus. Run BFS and keep every vertex with distance at most k.", [s.head("Stage 5 of 8: within k hops"), s.untake(), hl("kh[2]")])
s.step("Within 2 hops of A: B and C at 1, and D, E and F at 2. You can also stop the search early, as soon as you dequeue a vertex at distance k.", [rs("g"), mk("g.B"), mk("g.C", 0.1), mk("g.D", 0.2), mk("g.E", 0.3), mk("g.F", 0.4), s.take("within k hops: d ≤ k")])

s.scene("bridge")
s.step("Stage 6: the third query: bridge devices between a source and a target, devices whose removal makes the trip longer or impossible. The simplest method: remove each device in turn, and run BFS again.", [s.head("Stage 6 of 8: bridge devices"), s.untake(), rs("g")] + hide("kh") + show("br"))
s.step("A to H is 3 hops, through E. Remove E, and the best route becomes A, B, D, G, J, H: 5 hops. So E is a bridge device.", [hl("br[0]"), hl("g.E", 0.4)])
s.step("A to I is 3 hops, but only along A, C, F, I. Remove C or F, and it grows to 5. Both are bridge devices.", [hl("br[1]"), mk("g.C", 0.4), mk("g.F", 0.5)])
s.step("A to J has four different 4-hop routes. No single device lies on all of them, so there are none. A faster method counts shortest paths: a device is a bridge exactly when every shortest path passes through it.", [hl("br[2]"), s.take("bridge = on every shortest path")])

s.scene("diam")
s.step("Stage 7: the fourth query: the diameter of a device's connected component, the longest shortest path. Run BFS from every vertex and record its largest distance, its eccentricity.", [s.head("Stage 7 of 8: the diameter"), s.untake(), rs("g")] + hide("br") + show("dm") + [hl("dm[0]")])
s.step("From A, the farthest is J, 4 hops away. From E, the farthest are G and I, 3 hops away.", [hl("dm[1]")])
s.step("The diameter is the largest eccentricity: 4. BFS only reaches the start's own component, so this gives exactly the component's diameter.", [hl("dm[4]"), s.take("diameter = max over starts of max distance")])

s.scene("cost")
s.step("Costs, with adjacency lists: each vertex is enqueued and dequeued once, and each list is scanned once.", [hl("dm")] + hide("g", "dm") + show("co") + [hl("co[0..=1]")])
s.step("So one BFS is O of n plus m. The bridge and diameter queries run n searches: O of n times n plus m, still fast for networks of thousands of devices.", [hl("co[2..=4]")])

s.scene("exam")
s.step("Now an exam question, starting from E.", [s.head("Exam question"), s.untake()] + hide("co") + show("g", "q") + [hl("q[0]")])
s.step("Give the BFS order and distances, the hops from E to G, the devices within 1 hop, and the bridge devices between D and I. Pause and work it out.", [hl("q[1..=2]")])
s.step("E's neighbours alphabetically: B, C, H, distance 1. B adds A and D; C adds F; H adds J: distance 2. Then D adds G, F adds I: distance 3.", hide("q") + show("qa") + [hl("qa[0..=3]")])
s.step("b: G has distance 3, so 3 hops. Within 1 hop: B, C and H.", [hl("qa[4]")])
s.step("c: D to I is 3 hops, and the only 3-hop route is D, G, J, I. Remove G or J and it grows, so both are bridge devices.", [hl("qa[5]"), mk("g.G", 0.4), mk("g.J", 0.5)])
s.step("The usual slip: marking a vertex as seen when it is dequeued instead of when it is enqueued. Then it can enter the queue twice.", [s.take("mark when discovered, not when dequeued")])

s.scene("recap")
s.step("Let us walk the stages again.", [s.head("Recap"), s.untake()] + hide("g", "qa") + show("stages"))
s.step("BFS uses a queue to finish each distance before the next, setting each vertex's distance and parent when it is discovered. One run costs O of n plus m.", [hl("stages[0..=3]")])
s.step("Distances answer minimum hops and k-hop reach; parents give the route; repeated runs find bridge devices and the diameter.", [hl("stages[4..=6]")])
s.step("Next video: going deep instead of wide. Depth-first search.", [mk("stages[0..=7]"), s.take("Next: depth-first search")])

s.save("/home/claude/playlist/dsa2/d2v12.json")
