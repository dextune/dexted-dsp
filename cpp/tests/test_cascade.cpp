#include <dexted_dsp/cascade.hpp>
#include <dexted_dsp/c_api.h>
#include <array>
#include <iostream>
#include <limits>
int main(){
  int errors=0;
  auto check=[&](const float* rows,std::size_t count,double gamma,int expected,unsigned depth=48) {
    const int result=dexted_dsp::certify_cascade_f32(rows,count,gamma,depth);
    if(result!=expected){++errors;std::cerr<<"cascade mismatch got "<<result<<" expected "<<expected<<"\n";}
  };
  const std::array<float,10> pair{1,-.75f,0,-.125f,0,.75f,-.09375f,0,-.75f,0};
  check(pair.data(),2,1,1);
  if(dexted_dsp_cascade_f32(pair.data(),2,1,48,20000)!=1)++errors;
  check(pair.data(),2,.7,0);
  const std::array<float,5> constant{.5f,0,0,0,0};
  check(constant.data(),1,1,1);
  check(constant.data(),1,.5,0);
  const std::array<float,5> bad{1,0,0,0,1};
  check(bad.data(),1,1,0);
  const std::array<float,5> high_q{2.6702880859375e-05f,0,-2.6702880859375e-05f,0,0.99993896484375f};
  check(high_q.data(),1,1,-3,0);
  if(dexted_dsp_cascade_f32(high_q.data(),1,1,0,20000)!=-3)++errors;
  check(high_q.data(),1,1,1,16);
  check(nullptr,1,1,-1);
  const std::array<float,5> invalid{std::numeric_limits<float>::infinity(),0,0,0,0};
  check(invalid.data(),1,1,-1);
  check(constant.data(),0,1,-1);
  std::cout<<"native cascade tests: "<<(errors?"FAIL":"PASS")<<"\n";
  return errors?1:0;
}
