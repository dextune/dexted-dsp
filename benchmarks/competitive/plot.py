#!/usr/bin/env python3
"""Deterministic, zero-dependency, GitHub-safe SVGs from *archived* raw observations."""
from __future__ import annotations
import argparse
from fractions import Fraction
import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

BG = "#0b1425"
SURFACE = "#142238"
FOREGROUND = "#f5f8ff"
MUTED = "#a9bad2"
LINE = "#30445f"
ORANGE = "#f5a56b"
CYAN = "#63ded2"


def text(x, y, content, size=18, color=FOREGROUND, weight=400, anchor="start"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" '
            f'font-family="Inter,Segoe UI,Arial,sans-serif" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}">{escape(str(content))}</text>')


def canvas(height, title, desc):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="740" height="{height}" '
        f'viewBox="0 0 740 {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(title)}</title>',
        f'<desc id="desc">{escape(desc)}</desc>',
        f'<rect width="740" height="{height}" rx="18" fill="{BG}"/>',
    ]


def number(x):
    return f"{x:,.3f}" if x < 10 else f"{x:,.2f}"


def decision(data):
    summary = data["summary"]
    a = summary["scipy_before"]["false_accepts"]
    b = summary["control_before"]["false_accepts"]
    n_fail = sum(not c["oracle_pass"] for c in data["cases"])
    vals = [a, summary["scipy_after"]["false_accepts"],
            b, summary["control_after"]["false_accepts"]]
    title = "Measured false-PASS: numerical sample vs mathematical gate"
    s = canvas(382, title, "Actual SciPy freqz_sos and python-control frequency_response on identical binary32 SOS coefficients and a 1024-point inclusive grid. After includes exact verified proof. All cases are synthetic.")
    s += [text(32, 43, "THE MISSED-PEAK GAP", 13, CYAN, 700),
          text(32, 80, "A sampled PASS isn't a proof.", 28, FOREGROUND, 750),
          text(32, 108, f"9 synthetic filters | {n_fail} exact FAIL | 1,024 grid frequencies", 15, MUTED),
          f'<rect x="28" y="136" width="684" height="212" rx="12" fill="{SURFACE}"/>']
    names = ["SciPy / before", "SciPy + proof", "control / before", "control + proof"]
    maximum = max(1, max(vals))
    for i, (name, val) in enumerate(zip(names, vals)):
        y = 169 + 49*i
        color = ORANGE if i % 2 == 0 else CYAN
        s.append(text(46, y+7, name, 16, FOREGROUND))
        s.append(f'<rect x="262" y="{y-12}" width="364" height="23" rx="6" fill="{LINE}"/>')
        width = 364 * val / maximum
        if val:
            s.append(f'<rect x="262" y="{y-12}" width="{width:.2f}" height="23" rx="6" fill="{color}"/>')
        s.append(text(665, y+7, f"{val}", 19, color, 750, "end"))
    s.append(text(30, 375, "False-PASS count among exact FAILs • synthetic stress tests, not defect prevalence", 13, MUTED))
    return "\n".join(s+["</svg>"])+"\n"


def runtime(data):
    """Paired linear p50 bars: zero-origin scale, never a deceptive speedup."""
    summary = data["summary"]
    methods = ("scipy_before", "scipy_after", "control_before",
               "control_after", "dexted_certification_only")
    names = ("SciPy / before", "SciPy + proof", "control / before",
             "control + proof", "Dexted proof only")
    scale = math.ceil(max(summary[x]["p50_ms"] for x in methods)*2)/2
    if scale <= 0:
        raise AssertionError("positive timing expected")
    s = canvas(474, "The actual latency cost of verified certification",
               "Linear zero-origin scale showing per-case-method wall-time p50 in milliseconds, with p95 in text. Same SciPy/control frequency samples before and after, proof added only after. Shared Linux CI runner and synthetic filters, not a DSP speedup.")
    s.extend([
        text(30,43,"LATENCY TRADE-OFF",14,CYAN,700),
        text(30,82,"Stronger checking takes longer.",28,FOREGROUND,750),
        text(30,110,"Wall-clock median / filter (ms), linear scale from zero",15,MUTED),
        f'<rect x="27" y="133" width="685" height="290" rx="12" fill="{SURFACE}"/>',
    ])
    gx,gw=242,344
    for i in range(4):
        x=gx+gw*i/3
        s.append(f'<path d="M {x:.1f} 152 V 397" stroke="{LINE}" stroke-dasharray="3 6"/>')
        s.append(text(round(x,1),416, f"{scale*i/3:.2f}",13,MUTED,anchor="middle"))
    for i,(method,name) in enumerate(zip(methods,names)):
        y=178+i*47
        value=summary[method]["p50_ms"]
        p95=summary[method]["p95_ms"]
        color=CYAN if "after" in method or "only" in method else ORANGE
        length=gw*value/scale
        s.extend([
            text(41,y+7,name,15,FOREGROUND,600),
            f'<rect x="{gx}" y="{y-8}" width="{max(length,2):.2f}" height="19" rx="4" fill="{color}"/>',
            text(685,y+8,f"{value:.3f} ms",16,color,700,"end"),
            text(685,y+24,f"p95 {p95:.3f} ms",10,MUTED,400,"end"),
        ])
    a=summary["scipy_after"]["p50_ms"]-summary["scipy_before"]["p50_ms"]
    b=summary["control_after"]["p50_ms"]-summary["control_before"]["p50_ms"]
    s.extend([
        text(30,449,f"Added median: SciPy +{a:.3f} ms  |  control +{b:.3f} ms",14,CYAN,650),
        text(30,467,"Differences of pooled medians, not paired overhead  •  p95 labeled separately",11,MUTED),
    ])
    return "\n".join(s+["</svg>"])+"\n"


def memory(data):
    summary = data["summary"]
    methods = ("scipy_before", "scipy_after", "control_before", "control_after")
    labels = ("SciPy", "SciPy + Dexted", "python-control", "control + Dexted")
    vals = [summary[m]["peak_python_kib_p50"] for m in methods]
    maximum = max(vals) if max(vals) else 1
    s=canvas(350, "Measured Python allocation peak, median",
             "tracemalloc instrumented Python allocations only, not RSS or native buffers. 30 repeats per case and operation, separate from wall-time measurement.")
    s += [text(32, 43, "ALLOCATION FOOTPRINT", 13, CYAN, 700),
          text(32, 80, "We expose memory cost too.", 26, FOREGROUND, 750),
          text(32, 108, "Median peak Python allocations (KiB), not total process RSS", 15, MUTED),
          f'<rect x="28" y="133" width="684" height="188" rx="12" fill="{SURFACE}"/>']
    for i,(m,label,val) in enumerate(zip(methods,labels,vals)):
        y=166+i*44
        color=CYAN if "after" in m else ORANGE
        s += [text(44,y+6,label,15,FOREGROUND),
              f'<rect x="235" y="{y-8}" width="370" height="20" rx="5" fill="{LINE}"/>',
              f'<rect x="235" y="{y-8}" width="{max(0,370*val/maximum):.2f}" height="20" rx="5" fill="{color}"/>',
              text(684,y+7,number(val),16,color,700,"end")]
    s.append(text(30,341,"Separate instrumented trials; native NumPy/C allocations excluded (see protocol)",12,MUTED))
    return "\n".join(s+["</svg>"])+"\n"



def mobile(data, measure):
    """Narrow device chart; 390 CSSpx-wide rather than a scaled-down desktop."""
    info={
        "decision":("MISSED VIOLATIONS","Before vs after proof","false PASS","false_accepts",
                    "Both samplers miss the SAME constructed peak",630),
        "runtime":("VERIFICATION COST","Proof is slower","ms (median)","p50_ms",
                   "Cost is higher; no sampling speedup claim",630),
        "memory":("MEMORY FOOTPRINT","Python-traced peak","KiB (median)","peak_python_kib_p50",
                   "Native NumPy/C allocations and RSS excluded",630)
    }
    eyebrow,title,unit,field,note,height=info[measure]
    methods=("scipy_before","scipy_after","control_before","control_after")
    scores=[data["summary"][m][field] for m in methods]
    scale=max(1e-12,max(scores))
    s=[
        f'<svg xmlns="http://www.w3.org/2000/svg" width="390" height="{height}" viewBox="0 0 390 {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(title)}</title>',
        f'<desc id="desc">{escape(note)}. Same 9 synthetic filters and 30 repeat observations.</desc>',
        f'<rect width="390" height="{height}" rx="16" fill="{BG}"/>',
        text(26,46,eyebrow,14,CYAN,700),
        text(26,83,title,25,FOREGROUND,750),
        text(26,114,unit+" · 9 synthetic filters",16,MUTED),
    ]
    for i,(method,value) in enumerate(zip(methods,scores)):
        if i in (0,2):
            group="SciPy freqz_sos" if i==0 else "python-control"
            s.append(text(26,159+(i//2)*223,group,21,FOREGROUND,700))
        label="BEFORE · grid" if i%2==0 else "AFTER · grid + proof"
        y=201+i*99+(i//2)*24
        color=ORANGE if i%2==0 else CYAN
        s.extend([
            text(26,y,label,17,FOREGROUND,650),
            f'<rect x="26" y="{y+16}" width="273" height="22" rx="5" fill="{LINE}"/>',
            f'<rect x="26" y="{y+16}" width="{273*value/scale:.3f}" height="22" rx="5" fill="{color}"/>',
            text(365,y+34,number(value) if measure!="decision" else str(value),
                 18,color,700,"end")
        ])
    s.extend([text(26,604,note,12,MUTED),"</svg>"])
    return "\n".join(s)+"\n"



def hidden_peak_values(data):
    """Recompute the predeclared hidden peak from archived *represented* SOS.

    The exact whole-band maximum 2 is special to this constructed filter:
    H(z)=alpha*(1-z^-2)/(1+(1-alpha)*z^-2), 0<alpha<1.
    |H|²=4*alpha²*(1-cos²(w))/(alpha²+4*(1-alpha)*cos²(w)) <=4;
    equality occurs at w=pi/2. Hence maximum 2 is analytical, NOT a
    higher-density sample or a claim about runtime floating-point arithmetic.
    """
    chosen = [c for c in data["cases"] if c["id"] == "hidden-peak-adversarial"]
    if len(chosen) != 1:
        raise ValueError("missing exact hidden-peak archived case")
    case = chosen[0]
    if case["sections"] != 1 or case["oracle_verdict"] != "gain_limit_not_met":
        raise ValueError("wrong archived oracle or section count")
    for backend in ("scipy", "control"):
        if case["decisions"][backend+"_before"] is not True or case["decisions"][backend+"_after"] is not False:
            raise ValueError("archived Before/After does not exhibit a missed peak")
    b0,b1,b2,a0,a1,a2 = map(Fraction,case["sos"][0])
    alpha = b0
    if not (0 < alpha < 1 and b1 == 0 and b2 == -alpha and
            a0 == 1 and a1 == 0 and a2 == 1-alpha and Fraction(case["gain_limit"]) == 1):
        raise ValueError("not the predeclared dyadic hidden-peak filter")
    sampled = 0.0
    for k in range(1024):
        w = math.pi*k/1023
        z2 = complex(math.cos(2*w), -math.sin(2*w))
        measured = abs(float(alpha)*(1-z2))/abs(1+float(1-alpha)*z2)
        sampled = max(sampled,measured)
    maximum = abs((b0-b2)/(a0-a2))  # exact rational at pi/2, global max by bound above
    if maximum != 2 or not (0.03974 < sampled < 0.03975):
        raise AssertionError("numerical/analytic hook drift")
    return {"sampled":sampled,"exact":float(maximum),"threshold":float(case["gain_limit"])}


def peak_gap(data, mobile=False):
    """Prominent, linear-scale evidence with the spec limit drawn on BOTH rows."""
    v = hidden_peak_values(data)
    sampled, maximum, limit = v["sampled"],v["exact"],v["threshold"]
    if mobile:
        s = [
            '<svg xmlns="http://www.w3.org/2000/svg" width="390" height="606" viewBox="0 0 390 606" role="img" aria-labelledby="title desc">',
            '<title id="title">A frequency grid passes a violating filter</title>',
            '<desc id="desc">A synthetic high-Q filter: a 1024-point grid observes only '+f'{sampled:.5f}'+
            ', so a strict limit of 1 looks met. Algebra proves the actual global peak is exactly 2, so Dexted rejects it. Same represented coefficients, linear scale. Sampling does not promise certification.</desc>',
            f'<rect width="390" height="606" rx="16" fill="{BG}"/>',
            text(22,39,"SAME FILTER  /  DIFFERENT RESULT",13,CYAN,700),
            text(22,75,"A hidden 50x gap",27,FOREGROUND,750),
            text(22,102,"Gain limit: strictly below 1.0",16,MUTED),
        ]
        for idx,(tag,caption,value,judgment,color) in enumerate((
            ("BEFORE","1,024-point sampled estimate",sampled,"FALSE PASS",ORANGE),
            ("AFTER","Exact whole-band maximum",maximum,"VIOLATION FOUND",CYAN),
        )):
            y=128+idx*199
            s.extend([
                f'<rect x="18" y="{y}" width="354" height="185" rx="12" fill="{SURFACE}"/>',
                text(34,y+30,tag,14,color,700),
                text(34,y+53,caption,15,MUTED),
                text(34,y+105,f"{value:.5f}" if idx==0 else "2.00000",37,FOREGROUND,750),
                text(352,y+102,judgment,11,color,750,"end"),
                f'<rect x="34" y="{y+128}" width="319" height="21" rx="6" fill="{LINE}"/>',
                f'<rect x="34" y="{y+128}" width="{319*value/maximum:.3f}" height="21" rx="6" fill="{color}"/>',
                f'<path d="M {34+319*limit/maximum:.1f} {y+119} v 41" stroke="#f2d07a" stroke-width="2" stroke-dasharray="3 4"/>',
                text(34,y+170,"0",13,MUTED),
                text(34+319*limit/maximum,y+170,"limit 1.0",13,"#f2d07a",600,"middle"),
                text(353,y+170,"2",13,MUTED,400,"end"),
            ])
        s.extend([
            text(22,552,"Numeric sampler is not a certifier.",15,MUTED),
            text(22,576,"Constructed synthetic fixture; not a field error rate.",12,MUTED),
            "</svg>",
        ])
    else:
        s=canvas(463,"One synthetic filter, two incompatible verdicts",
                 f"Same binary32 SOS coefficients. 1024-point inclusive frequency grid sees {sampled:.5f}, below strict gain limit 1, returning false PASS. The exact algebraic whole-band gain is 2 and Dexted rejects the filter. Two horizontal bars share a linear 0 to 2 axis and threshold line.")
        s.extend([
            text(28,42,"THE MISSING PEAK",14,CYAN,700),
            text(28,83,"The grid says PASS. The proof says FAIL.",27,FOREGROUND,750),
            text(28,112,"One constructed float32 high-Q filter | same coefficients | limit < 1.0",15,MUTED),
            f'<rect x="24" y="134" width="692" height="125" rx="12" fill="{SURFACE}"/>',
            f'<rect x="24" y="268" width="692" height="125" rx="12" fill="{SURFACE}"/>',
        ])
        for idx,(tag,caption,value,judgment,color) in enumerate((
            ("BEFORE / SAMPLED","1,024-point grid estimate",sampled,"FALSE PASS",ORANGE),
            ("AFTER / PROVED","Exact global maximum",maximum,"VIOLATION FOUND",CYAN),
        )):
            y=134+idx*134
            sx,sw=360,320
            s.extend([
                text(42,y+32,tag,14,color,700),
                text(42,y+56,caption,15,MUTED),
                text(42,y+103,f"{value:.5f}" if idx==0 else "2.00000",36,FOREGROUND,750),
                text(690,y+29,judgment,15,color,700,"end"),
                f'<rect x="{sx}" y="{y+68}" width="{sw}" height="26" rx="6" fill="{LINE}"/>',
                f'<rect x="{sx}" y="{y+68}" width="{sw*value/maximum:.3f}" height="26" rx="6" fill="{color}"/>',
                f'<path d="M {sx+sw*limit/maximum:.1f} {y+54} v 56" stroke="#f2d07a" stroke-width="2" stroke-dasharray="4 4"/>',
            ])
        s.extend([
            text(360,414,"0",13,MUTED),
            text(520,414,"gain limit 1.0",13,"#f2d07a",600,"middle"),
            text(680,414,"2",13,MUTED,400,"end"),
            text(28,445,"Linear gain scale  |  one sampled false PASS  |  full-band mathematical violation",13,MUTED),
            "</svg>",
        ])
    return "\n".join(s)+"\n"


def generate(data):
    return {"decision.svg":decision(data),"runtime.svg":runtime(data),"memory.svg":memory(data),
            "decision-mobile.svg":mobile(data,"decision"),
            "runtime-mobile.svg":mobile(data,"runtime"),
            "memory-mobile.svg":mobile(data,"memory"),
            "peak-gap.svg":peak_gap(data),
            "peak-gap-mobile.svg":peak_gap(data,mobile=True)}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    data=json.loads(args.input.read_text(encoding="utf-8"))
    figures=generate(data)
    if not args.check: args.out.mkdir(parents=True,exist_ok=True)
    for name, content in figures.items():
        path=args.out/name
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8")!=content:
                raise SystemExit("stale or unverified graph: "+str(path))
        else:
            path.write_text(content,encoding="utf-8")
        print(name, "checked" if args.check else "generated")


if __name__=="__main__": main()
