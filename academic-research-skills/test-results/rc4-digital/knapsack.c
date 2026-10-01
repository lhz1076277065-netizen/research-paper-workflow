
#include <stdio.h>
int main(int argc, char **argv) {
  if(argc!=3) return 2;
  FILE *in=fopen(argv[1],"r"), *out=fopen(argv[2],"w");
  if(!in || !out) return 3;
  int n,capacity,w[20],v[20];
  if(fscanf(in,"%d%d",&n,&capacity)!=2 || n<1 || n>20 || capacity<0) return 4;
  for(int i=0;i<n;i++) if(fscanf(in,"%d%d",&w[i],&v[i])!=2 || w[i]<=0 || v[i]<0) return 5;
  int best=0;unsigned mask_best=0;
  /* ponytail: exponential search limited to 20 items; use branch-and-bound for larger instances. */
  for(unsigned mask=0;mask<(1u<<n);mask++) {
    int weight=0,value=0;
    for(int i=0;i<n;i++) if(mask&(1u<<i)) {weight+=w[i];value+=v[i];}
    if(weight<=capacity && value>best) {best=value;mask_best=mask;}
  }
  fprintf(out,"%d %u\n",best,mask_best); fclose(in);fclose(out);return 0;
}
