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
/* Rows contain [b0,b1,b2,a1,a2]. gamma is a positive finite binary64.
   Results: 1=certified; 0=not certified; -1=invalid; -2=internal/resource error.
   The caller owns all buffers and supplies count*5 readable coefficient floats
   and count writable results. Native batch output is a predicate, not a proof. */
DEXTED_DSP_API int dexted_dsp_biquad_f32(const float *coefficients, double gamma);
DEXTED_DSP_API void dexted_dsp_batch_f32(const float *rows, size_t count, double gamma, int *out);
#ifdef __cplusplus
}
#endif
#endif
