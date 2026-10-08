"""Integer Bernstein subdivision: proof-carrying sufficient cascade check."""
from __future__ import annotations
from math import comb, lcm
from .model import Biquad, positive_gamma
from .biquad import integer_coefficients, squared_coefficients

MAX_SECTIONS = 32
SCHEMA = 'dexted-dsp/cascade/v1'


def validate_sections(sections) -> tuple[Biquad, ...]:
    rows = tuple(sections)
    if not 1 <= len(rows) <= MAX_SECTIONS or any(not isinstance(s, Biquad) for s in rows):
        raise ValueError(f"one to {MAX_SECTIONS} Biquad objects are required")
    return rows


def gap_polynomial(sections, gamma):
    n, d, stable = [1], [1], True
    for section in sections:
        (b0, b1, b2, a1, a2), scale = integer_coefficients(section.coefficients)
        stable = stable and abs(a2)<scale and scale+a1+a2>0 and scale-a1+a2>0
        n = mul(n, list(squared_coefficients(b0,b1,b2)))
        d = mul(d, list(squared_coefficients(scale,a1,a2)))
    gn, gd = gamma.as_integer_ratio()
    p = [gn*gn*y-gd*gd*x for x,y in zip(n,d)]
    while len(p)>1 and p[-1]==0:
        p.pop()
    return p, bool(stable)

def mul(a:list[int],b:list[int])->list[int]:
    out=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]+=x*y
    return out


def to_bernstein_scaled(p:list[int])->list[int]:
    n=len(p)-1
    choose=[comb(n,k) for k in range(n+1)];L=lcm(*choose)
    a=[sum(p[j]*comb(j,k)*2**k*(-1)**(j-k) for j in range(k,n+1)) for k in range(n+1)]
    return [sum(a[k]*comb(i,k)*(L//choose[k]) for k in range(i+1)) for i in range(n+1)]


def split_scaled(b:list[int])->tuple[list[int],list[int]]:
    # Multiply EACH child by 2^degree; sign information remains exact.
    n=len(b)-1;v=b[:];left=[b[0]<<n];right=[b[-1]<<n]
    for r in range(1,n+1):
        v=[x+y for x,y in zip(v[:-1],v[1:])]
        left.append(v[0]<<(n-r));right.append(v[-1]<<(n-r))
    return left,list(reversed(right))


def prove_positive(p:list[int],max_depth:int=60,max_nodes:int=20000)->dict:
    if max_depth<0 or max_nodes<1:raise ValueError('invalid budgets')
    stack=[(to_bernstein_scaled(p),0,0)];nodes=0;leaves=[];unknown=False;max_seen=0
    while stack:
        if nodes >= max_nodes:
            unknown = True
            break
        b,index,depth=stack.pop();nodes+=1;max_seen=max(max_seen,depth)
        if b[0]<=0 or b[-1]<=0:
            k=index if b[0]<=0 else index+1
            return dict(verdict='condition_failed',nodes=nodes,max_depth=max_seen,
                        witness_t=[k,depth],reason='exact nonpositive gap at dyadic t, c=2t-1')
        if min(b)>0:
            leaves.append([index,depth]);continue
        if depth>=max_depth or nodes>=max_nodes:
            unknown=True
            if nodes>=max_nodes:break
            continue
        lo,hi=split_scaled(b)
        stack.append((hi,2*index+1,depth+1));stack.append((lo,2*index,depth+1))
    if unknown:return dict(verdict='unknown',nodes=nodes,max_depth=max_seen,reason='budget exhausted')
    return dict(verdict='certified',nodes=nodes,max_depth=max_seen,
                cover=leaves,degree=len(p)-1)



def certify_cascade(sections, max_gain=1.0, *, max_depth=48, max_nodes=20000) -> dict:
    """Return certified / condition_failed / unknown / denominator_not_schur.

    Every supplied section must have a strictly stable denominator, even if
    its poles would be canceled in the total transfer function. Finite budgets
    make this a sufficient procedure, not a complete positivity decision.
    """
    rows = validate_sections(sections)
    gamma = positive_gamma(max_gain)
    if type(max_depth) is not int or not 0 <= max_depth <= 128:
        raise ValueError("max_depth must be an integer in [0,128]")
    if type(max_nodes) is not int or not 1 <= max_nodes <= 100000:
        raise ValueError("max_nodes must be an integer in [1,100000]")
    p, stable = gap_polynomial(rows, gamma)
    report = (prove_positive(p, max_depth, max_nodes) if stable else
              {'verdict': 'denominator_not_schur', 'nodes': 0})
    report['status'] = report.pop('verdict')
    report.update(schema=SCHEMA, method='integer-bernstein-subdivision',
                  certified=report['status']=='certified', strict=True,
                  denominator_stable=stable, max_gain_hex=gamma.hex(),
                  sections_hex=[s.hex_coefficients() for s in rows],
                  degree=len(p)-1,
                  scope='fixed real LTI cascade; all section denominators stable; no runtime-roundoff guarantee')
    return report
