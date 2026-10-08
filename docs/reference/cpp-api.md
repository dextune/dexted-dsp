# C++20 / C ABI

Build with CMake >= 3.20, Boost headers >= 1.74, and a C++20 compiler. The native API tests **binary32 biquad coefficients** with a binary64 threshold. It does not implement arbitrary cascade certification.

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel 2
ctest --test-dir build --output-on-failure
```

The header API is `dexted_dsp::certify_biquad_f32`; see `cpp/include/dexted_dsp/biquad.hpp`. The C ABI functions `dexted_dsp_biquad_f32` and `dexted_dsp_batch_f32` are defined in `cpp/include/dexted_dsp/c_api.h`. Their integer return values are **not booleans**: negative values signal errors. Do not use `-ffast-math` if finite-value checks are needed.

[Full API and CMake consumer instructions](API.md) · [Usage guide](../en/getting-started/USER_GUIDE.md)
