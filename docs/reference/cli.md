# Command-line interface

The CLI processes JSON coefficient/config files without executing them. It is an **offline verifier**, not an audio processor.

```bash
dexted-dsp check examples/safe.json --output certificate.json
dexted-dsp verify examples/safe.json certificate.json
# The following example deliberately fails the strict-gain condition:
dexted-dsp check examples/hidden_peak.json
```

| Exit code | Meaning |
|---|---|
| `0` | Certified, or certificate verified |
| `1` | Condition failed / certificate invalid |
| `2` | Invalid input or execution error |
| `3` | Unknown due to proof resource limits |

For automated deployment gates, accept **only zero**. A failed sufficient-condition certificate does not prove that every surrounding device or application is unstable.

[Full CLI contract](API.md) · [Test guide](../en/guides/TESTING.md)
