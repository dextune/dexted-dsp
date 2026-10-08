from dexted_dsp import Biquad, certify, certify_cascade, verify_cascade

# Exact dyadic coefficients: total transfer function is the constant 0.75.
filters = [Biquad.from_coefficients(row, precision="float32") for row in
           [[1, -.75, 0, -.125, 0], [.75, -.09375, 0, -.75, 0]]]
print("Per-section:", [certify(f).status for f in filters])
report = certify_cascade(filters, max_gain=1.0)
print("Joint:", report["status"])
assert report["certified"] and verify_cascade(report, filters)
