# Alcohol and color intensity in the complete UCI Wine dataset: pooled and cultivar-conditioned associations

*Revised scientific draft.*

## Abstract

We described the association between alcohol content and color intensity in all 178 records of the original UCI Wine dataset, overall and conditional on its three cultivar classes. Pearson and Spearman correlations and ordinary least-squares regressions summarized direction and magnitude. The pooled Pearson correlation was 0.546 and Spearman correlation was 0.635; the pooled slope was 1.560 recorded color-intensity units per recorded alcohol unit (nominal 95% HC3 normal-approximation interval, 1.246–1.875). Class-specific slopes were 1.094, 0.464 and 1.527. With class-specific intercepts, the common slope was 0.940 (0.492–1.389), and the class-adjusted partial correlation was 0.319. All single-record omissions retained positive pooled and adjusted slopes. Thus, positive direction was shared across classes, while class conditioning reduced the pooled magnitude. The differing class estimates and an interaction reference p-value of 0.106 do not establish equal slopes. These findings describe this historical dataset; intervals and reference tests are model-based sensitivity summaries and support neither population nor causal claims. [claim:C001] [evidence:E001,E003,E004,E005,E006]

## Introduction

The UCI Wine dataset contains chemical measurements from wines grown in one Italian region and derived from three cultivars [1]. Although the dataset has been used for classification, the present question concerns the relationship between two recorded measurements: alcohol content and color intensity. A pooled association combines variation within cultivar classes with differences among classes, so it need not describe the association within each class. [claim:C002] [evidence:E001,E002,E005,E007]

We estimated the direction and magnitude of the alcohol–color-intensity association in the complete original dataset, then examined its direction and magnitude within cultivar class and after class adjustment. The aim was a coherent description of these historical records, with no claim about wine quality, a causal alcohol effect or a wider wine population. [claim:C003] [evidence:E001,E002,E005,E007]

## Methods

We used all 178 records in the original headerless `wine.data` table, interpreted using `wine.names` [1]. The first raw column identifies cultivar class; alcohol is the first chemical feature (raw column 2), and color intensity the tenth (raw column 11). Classes 1, 2 and 3 contain 59, 71 and 48 records. The source reports no missing attributes. No records were excluded or imputed, and neither variable was transformed. The dictionary does not provide measurement units or cultivar names, so coefficients are expressed in recorded units and classes retain their numeric labels. [claim:C004] [evidence:E002,E003,E004,E005,E006]

Let X denote recorded alcohol and Y recorded color intensity. The pooled analysis summarized Pearson r, Spearman ρ using average-tied ranks, and the least-squares model Y = α + βX + e. The same correlations and regression were fitted separately within each class. The class-adjusted model was Y = α + βX + γ₂I(class = 2) + γ₃I(class = 3) + e, with class 1 as reference. Its common slope summarizes within-class association, weighting class-specific slopes by their within-class alcohol sums of squares. We also correlated X and Y after separately subtracting their class means to obtain the class-adjusted partial correlation. A model adding X-by-class indicators allowed different slopes; a joint HC3 Wald statistic for the two interaction coefficients was compared with a χ² reference distribution with two degrees of freedom as a heterogeneity diagnostic. [claim:C005] [evidence:E002,E003,E004,E005,E006]

Regressions used NumPy 2.3.5 least-squares solutions, with pandas 2.2.3 for data handling and tied ranks. Slope intervals used heteroscedasticity-consistent HC3 covariance and the standard normal 0.975 quantile; conventional variance estimates with the same normal reference were also calculated. Pearson intervals used Fisher's z transformation. Because the target is a complete fixed dataset without a documented probability sampling design, these nominal 95% intervals and reference p-values describe sensitivity under hypothetical statistical assumptions rather than population coverage. No sampling-based significance threshold was used to define the substantive conclusion. [claim:C006] [evidence:E002,E003,E004,E005,E006]

Sensitivity analyses refitted pooled and adjusted models after each of the 178 single-record omissions, examined residuals and influence, and added a common quadratic term in class-centered alcohol to the adjusted model. Separate calculations from the raw table checked the pooled slope, the adjusted slope using class demeaning and QR decomposition, and the adjusted HC3 standard error. These are checks of the same dataset, not independent replications. [claim:C007] [evidence:E002,E003,E004,E005,E006]

## Results

The pooled association was positive: Pearson r = 0.546 (Fisher nominal 95% interval, 0.434–0.642), Spearman ρ = 0.635, and slope = 1.560 (HC3 interval, 1.246–1.875). The pooled regression R² was 0.299. [claim:C008] [evidence:E003,E004,E006]

Positive associations were also present within every class, although their magnitudes differed (Table 1). Class-specific slopes ranged from 0.464 in class 2 to 1.527 in class 3. Alcohol means were 13.745, 12.279 and 13.154 in classes 1–3, while color-intensity means were 5.528, 3.087 and 7.396, respectively. [claim:C009] [evidence:E003,E004,E006]

**Table 1. Alcohol–color-intensity associations in the original Wine records.** Slopes are recorded color-intensity units per recorded alcohol unit; brackets contain nominal 95% HC3 normal-approximation intervals. Each row uses all records in its stated analysis set. [claim:C010] [evidence:E003,E004,E006]

| Analysis set | n | Pearson r | Spearman ρ | Slope [HC3 interval] |
|---|---:|---:|---:|---:|
| All records | 178 | 0.546 | 0.635 | 1.560 [1.246, 1.875] | [claim:C011] [evidence:E003,E004,E006]
| Class 1 | 59 | 0.408 | 0.443 | 1.094 [0.423, 1.765] | [claim:C012] [evidence:E003,E004,E006]
| Class 2 | 71 | 0.270 | 0.257 | 0.464 [0.078, 0.850] | [claim:C013] [evidence:E003,E004,E006]
| Class 3 | 48 | 0.350 | 0.284 | 1.527 [0.295, 2.759] | [claim:C014] [evidence:E003,E004,E006]

After class adjustment, the common slope remained positive at 0.940 (HC3 interval, 0.492–1.389), and the class-adjusted partial correlation was 0.319. The adjusted model R² was 0.622 for alcohol and class indicators together. Conventional normal-reference slope intervals were 1.207–1.914 pooled and 0.525–1.356 adjusted. The interaction diagnostic was χ²(2) = 4.483, with reference p = 0.106; it does not establish that the class slopes are equal. [claim:C015] [evidence:E003,E004,E006]

Across all single-record omissions, pooled slopes ranged from 1.492 to 1.604 and adjusted slopes from 0.818 to 0.998; all remained positive. Maximum Cook's distances were 0.099 and 0.140, respectively. Correlations between absolute residuals and fitted values were 0.188 and 0.481, indicating residual variation that warrants attention to the variance assumptions. The added class-centered quadratic coefficient was 0.014 (HC3 interval, −0.652–0.680), leaving substantial uncertainty about curvature. Separate raw-file calculations reproduced the main slopes to a maximum absolute difference of 1.33 × 10⁻¹⁵ and the adjusted HC3 standard error to 3.36 × 10⁻¹⁴. [claim:C016] [evidence:E003,E004,E006]

## Discussion

Alcohol content and color intensity were positively associated in this dataset, both overall and within each of its three cultivar classes. The association persisted after class adjustment, with a smaller common slope and partial correlation than their pooled counterparts. Cultivar conditioning therefore changes the magnitude of the descriptive relationship without reversing its direction. The pooled slope alone would give an incomplete account of the within-class association. [claim:C017] [evidence:E001,E002,E003,E004,E005,E006]

Consistency of direction should be distinguished from equality of magnitude. The three fitted slopes differ numerically, and the adjusted common slope is a weighted summary rather than a demonstration of identical class responses. The interaction diagnostic supplies neither an equivalence test nor a population-level conclusion. Rank correlations and the omission analyses support the positive descriptive direction, while the wide quadratic interval does not establish linearity. [claim:C018] [evidence:E001,E002,E003,E004,E005,E006]

The original records lack a documented probability sampling frame, collection dates, batch structure, replication details and measurement units. HC3 addresses heterogeneous error variance under independent errors; it cannot remedy unknown clustering, measurement error or an inappropriate mean model. Accordingly, these coefficients summarize the recorded wines and do not identify a causal mechanism, establish practical wine-quality implications or justify extrapolation to other wines. Within that scope, the complete-data analyses answer the original question: the alcohol–color-intensity association is positive overall and conditional on cultivar class, with attenuation after class adjustment and unresolved equality of class-specific magnitudes. [claim:C019] [evidence:E001,E002,E003,E004,E005,E006]

## Reference

1. Aeberhard, S., & Forina, M. (1992). *Wine* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5PC7J. [claim:C020] [evidence:E007]
