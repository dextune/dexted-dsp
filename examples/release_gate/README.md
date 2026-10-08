# Fail-closed CI release gate

The JSON is the final deployed, normalized coefficient representation (five values per SOS section for the CLI; `a0=1` is implicit). Always round it in the deployment/export pipeline **before** certification.

```bash
dexted-dsp inspect examples/safe.json --output proof.json --report inspection.md
dexted-dsp verify examples/safe.json proof.json
```

Only exit `0` is success. `1` means the strict stability/gain conditions were not established (`rejected`); `2` is malformed/invalid input; `3` is budget-limited `unknown`. Never convert `unknown` to a PASS. `verify` repeats the exact mathematical check on caller-supplied expected input; the SHA-256 input binding is not a signature or a security certificate.

See [integration contract](../../docs/product/inspection.md).
