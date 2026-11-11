import itertools, random
def sim(seq, k, pol):
    frames=[None]*k; order=[]; out=[]; 
    for r in seq:
        if r in frames:
            if pol=="LRU": order.remove(r); order.append(r)
            out.append(("hit",None,list(frames)))
        else:
            if None in frames:
                i=frames.index(None); ev=None
            else:
                v=order.pop(0); i=frames.index(v); ev=v
            frames[i]=r; order.append(r)
            out.append(("miss",ev,list(frames)))
    return out
def hits(seq,k,pol): return sum(o[0]=="hit" for o in sim(seq,k,pol))
if __name__=="__main__":
    best=[]
    random.seed(1)
    for n in (8,9,10):
        for _ in range(200000):
            seq=[random.choice("ABCD") for _ in range(n)]
            l,f=hits(seq,3,"LRU"),hits(seq,3,"FIFO")
            best.append((f-l, -n, "".join(seq), l, f))
    best.sort(reverse=True)
    print("FIFO beats LRU:", best[:5])
    best.sort(key=lambda t:(t[0], t[1]))
    print("LRU beats FIFO:", best[:5])
