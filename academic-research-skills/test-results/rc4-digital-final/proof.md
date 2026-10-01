For a > 0, minimize f(x)=a(x-t)^2 over 0 <= x <= 1.
The unique minimizer is p=min(1,max(0,t)). For every feasible x,
f(x)-f(p)=a(x-p)^2+2a(p-t)(x-p). If 0<=t<=1, p=t and the second
term vanishes. If t<0, p=0 and both factors p-t and x-p are nonnegative.
If t>1, p=1 and both factors are nonpositive. Thus the difference is
nonnegative, and a>0 makes it strictly positive when x!=p.
At a=0 every feasible point minimizes, so uniqueness fails. For a<0
the proposed projection can fail (t=1/2: endpoints beat p=1/2).
This is an elementary established result used to verify the tool chain,
not a new mathematical theorem. The algebra and sign argument constitute
the proof; the following finite computations only check implementation.
