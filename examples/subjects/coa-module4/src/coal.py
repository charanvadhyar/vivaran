"""Global-memory sectors touched by one warp: 32-byte sectors."""
def sectors(addrs, size, sector=32):
    s = set()
    for a in addrs:
        for b in range(a, a + size):
            s.add(b // sector)
    return len(s)

def eff(addrs, size, sector=32):
    n = sectors(addrs, size, sector)
    return n, 32 * size / (n * sector)
