#!/usr/bin/env python3
"""Render each chart separately from recorded measurements; no invented data."""
from pathlib import Path
import argparse
import json
import numpy as np
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
LABELS={'ordinary':'Ordinary filters','high_q':'High-Q stress filters',
        'near_threshold':'Near gain threshold','unstable':'Unstable denominators'}
METHODS={'integer':'Exact integer', 'grid1024':'Grid: 1,024 points',
         'grid16384':'Grid: 16,384 points','float64_algebraic':'Float64 algebraic (not certified)'}


def render(results, destination, show=False):
    data=json.loads(Path(results).read_text())
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=True)
    def save(fig,name):
        fig.tight_layout()
        fig.savefig(destination/(name+'.png'),dpi=180,bbox_inches='tight')
        fig.savefig(destination/(name+'.svg'),bbox_inches='tight')
    families=list(LABELS)
    fig,ax=plt.subplots(figsize=(11.2,6.2))
    y=np.arange(len(families));width=.18
    for j,(method,label) in enumerate(METHODS.items()):
        samples=[np.asarray(data['families'][f]['raw_us_per_filter'][method]) for f in families]
        centers=np.array([np.median(x) for x in samples])
        # Whiskers are measured min/max across trials, not confidence intervals.
        errors=np.array([[m-x.min() for m,x in zip(centers,samples)],
                         [x.max()-m for m,x in zip(centers,samples)]])
        ax.barh(y+(j-1.5)*width,centers,height=width,label=label,xerr=errors,
                error_kw={'capsize':2,'linewidth':.8})
    ax.set_yticks(y,[LABELS[f] for f in families]);ax.invert_yaxis();ax.set_xscale('log')
    ax.set_xlabel('Microseconds per filter — lower is faster (log scale)')
    ax.set_title(f'Native C++: latency and the cost of exact arithmetic\n{data["protocol"]["trials"]} trials; bars = median, whiskers = observed range')
    ax.grid(axis='x',alpha=.2);ax.legend(loc='lower right',fontsize=9)
    save(fig,'native_latency')
    if show:plt.show()
    plt.close(fig)

    fig,ax=plt.subplots(figsize=(10.4,5.5))
    names=list(METHODS);positions=np.arange(len(names));family=data['families']['high_q']
    for offset,key,label in [(-.18,'false_accepts','False accept (missed violation)'),(.18,'false_rejects','False reject')]:
        values=[family['correctness'][m][key] for m in names]
        bars=ax.bar(positions+offset,values,width=.34,label=label)
        ax.bar_label(bars,padding=3)
    ax.set_xticks(positions,['Exact\ninteger','Grid\n1,024','Grid\n16,384','Float64\nalgebraic'])
    ax.set_ylabel('Cases disagreeing with the exact-rational reference')
    ax.set_title(f'High-Q stress set: errors on {family["n"]:,} fixed filters\nConstructed stress distribution — not a real-world failure rate')
    ax.set_ylim(0,max(family['correctness'][m]['false_accepts'] for m in names)*1.22+1)
    ax.legend();ax.grid(axis='y',alpha=.2)
    save(fig,'high_q_correctness');plt.close(fig)

    fig,ax=plt.subplots(figsize=(10.4,4.8))
    methods=['python_integer_api','fraction_reference','scipy_freqz1024']
    values=[data['python_high_q']['median_us'][m] for m in methods]
    bars=ax.barh(['Exact Python API','Exact Fraction reference','SciPy freqz: 1,024 points'],values)
    ax.bar_label(bars,fmt='%.2f',padding=5);ax.invert_yaxis();ax.set_xlim(0,max(values)*1.22)
    ax.set_xlabel(f'Microseconds per filter — median of {data["protocol"]["trials"]} trials')
    ax.set_title(f'Python-level comparison: includes per-filter API overhead\n{data["python_high_q"]["n"]} high-Q filters; not a native-kernel speed comparison')
    ax.grid(axis='x',alpha=.2)
    save(fig,'python_latency');plt.close(fig)

    fig,ax=plt.subplots(figsize=(10.4,5.4))
    alpha=2.**-14
    def magnitude(w):
        z=np.exp(-1j*w)
        return np.abs(alpha*(1-z*z)/(1+(1-alpha)*z*z))
    w=np.linspace(.497*np.pi,.503*np.pi,12001)
    grid=np.linspace(0,np.pi,1024);selected=grid[(grid>=w.min())&(grid<=w.max())]
    ax.plot(w/np.pi,magnitude(w),label='Response curve for illustration')
    ax.scatter(selected/np.pi,magnitude(selected),s=60,marker='x',label='1,024-point grid samples')
    ax.axhline(1,linestyle='--',label='Requested strict gain limit: 1')
    ax.set_xlabel('Normalized frequency (omega / pi)');ax.set_ylabel('Magnitude')
    ax.set_title('A narrow peak between sample points\nExact algebra: magnitude at omega = pi/2 is 2')
    ax.set_ylim(0,2.2);ax.legend(loc='upper right');ax.grid(alpha=.2)
    save(fig,'hidden_peak');plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--results',type=Path,default=ROOT/'benchmarks/results/benchmark.json')
    p.add_argument('--out',type=Path,default=ROOT/'benchmarks/figures')
    p.add_argument('--show',action='store_true')
    args=p.parse_args();render(args.results,args.out,args.show)
