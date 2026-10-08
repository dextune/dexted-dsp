"""Slower independently expressed Fraction arithmetic for cross-checking.

    This is a second implementation in the same repository, not an external
    independent audit or a proof-assistant formalization.
"""
from fractions import Fraction as F
from math import comb
from .model import Biquad, positive_gamma


def square(x, y, z):
    return [(x-z)**2+y*y, 2*y*(x+z), 4*x*z]


def multiply(a, b):
    out = [F(0)] * (len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x*y
    return out


def polynomial(sections, max_gain):
    gamma = F(positive_gamma(max_gain))
    num, den = [F(1)], [F(1)]
    stable = True
    for section in sections:
        b0, b1, b2, a1, a2 = map(F, section.coefficients)
        stable = stable and abs(a2) < 1 and 1+a1+a2 > 0 and 1-a1+a2 > 0
        num = multiply(num, square(b0, b1, b2))
        den = multiply(den, square(F(1), a1, a2))
    gap = [gamma*gamma*d-n for n, d in zip(num, den)]
    while len(gap) > 1 and gap[-1] == 0:
        gap.pop()
    return gap, stable


def reference_decision(section: Biquad, max_gain=1.0) -> bool:
    p, stable = polynomial([section], max_gain)
    p += [F(0)]*(3-len(p))
    c, b, a = p
    points = [F(-1), F(1)]
    if a > 0:
        vertex = -b/(2*a)
        if -1 < vertex < 1:
            points.append(vertex)
    return bool(stable and min(a*x*x+b*x+c for x in points) > 0)


def bernstein(p):
    n = len(p)-1
    a = [sum((p[j]*comb(j,k)*2**k*(-1)**(j-k)
              for j in range(k,n+1)), F(0)) for k in range(n+1)]
    return [sum((a[k]*F(comb(i,k),comb(n,k))
                 for k in range(i+1)), F(0)) for i in range(n+1)]
