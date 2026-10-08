from dexted_dsp import Biquad, certify, verify_biquad

# Explicit deployed coefficients; no audio is played by this example.
f = Biquad.from_coefficients([0.25, 0, 0, -0.5, 0], precision="float32")
report = certify(f, max_gain=1.0)
print(report.status)
print("Independent exact-rational recheck:", verify_biquad(report.as_dict(), f))
assert report.certified
