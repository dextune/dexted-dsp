// Benchmark-only baselines. No ADAC/SciPy source is copied.
#include <dexted_dsp/biquad.hpp>
extern "C" void exact_batch(const float *rows, std::size_t count, double gamma, int *out) {
    for(std::size_t i=0;i<count;++i) {
        try {out[i]=dexted_dsp::certify_biquad_f32(rows+5*i,gamma);}
        catch(...) {out[i]=-2;}
    }
}
extern "C" void grid_batch(const float *v,std::size_t count,double gamma,std::size_t M,int *out){
    if(M<2 || !std::isfinite(gamma) || gamma<=0){std::fill(out,out+count,-1);return;}
    // Stronger baseline: cache the frequency grid. Accuracy calls warm it
    // BEFORE timed runs, so trig/grid preparation does not inflate timings.
    static thread_local std::vector<std::complex<double>> z,z2;
    if(z.size()!=M){
        z.resize(M);z2.resize(M);
        const double pi=std::acos(-1.0);
        for(std::size_t j=0;j<M;++j){z[j]=std::polar(1.0,-pi*double(j)/double(M-1));z2[j]=z[j]*z[j];}
    }
    const double g2=gamma*gamma;
    for(std::size_t i=0;i<count;++i){
        const float *r=v+5*i;
        bool finite=true;for(int k=0;k<5;++k)finite=finite&&std::isfinite(r[k]);
        if(!finite){out[i]=-1;continue;}
        const double b0=r[0],b1=r[1],b2=r[2],a1=r[3],a2=r[4];
        if(!(std::abs(a2)<1 && 1+a1+a2>0 && 1-a1+a2>0)){out[i]=0;continue;}
        bool pass=true;
        for(std::size_t j=0;j<M;++j){
            const auto n=b0+b1*z[j]+b2*z2[j],d=1.+a1*z[j]+a2*z2[j];
            // Early exit helps the baseline on rejections. No sqrt/division.
            if(!(std::norm(n)<g2*std::norm(d))){pass=false;break;}
        }
        out[i]=pass?1:0;
    }
}


// Stronger non-grid baseline: SAME algebraic threshold test in binary64.
// It is very fast, but cancellation can change a strict sign near zero.
// It is not an interval-arithmetic or exact certificate.
extern "C" void float64_batch(const float *rows, std::size_t count, double gamma, int *out) {
    for(std::size_t i=0;i<count;++i) {
        const float *v=rows+5*i;
        bool valid=std::isfinite(gamma)&&gamma>0;
        for(int j=0;j<5;++j) valid=valid&&std::isfinite(v[j]);
        if(!valid) {out[i]=-1;continue;}
        double b0=v[0],b1=v[1],b2=v[2],a1=v[3],a2=v[4];
        if(!(std::abs(a2)<1 && 1+a1+a2>0 && 1-a1+a2>0)){out[i]=0;continue;}
        auto sq=[](double x,double y,double z, double *p) {
            p[0]=(x-z)*(x-z)+y*y;p[1]=2*y*(x+z);p[2]=4*x*z;
        };
        double n[3],d[3];sq(b0,b1,b2,n);sq(1,a1,a2,d);
        double c=gamma*gamma*d[0]-n[0],b=gamma*gamma*d[1]-n[1],a=gamma*gamma*d[2]-n[2];
        bool ok=a-b+c>0 && a+b+c>0;
        if(a>0 && -2*a<b && b<2*a) ok=ok&&(4*a*c-b*b>0);
        out[i]=ok?1:0;
    }
}
