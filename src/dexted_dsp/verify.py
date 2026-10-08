"""Independent exact-rational certificate consumers."""
from fractions import Fraction as F
from math import comb
from .model import Biquad, positive_gamma
from .request import bounded_take
from . import reference


def verify_biquad(report: dict, expected: Biquad, max_gain=1.0) -> bool:
    try:
        if not isinstance(report,dict) or not isinstance(expected,Biquad):
            return False
        if report.get('schema')!='dexted-dsp/biquad/v1' or report.get('status')!='certified' or report.get('certified') is not True or report.get('strict') is not True:
            return False
        gamma=positive_gamma(max_gain)
        if report.get('coefficients_hex')!=expected.hex_coefficients() or report.get('max_gain_hex')!=gamma.hex():
            return False
        if not reference.reference_decision(expected,gamma):
            return False
        from .biquad import certify
        return report == certify(expected,gamma).as_dict()
    except (TypeError,ValueError,OverflowError,ArithmeticError,MemoryError):
        return False


def verify_cascade(report: dict, expected_sections, max_gain=1.0) -> bool:
    try:
        rows=bounded_take(expected_sections,32,'SOS sections')
        if not 1<=len(rows)<=32 or any(not isinstance(s,Biquad) for s in rows):
            return False
        if not isinstance(report,dict) or len(report)>16:
            return False
        fields={'schema','method','status','certified','strict','denominator_stable',
                'max_gain_hex','sections_hex','degree','scope','nodes','max_depth','cover'}
        if not set(report).issubset(fields):
            return False
        if (report.get('schema')!='dexted-dsp/cascade/v1'
            or report.get('method')!='integer-bernstein-subdivision'
            or report.get('status')!='certified'
            or report.get('certified') is not True or report.get('strict') is not True
            or report.get('denominator_stable') is not True
            or report.get('sections_hex')!=[s.hex_coefficients() for s in rows]
            or report.get('max_gain_hex')!=positive_gamma(max_gain).hex()):
            return False
        nodes,md,degree=report.get('nodes'),report.get('max_depth'),report.get('degree')
        if (type(nodes) is not int or not 1<=nodes<=100000
            or type(md) is not int or not 0<=md<=128
            or type(degree) is not int or not 0<=degree<=64):
            return False
        cover=report.get('cover')
        if not isinstance(cover,list) or not 1<=len(cover)<=min(nodes,50000):
            return False
        for item in cover:
            if not isinstance(item,list) or len(item)!=2:
                return False
            index,depth=item
            if type(index) is not int or type(depth) is not int or not 0<=depth<=md:
                return False
            if index<0 or index.bit_length()>depth or index>=1<<depth:
                return False
        p,stable=reference.polynomial(rows,max_gain)
        if not stable or degree!=len(p)-1:
            return False
        if any(max(abs(x.numerator).bit_length(),x.denominator.bit_length())>262144 for x in p):
            return False
        intervals=sorted((F(i,1<<d),F(i+1,1<<d)) for i,d in cover)
        last=F(0)
        for lo,hi in intervals:
            if lo!=last:
                return False
            h,m,n=hi-lo,hi+lo-1,len(p)-1
            transformed=[sum((p[j]*comb(j,k)*h**k*m**(j-k) for j in range(k,n+1)),F(0)) for k in range(n+1)]
            if min(reference.bernstein(transformed))<=0:
                return False
            last=hi
        return last==1
    except (KeyError,TypeError,ValueError,OverflowError,ZeroDivisionError,ArithmeticError,MemoryError):
        return False
