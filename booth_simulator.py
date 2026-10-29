"""
B1: Booth and Modified Booth (bit-pair / radix-4) multiplier simulator
COA Bright Learner Activity - Don Bosco Institute of Technology

Usage:
  python booth_simulator.py            -> runs all 4-bit pairs, prints summary
  python booth_simulator.py -13 11 6   -> step-by-step trace for M=-13, Q=11, n=6 bits
"""
import sys


def mask(w):
    return (1 << w) - 1


def b(x, w):
    """Two's complement binary string of x using w bits."""
    return format(x & mask(w), "0{}b".format(w))


def fits(x, w):
    return -(1 << (w - 1)) <= x < (1 << (w - 1))


def booth_radix2(M, Q, n, aw=None):
    """Original Booth (radix-2). Returns (product, ops, steps)."""
    aw = aw or n + 2
    A, q, qm1, ops, steps = 0, Q & mask(n), 0, 0, []
    for i in range(1, n + 1):
        q0 = q & 1
        pair = "%d%d" % (q0, qm1)
        if pair == "10":
            A -= M; act = "A = A - M"; ops += 1
        elif pair == "01":
            A += M; act = "A = A + M"; ops += 1
        else:
            act = "No add/sub"
        assert fits(A, aw), "A overflow"
        a_op = b(A, aw)
        qm1 = q & 1
        q = (q >> 1) | ((A & 1) << (n - 1))
        A >>= 1
        steps.append(dict(step=i, pair=pair, act=act, A_op=a_op,
                          A=b(A, aw), Q=b(q, n), Qm1=str(qm1)))
    return A * (1 << n) + q, ops, steps


def booth_radix4(M, Q, n, aw=None):
    """Modified Booth (bit-pair recoding). n must be even."""
    assert n % 2 == 0
    aw = aw or n + 2
    A, q, qm1, ops, steps = 0, Q & mask(n), 0, 0, []
    for i in range(1, n // 2 + 1):
        trip = "%d%d%d" % ((q >> 1) & 1, q & 1, qm1)
        digit = -2 * ((q >> 1) & 1) + (q & 1) + qm1
        if digit != 0:
            ops += 1
        A += digit * M
        assert fits(A, aw), "A overflow"
        a_op = b(A, aw)
        act = {0: "No add/sub", 1: "A = A + M", 2: "A = A + 2M",
               -1: "A = A - M", -2: "A = A - 2M"}[digit]
        qm1 = (q >> 1) & 1
        q = (q >> 2) | ((A & 3) << (n - 2))
        A >>= 2
        steps.append(dict(step=i, pair=trip, digit=digit, act=act, A_op=a_op,
                          A=b(A, aw), Q=b(q, n), Qm1=str(qm1)))
    return A * (1 << n) + q, ops, steps


def print_trace(M, Q, n):
    aw = n                      # A register is n bits wide (as in the textbook)
    try:
        booth_radix2(M, Q, n, aw); booth_radix4(M, Q, n, aw)
    except AssertionError:
        aw = n + 2              # widen A if an intermediate value needs more bits
    print("M = %d (%s), Q = %d (%s), n = %d bits\n" % (M, b(M, n), Q, b(Q, n), n))
    p, ops, st = booth_radix2(M, Q, n, aw)
    print("--- Booth (radix-2) ---")
    print("Step  Q0Q-1  Action        A(after op)  A(shifted)   Q        Q-1")
    for s in st:
        print("%-5d %-6s %-13s %-12s %-12s %-8s %s" % (s["step"], s["pair"], s["act"], s["A_op"], s["A"], s["Q"], s["Qm1"]))
    print("Product = %d (%s)  | add/sub ops = %d\n" % (p, b(p, 2 * n), ops))
    p, ops, st = booth_radix4(M, Q, n, aw)
    print("--- Modified Booth (bit-pair, radix-4) ---")
    print("Step  Triplet Digit Action        A(after op)  A(shifted)   Q        Q-1")
    for s in st:
        print("%-5d %-7s %-5d %-13s %-12s %-12s %-8s %s" % (s["step"], s["pair"], s["digit"], s["act"], s["A_op"], s["A"], s["Q"], s["Qm1"]))
    print("Product = %d (%s)  | add/sub ops = %d" % (p, b(p, 2 * n), ops))


def test_all(n=4):
    lo, hi = -(1 << (n - 1)), (1 << (n - 1)) - 1
    total2 = total4 = pairs = 0
    fewer = equal = more = 0
    max2 = max4 = 0
    wrong = 0
    hist2, hist4 = {}, {}
    for M in range(lo, hi + 1):
        for Q in range(lo, hi + 1):
            p2, o2, _ = booth_radix2(M, Q, n)
            p4, o4, _ = booth_radix4(M, Q, n)
            if p2 != M * Q or p4 != M * Q:
                wrong += 1
            pairs += 1
            total2 += o2; total4 += o4
            max2 = max(max2, o2); max4 = max(max4, o4)
            hist2[o2] = hist2.get(o2, 0) + 1
            hist4[o4] = hist4.get(o4, 0) + 1
            if o4 < o2: fewer += 1
            elif o4 == o2: equal += 1
            else: more += 1
    return dict(pairs=pairs, wrong=wrong, total2=total2, total4=total4,
                avg2=total2 / pairs, avg4=total4 / pairs, max2=max2, max4=max4,
                fewer=fewer, equal=equal, more=more, hist2=hist2, hist4=hist4)


if __name__ == "__main__":
    if len(sys.argv) == 4:
        print_trace(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
    else:
        r = test_all(4)
        print("4-bit signed operands, all %d pairs (-8..7 x -8..7)" % r["pairs"])
        print("Wrong products           :", r["wrong"])
        print("Booth       total / avg / max ops: %d / %.3f / %d" % (r["total2"], r["avg2"], r["max2"]))
        print("Modified    total / avg / max ops: %d / %.3f / %d" % (r["total4"], r["avg4"], r["max4"]))
        print("Modified fewer / equal / more ops than Booth: %d / %d / %d" % (r["fewer"], r["equal"], r["more"]))
        print("Ops histogram Booth   :", dict(sorted(r["hist2"].items())))
        print("Ops histogram Modified:", dict(sorted(r["hist4"].items())))
        print()
        print_trace(-13, 11, 6)
