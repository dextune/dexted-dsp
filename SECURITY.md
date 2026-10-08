# Security and assurance boundaries

No external safety certification or formal proof-assistant verification is claimed.
Do not use this research alpha as the sole control protecting people or equipment.
A mathematical pass does not certify runtime arithmetic, clipping, a nonlinear model
or a whole device. Inspect `docs/API.md` and the mathematics before integration.

The CLI reads JSON and writes optional reports; it does not play audio, execute
uploaded plugins or contact a service. Arbitrary-precision arithmetic can consume
substantial resources; size limits do not make the checker a hostile-input sandbox.
Run untrusted input in a separately resource-limited process.

Proof JSON files are not signed. Always supply the expected coefficients and threshold
to the verifier; never authorize deployment from `certified: true` alone.
Native raw pointer APIs require correctly sized caller-owned buffers and explicit
handling of negative error codes. Load only locally trusted native libraries.

After publishing, maintainers should enable GitHub private vulnerability reporting.
No maintainer email or reporting endpoint is invented in this generated bundle.
