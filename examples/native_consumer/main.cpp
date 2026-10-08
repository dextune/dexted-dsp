// SPDX-License-Identifier: MIT
// Standalone CMake consumer using only the installed DextedDSP export.
#include <dexted_dsp/c_api.h>

int main() {
    const float stable[5] = {0.25f, 0.0f, 0.0f, -0.5f, 0.0f};
    const float rejected[5] = {1.0f, 0.0f, 0.0f, 0.0f, 0.0f};
    if (dexted_dsp_biquad_f32(stable, 1.0) != 1) return 1;
    if (dexted_dsp_biquad_f32(rejected, 1.0) != 0) return 2;
    const float compensated[10] = {
        1.0f, -0.75f, 0.0f, -0.125f, 0.0f,
        0.75f, -0.09375f, 0.0f, -0.75f, 0.0f
    };
    if (dexted_dsp_cascade_f32(compensated, 2, 1.0, 48, 20000) != 1) return 3;
    if (dexted_dsp_cascade_f32(compensated, 0, 1.0, 48, 20000) != -1) return 4;
    int output[2] = {99,99};
    const float rows[10] = {
        0.25f, 0.0f, 0.0f, -0.5f, 0.0f,
        1.0f, 0.0f, 0.0f, 0.0f, 0.0f
    };
    dexted_dsp_batch_f32(rows, 2, 1.0, output);
    return (output[0]==1 && output[1]==0) ? 0 : 5;
}
