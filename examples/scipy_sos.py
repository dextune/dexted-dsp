# Optional dependency: pip install scipy
from scipy.signal import butter
from dexted_dsp import from_sos, certify_cascade, verify_cascade

sos = butter(4, 0.2, output="sos")
# Inspect after float32 deployment rounding, not only before rounding.
sections = from_sos(sos, precision="float32")
proof = certify_cascade(sections, max_gain=1.01)
print(proof["status"])
assert proof["certified"] and verify_cascade(proof, sections, 1.01)
