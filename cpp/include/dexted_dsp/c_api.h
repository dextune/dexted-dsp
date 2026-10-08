/* SPDX-License-Identifier: MIT */
#ifndef DEXTED_DSP_C_API_H
#define DEXTED_DSP_C_API_H
#include <stddef.h>
#if defined(_WIN32)
# if defined(DEXTED_DSP_BUILD)
#  define DEXTED_DSP_API __declspec(dllexport)
# else
#  define DEXTED_DSP_API __declspec(dllimport)
# endif
#else
# define DEXTED_DSP_API __attribute__((visibility("default")))
#endif
#ifdef __cplusplus
extern "C" {
#endif
/* Rows contain [b0,b1,b2,a1,a2], gamma is positive finite binary64.
   1=certified, 0=condition failed, -1=invalid, -2=internal/resource error.
   Batch callers own count*5 readable floats and count writable ints. */
DEXTED_DSP_API int dexted_dsp_biquad_f32(const float *coefficients, double gamma);
DEXTED_DSP_API void dexted_dsp_batch_f32(const float *rows, size_t count, double gamma, int *out);
/* Offline 1..32-section cascade, including exact integer Bernstein certificate
   predicate. This C ABI returns -3 for budget-limited UNKNOWN, never PASS.
   No serialized certificate is produced by the native predicate. */
DEXTED_DSP_API int dexted_dsp_cascade_f32(const float *rows, size_t count,
                                         double gamma, unsigned max_depth,
                                         size_t max_nodes);
#ifdef __cplusplus
}
#endif
#endif
