# Synthetic designed-SOS pilot — revision provenance

This folder preserves both original and corrected **private local** pilot measurements. Both were generated from 25 **synthetic designed/constructed** fixed SOS filters; neither measures real product incidence or sound quality. No independent external benchmark has been conducted.

| File | Source integrity / intended use |
|---|---|
| `designed_sos_20261008_linux_shared.json` | **Historical first local run**. Its measured `src/dexted_dsp/biquad.py` and `cascade.py` were shorter formatting variants, so strict source hash validation against GitHub `main` correctly fails. Preserve its raw timings and old source hashes unchanged; `--allow-source-drift` checks only saved arithmetic and archived fixture identity. **Do not cite as measurements of the current GitHub source checkout.** |
| `designed_sos_20261008_main_matched.json` | **Separate complete rerun** after restoring those two modules byte-for-byte from current GitHub. Both Git blob SHA values matched the remote source before measuring. The full 25-case, 30-trial raw dataset passes strict audit against the actual `main` modules. |

```bash
python benchmarks/suites/audit_pilot_v2.py validation/pilot_v2/designed_sos_20261008_main_matched.json
python benchmarks/suites/audit_pilot_v2.py validation/pilot_v2/designed_sos_20261008_linux_shared.json --allow-source-drift
```

Do not overwrite either result or turn this small synthetic experiment into a general claim about speedups, field failure rates, independent validation or security certification. See [protocol details](../../benchmarks/suites/PROTOCOL_V2.md).
