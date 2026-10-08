"""SciPy filter design -> deployed float32 -> exact full-band inspection."""
from scipy.signal import butter
from dexted_dsp import inspect_sos,verify_inspection

sos = butter(8,0.2,output='sos')
report = inspect_sos(sos,precision='float32',max_gain=1.01,fs=48000)
print(report.status,report.reason)
print(report.gain_bounds.as_dict() if report.gain_bounds is not None else 'unavailable')
assert report.certified
assert verify_inspection(report.as_dict(),sos,precision='float32',max_gain=1.01,fs=48000)
