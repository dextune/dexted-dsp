# Provenance and dependencies

The Python integer predicate, C++ dyadic decoding, and integer Bernstein
subdivision are adapted from the MIT-licensed research archive
`av_certified_research_v2.zip` generated earlier in this research conversation.
The original `Copyright (c) 2026` notice is retained in LICENSE.
Packaging, public interfaces, documentation, tests and benchmark integration
were prepared with AI assistance for this release. They have not received an
independent external audit. No claim of peer review or novel mathematics is made.

Boost headers are required only when building C++; they are NOT vendored.
Boost.Multiprecision is distributed under the Boost Software License 1.0.
NumPy, SciPy and Matplotlib are optional benchmark dependencies, not bundled code.
No OpenAI math source, ADAC source, third-party media, credentials, or model
weights are redistributed. References are links, not software endorsements.
The project is not affiliated with OpenAI, ADAC, SciPy or Boost.

## OpenAI attribution boundary

Research began with `openai/math`. The referenced complete Crouzeix result, family
325 at commit `adc7f1241b42e322a6451854ab7e4b4c146bf78a`, is used only as an
explicit assumption in extension notes. It is not a dependency of the executable
biquad/cascade certifiers or of any measured speedup. The DFT paper informed scope,
not implementation. See [the four-language provenance guides](../README.md) and
[the source registry](../research/provenance/sources.json) for exact file locations, blob
hashes, attribution and verification limits. No upstream proof source is bundled.

## Project identity

Dexted DSP is the maintained name of the earlier CertifiedDSP research package.
Repository: https://github.com/dextune/dexted-dsp
Maintainer: DEXTUNE. Historical archive labels and measurements remain unchanged.
See [migration notes](../project/REBRANDING.md) for API and certificate-schema changes.
