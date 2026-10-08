// SPDX-License-Identifier: MIT
#include "dexted_dsp/c_api.h"
#include "dexted_dsp/biquad.hpp"
#include "dexted_dsp/cascade.hpp"
extern "C" int dexted_dsp_biquad_f32(const float *row, double gamma) {
    try { return dexted_dsp::certify_biquad_f32(row, gamma); }
    catch (...) { return -2; }
}
extern "C" void dexted_dsp_batch_f32(const float *rows, size_t count, double gamma, int *out) {
    if (!out) return;
    if (!rows) { for (size_t i=0; i<count; ++i) out[i]=-1; return; }
    for (size_t i=0; i<count; ++i) out[i]=dexted_dsp_biquad_f32(rows+5*i, gamma);
}
extern "C" int dexted_dsp_cascade_f32(const float *rows, size_t count,
                                        double gamma, unsigned max_depth, size_t max_nodes) {
    try { return dexted_dsp::certify_cascade_f32(rows,count,gamma,max_depth,max_nodes); }
    catch (...) { return -2; }
}
