# 形式推导

令 $\bar{x}=n^{-1}\sum_{i=1}^n x_i$。对任意实数 $a$，

$$
\begin{aligned}
S(a)&=\sum_{i=1}^n[(x_i-\bar{x})+(\bar{x}-a)]^2\\
&=\sum_{i=1}^n(x_i-\bar{x})^2
 +2(\bar{x}-a)\sum_{i=1}^n(x_i-\bar{x})
 +n(\bar{x}-a)^2\\
&=S(\bar{x})+n(\bar{x}-a)^2.
\end{aligned}
$$

中间项为零，因为 $\sum_i(x_i-\bar{x})=0$。由于 $n\ge1$，最后一项非负，且只在 $a=\bar{x}$ 时为零。因此均值是唯一最小化点，包括 $n=1$。此证明不需要样本分布或随机抽样假设。
