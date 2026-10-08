// SPDX-License-Identifier: MIT
// Exact binary32 serial-SOS predicate. Offline only: no runtime-roundoff proof.
#pragma once
#include "dexted_dsp/biquad.hpp"
#include <array>
#include <cstddef>
#include <utility>
#include <vector>

namespace dexted_dsp {
namespace detail {
inline std::vector<cpp_int> multiply(const std::vector<cpp_int>& a,
                                     const std::vector<cpp_int>& b) {
    std::vector<cpp_int> out(a.size()+b.size()-1);
    for (std::size_t i=0;i<a.size();++i)
        for (std::size_t j=0;j<b.size();++j) out[i+j]+=a[i]*b[j];
    return out;
}
inline cpp_int gcd(cpp_int a,cpp_int b) {
    while(b!=0){cpp_int r=a%b;a=std::move(b);b=std::move(r);}
    return a;
}
inline std::vector<std::vector<cpp_int>> binomials(std::size_t n) {
    std::vector<std::vector<cpp_int>> choose(n+1);
    for(std::size_t i=0;i<=n;++i){
        choose[i].resize(i+1);choose[i][0]=choose[i][i]=1;
        for(std::size_t j=1;j<i;++j)choose[i][j]=choose[i-1][j-1]+choose[i-1][j];
    }
    return choose;
}
inline std::vector<cpp_int> bernstein_scaled(const std::vector<cpp_int>& p) {
    const std::size_t n=p.size()-1;
    const auto choose=binomials(n);
    cpp_int lcm=1;
    for(std::size_t k=0;k<=n;++k) lcm=(lcm/gcd(lcm,choose[n][k]))*choose[n][k];
    std::vector<cpp_int> power(n+1),bern(n+1);power[0]=1;
    for(std::size_t k=0;k<=n;++k){
        cpp_int acc=0;
        for(std::size_t j=k;j<=n;++j){
            cpp_int term=p[j]*choose[j][k];
            if((j-k)%2)acc-=term;else acc+=term;
        }
        power[k]=acc<<k;
    }
    for(std::size_t i=0;i<=n;++i)
        for(std::size_t k=0;k<=i;++k)
            bern[i]+=power[k]*choose[i][k]*(lcm/choose[n][k]);
    return bern;
}
inline std::pair<std::vector<cpp_int>,std::vector<cpp_int>> split_scaled(
        const std::vector<cpp_int>& coeffs) {
    const std::size_t n=coeffs.size()-1;
    std::vector<cpp_int> v=coeffs,left,right;
    left.reserve(n+1);right.reserve(n+1);
    left.push_back(coeffs.front()<<n);right.push_back(coeffs.back()<<n);
    for(std::size_t r=1;r<=n;++r){
        for(std::size_t i=0;i<=n-r;++i)v[i]+=v[i+1];
        left.push_back(v[0]<<(n-r));right.push_back(v[n-r]<<(n-r));
    }
    std::reverse(right.begin(),right.end());
    return {std::move(left),std::move(right)};
}
inline int positive_over_interval(const std::vector<cpp_int>& p,
                                unsigned max_depth,std::size_t max_nodes) {
    struct Node{std::vector<cpp_int> coeffs;unsigned depth;};
    std::vector<Node> stack;
    stack.push_back({bernstein_scaled(p),0});
    std::size_t nodes=0;
    while(!stack.empty()){
        if(nodes>=max_nodes)return -3;
        Node node=std::move(stack.back());stack.pop_back();++nodes;
        const auto& b=node.coeffs;
        if(b.front()<=0 || b.back()<=0)return 0;
        bool positive=true;
        for(const auto& x:b)if(x<=0){positive=false;break;}
        if(positive)continue;
        if(node.depth>=max_depth || nodes>=max_nodes)return -3;
        auto [left,right]=split_scaled(b);
        stack.push_back({std::move(right),node.depth+1});
        stack.push_back({std::move(left),node.depth+1});
    }
    return 1;
}
} // namespace detail

// 1=certified, 0=condition failed, -1=invalid, -3=resource-limited unknown.
// Memory/allocation errors may throw: use C ABI for caught -2 errors.
inline int certify_cascade_f32(const float* rows,std::size_t count,double gamma,
                               unsigned max_depth=48,std::size_t max_nodes=20000) {
    if(!rows || count<1 || count>32 || !std::isfinite(gamma) || gamma<=0 ||
       max_depth>128 || max_nodes<1 || max_nodes>100000)return -1;
    std::vector<cpp_int> num{1},den{1};
    for(std::size_t i=0;i<count;++i){
        const float* v=rows+5*i;
        for(int j=0;j<5;++j)if(!std::isfinite(v[j]))return -1;
        if(std::abs(v[4])>=1.0f)return 0;
        Dyadic d[5];int p=0;
        for(int j=0;j<5;++j){d[j]=decode_float(v[j]);p=std::max(p,-d[j].exp);}
        cpp_int scale=cpp_int(1)<<p;
        std::array<cpp_int,5> w;
        for(int j=0;j<5;++j)w[j]=cpp_int(d[j].mant)<<(d[j].exp+p);
        if(boost::multiprecision::abs(w[4])>=scale ||
           scale+w[3]+w[4]<=0 || scale-w[3]+w[4]<=0)return 0;
        cpp_int n[3],q[3];square_coeff(w[0],w[1],w[2],n);
        square_coeff(scale,w[3],w[4],q);
        num=detail::multiply(num,{n[0],n[1],n[2]});
        den=detail::multiply(den,{q[0],q[1],q[2]});
    }
    cpp_int gn,gd;positive_double_ratio(gamma,gn,gd);
    gn*=gn;gd*=gd;
    std::vector<cpp_int> gap(num.size());
    for(std::size_t i=0;i<gap.size();++i)gap[i]=gn*den[i]-gd*num[i];
    while(gap.size()>1 && gap.back()==0)gap.pop_back();
    return detail::positive_over_interval(gap,max_depth,max_nodes);
}
} // namespace dexted_dsp
