// SPDX-License-Identifier: MIT
// Offline predicate for IDEAL fixed LTI behavior with exact binary32
// coefficients. 1=certified, 0=condition not certified, -1=invalid input.
// This header may throw std::bad_alloc; the exported C API contains exceptions.
#pragma once
#include <boost/multiprecision/cpp_int.hpp>
#include <bit>
#include <cmath>
#include <complex>
#include <cstdint>
#include <cstring>
#include <limits>
#include <vector>
#include <algorithm>
namespace dexted_dsp {
using boost::multiprecision::cpp_int;
static_assert(sizeof(float)==4 && sizeof(double)==8);
static_assert(std::numeric_limits<float>::is_iec559 && std::numeric_limits<double>::is_iec559);
struct Dyadic { std::int64_t mant; int exp; };

inline Dyadic decode_float(float x) {
    std::uint32_t u;std::memcpy(&u,&x,4);
    unsigned e=(u>>23)&255u,m=u&0x7fffffu;
    if(e)m|=0x800000u;
    if(!m)return {0,0};
    int p=e?static_cast<int>(e)-150:-149;
    unsigned trailing=std::countr_zero(m);m>>=trailing;p+=static_cast<int>(trailing);
    return {(u>>31)?-static_cast<std::int64_t>(m):static_cast<std::int64_t>(m),p};
}
inline void positive_double_ratio(double x,cpp_int &n,cpp_int &d) {
    std::uint64_t u;std::memcpy(&u,&x,8);
    unsigned e=static_cast<unsigned>((u>>52)&2047u);
    std::uint64_t m=u&0xfffffffffffffu;
    if(e)m|=0x10000000000000u;
    int p=e?static_cast<int>(e)-1075:-1074;
    unsigned trailing=std::countr_zero(m);m>>=trailing;p+=static_cast<int>(trailing);
    n=m;d=1;
    if(p>=0)n<<=p;else d<<=-p;
}
inline void square_coeff(const cpp_int &x,const cpp_int &y,const cpp_int &z,cpp_int out[3]) {
    cpp_int delta=x-z;
    out[0]=delta*delta+y*y;out[1]=2*y*(x+z);out[2]=4*x*z;
}
inline int certify_biquad_f32(const float *v,double gamma) {
    if(!v || !std::isfinite(gamma) || gamma<=0)return -1;
    // Exact, not heuristic: |a2|<1 is a necessary Jury condition.
    // Comparing one binary32 coefficient with the exactly represented 1
    // requires no arithmetic approximation and avoids expensive decoding.
    for(int j=0;j<5;++j)if(!std::isfinite(v[j]))return -1;
    if(std::abs(v[4])>=1.0f)return 0;
    Dyadic dy[5];int p=0;
    for(int j=0;j<5;++j){
        dy[j]=decode_float(v[j]);p=std::max(p,-dy[j].exp);
    }
    cpp_int s=cpp_int(1)<<p,w[5];
    for(int j=0;j<5;++j)w[j]=cpp_int(dy[j].mant)<<(dy[j].exp+p);
    if(boost::multiprecision::abs(w[4])>=s || s+w[3]+w[4]<=0 || s-w[3]+w[4]<=0)return 0;
    cpp_int n[3],d[3];square_coeff(w[0],w[1],w[2],n);square_coeff(s,w[3],w[4],d);
    cpp_int gn,gd;positive_double_ratio(gamma,gn,gd);gn*=gn;gd*=gd;
    cpp_int c=gn*d[0]-gd*n[0],b=gn*d[1]-gd*n[1],a=gn*d[2]-gd*n[2];
    if(a-b+c<=0 || a+b+c<=0)return 0;
    if(a>0) {
        cpp_int twice_a=a;twice_a<<=1;
        if(b>-twice_a && b<twice_a) {
            cpp_int gap=a*c;gap<<=2;gap-=b*b;
            if(gap<=0)return 0;
        }
    }
    return 1;
}

} // namespace dexted_dsp
