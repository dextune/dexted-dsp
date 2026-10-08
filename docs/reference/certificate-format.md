# Certificate representation and trust

Certificates bind the exact decoded input coefficients and the strict gain threshold. Save them as JSON with `dexted-dsp check ... --output certificate.json` and recheck them with `dexted-dsp verify <input.json> <certificate.json>`.

- For biquads, exact-integer sign witnesses support a universal gain-condition decision. The verifier recomputes the rational decision; witness strings are **not** blindly trusted.
- For cascades, the verifier reconstructs the frequency-gap polynomial, threshold, and rational dyadic cover. A budget exhaustion may yield `unknown`, which **must not be treated as a pass**.
- Input binary32 conversion is explicit; raw decimal text is parsed to binary64 first.
- Certificates cover the modeled constant-coefficient filter, **not** finite-word-length processor overflow, all realtime states, or physical safety.

[Canonical schema and API specification](API.md) · [Mathematical derivation](../research/README.md)
