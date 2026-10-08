#!/usr/bin/env python3
"""Exercise the documented Python API and CLI on expected success/failure cases."""
from pathlib import Path
import copy
import json
import subprocess
import sys
import tempfile
from dexted_dsp import Biquad, certify, certify_cascade, from_sos, verify_biquad, verify_cascade

ROOT=Path(__file__).resolve().parents[1]

def main():
    passed=[]
    f=Biquad.from_coefficients([.25,0,0,-.5,0],precision='float32')
    proof=certify(f)
    assert proof.status=='certified' and verify_biquad(proof.as_dict(),f)
    passed.append('python_basic_and_rational_recheck')
    assert not certify(Biquad.from_coefficients([1,0,0,0,0])).certified
    passed.append('strict_equality_is_rejected')
    assert not verify_biquad(proof.as_dict(),f,max_gain=2.0)
    passed.append('certificate_threshold_binding')
    sos=from_sos([[1,-.75,0,1,-.125,0],[.75,-.09375,0,1,-.75,0]],precision='float32')
    p=certify_cascade(sos)
    assert p['certified'] and verify_cascade(p,sos)
    passed.append('cascade_compensation')
    q=copy.deepcopy(p);q['cover']=[]
    assert not verify_cascade(q,sos)
    passed.append('tampered_cover_rejected')
    with tempfile.TemporaryDirectory() as tmp:
        out=Path(tmp)/'certificate.json'
        def command(label,*args,expected=0):
            run=subprocess.run([sys.executable,'-m','dexted_dsp',*map(str,args)],
                               cwd=ROOT,text=True,capture_output=True,timeout=30)
            assert run.returncode==expected,(label,run.returncode,run.stdout,run.stderr)
            passed.append(label)
            return run.stdout
        command('cli_safe','check','examples/safe.json','--output',out)
        command('cli_verify','verify','examples/safe.json',out)
        command('cli_gain_limit_failure','check','examples/hidden_peak.json',expected=1)
        command('cli_unknown_is_exit_3','check','examples/budget_limited.json','--max-depth',0,expected=3)
        command('cli_retry_succeeds','check','examples/budget_limited.json','--max-depth',16)
        malformed=Path(tmp)/'bad.json';malformed.write_text('{bad',encoding='utf-8')
        command('cli_invalid_input_is_exit_2','check',malformed,expected=2)
        command('cli_mismatched_input_rejected','verify','examples/hidden_peak.json',out,expected=1)
    print(json.dumps({'status':'passed','checks':len(passed),'passed':passed},indent=2))

if __name__=='__main__':
    main()
