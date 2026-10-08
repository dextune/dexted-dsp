#include <dexted_dsp/biquad.hpp>
#include <dexted_dsp/c_api.h>
#include <array>
#include <cmath>
#include <iostream>
#include <limits>
int main() {
    int errors=0;
    auto check=[&](std::array<float,5> x, double g, int expected) {
        int h=dexted_dsp::certify_biquad_f32(x.data(),g);
        int c=dexted_dsp_biquad_f32(x.data(),g);
        if(h!=expected || c!=expected) { ++errors; std::cerr<<"predicate mismatch\n"; }
    };
    check({.5f,0,0,0,0},1,1);
    check({1,0,0,0,0},1,0);
    check({1,0,0,0,0},2,1);
    check({0,0,0,0,1},1,0);
    check({0,0,0,-2,1},1,0);
    float alpha=1.0f/16384;
    check({alpha,0,-alpha,0,1-alpha},1,0);
    check({alpha*7/16,0,-alpha*7/16,0,1-alpha},1,1);
    check({std::numeric_limits<float>::denorm_min(),0,0,0,0},1,1);
    check({std::numeric_limits<float>::max(),0,0,0,0},1,0);
    check({std::numeric_limits<float>::infinity(),0,0,0,0},1,-1);
    check({.5f,0,0,0,0},0,-1);
    check({.5f,0,0,0,0},1e-300,0);
    check({.5f,0,0,0,0},1e300,1);
    int out[2]={99,99};dexted_dsp_batch_f32(nullptr,2,1,out);
    if(out[0]!=-1 || out[1]!=-1) ++errors;
    if(dexted_dsp_biquad_f32(nullptr,1)!=-1) ++errors;
    std::cout << "native tests: " << (errors?"FAIL":"PASS") << "\n";
    return errors?1:0;
}
