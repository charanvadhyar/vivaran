CODE=[("ADD","R1",["R2","R3"],"ADD R1, R2, R3"),("SUB","R4",["R1","R5"],"SUB R4, R1, R5"),("LW","R6",["R4"],"LW  R6, 0(R4)"),
      ("AND","R7",["R6","R8"],"AND R7, R6, R8"),("OR","R9",["R7","R1"],"OR  R9, R7, R1")]
def sched(code, fwd):
    D,E,M,W,F=[],[],[],[],[]
    for i,(op,d,src,_) in enumerate(code):
        f = 1 if i==0 else D[i-1]          # fetched in the cycle the previous one leaves ID? use IF = prev ID first cycle
        f = i+1 if i==0 else max(i+1, F[i-1]+1)
        d0 = max(f+1, (D[i-1]+1) if i else 0)
        for s in src:
            ps=[p for p in range(i) if code[p][1]==s]
            if not ps: continue
            p=ps[-1]
            if fwd:
                need_e = (M[p]+1) if code[p][0]=="LW" else (E[p]+1)
                d0=max(d0, need_e-1)
            else:
                d0=max(d0, W[p])
        # stalled instruction holds IF of next: next IF = this D-start... handled via F
        D.append(d0); E.append(d0+1); M.append(d0+2); W.append(d0+3)
        F.append(f if i==0 else max(f, D[i-1]))   # IF ends when previous leaves ID
    return F,D,E,M,W
if __name__ == '__main__':
  for fwd in (False,True):
    F,D,E,M,W=sched(CODE,fwd)
    print("fwd" if fwd else "nofwd", "total", W[-1], "stalls", W[-1]-(5+len(CODE)-1))
    for i in range(len(CODE)): print("  ",CODE[i][3],"IF",F[i],"ID",D[i],"EX",E[i],"MEM",M[i],"WB",W[i])


def occupancy(code, fwd):
    """Blocks (lane index, cycle, label) for a space-time diagram with stalls shown."""
    F, D, E, M, W = sched(code, fwd)
    out, id_entry = [], []
    for i in range(len(code)):
        ife = 1 if i == 0 else id_entry[i - 1]
        ide = 2 if i == 0 else D[i - 1] + 1
        id_entry.append(ide)
        out.append((i, ife, "IF"))
        for c in range(ife + 1, ide):
            out.append((i, c, "stall"))
        out.append((i, ide, "ID"))
        for c in range(ide + 1, D[i] + 1):
            out.append((i, c, "stall"))
        out += [(i, E[i], "EX"), (i, M[i], "MEM"), (i, W[i], "WB")]
    return out, W[-1]
