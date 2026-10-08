#!/usr/bin/env python3
"""Deterministic, zero-dependency, GitHub-safe SVGs from *archived* raw observations."""
from __future__ import annotations
import argparse
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
    summary = data["summary"]
    methods = ("scipy_before", "scipy_after", "control_before",
               "control_after", "dexted_certification_only")
    labels = ("SciPy", "SciPy + Dexted", "python-control", "control + Dexted", "Dexted proof only")
    observed = [summary[m]["p50_ms"] for m in methods]
    # Logarithmic bar distance makes sub-millisecond and multi-ms samples both readable.
    minimum = min(v for v in observed if v > 0)
    maximum = max(observed)
    lo = math.floor(math.log10(minimum))
    hi = math.ceil(math.log10(maximum))
    if hi <= lo: hi=lo+1
    s = canvas(452, "Before/after per-filter runtime, p50 and p95",
               "GitHub Actions one shared Linux host; logarithmic axis, milliseconds. SciPy and control compare exactly matched before/after operations; Dexted proof and verifier add cost. No sampling speedup claim.")
    s += [text(32, 43, "THE VERIFICATION COST", 13, CYAN, 700),
          text(32, 80, "Proof costs time. Here's the bill.", 26, FOREGROUND, 750),
          text(32, 108, "Wall time / filter, median + p95 in ms | shared Linux CI host", 15, MUTED),
          f'<rect x="28" y="132" width="684" height="286" rx="12" fill="{SURFACE}"/>']
    gx, gw = 242, 335
    for x in range(lo, hi+1):
        xpos = gx + gw*(x-lo)/(hi-lo)
        s.append(f'<path d="M {xpos:.2f} 152 V 370" stroke="{LINE}" stroke-dasharray="3 5"/>')
        s.append(text(round(xpos,2), 395, f"10^{x}", 13, MUTED, anchor="middle"))
    for i, (method, label) in enumerate(zip(methods,labels)):
        y = 175+i*42
        median = summary[method]["p50_ms"]
        p95 = summary[method]["p95_ms"]
        color = CYAN if "after" in method or "only" in method else ORANGE
        w = max(3, (math.log10(max(median,10**lo))-lo)/(hi-lo)*gw)
        s.append(text(45, y+7, label, 15, FOREGROUND))
        s.append(f'<rect x="{gx}" y="{y-7}" width="{w:.2f}" height="16" rx="4" fill="{color}"/>')
        s.append(text(685, y+7, number(median), 16, color, 700, "end"))
        s.append(text(685, y+22, f"p95 {number(p95)}", 10, MUTED, anchor="end"))
    s.append(text(30, 443, "Log10 scale | the total After workflow includes the same sampler + certified proof check", 12, MUTED))
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


def generate(data):
    return {"decision.svg":decision(data),"runtime.svg":runtime(data),"memory.svg":memory(data)}


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
