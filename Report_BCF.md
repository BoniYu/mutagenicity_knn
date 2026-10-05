# Report: BCF Regression

## Overview

Extending the mutagenicity QSPR project to a second endpoint: predicting
bioconcentration factor (BCF), a measure of how much a chemical
accumulates in an organism relative to its environment. Unlike
mutagenicity (binary classification), BCF is a continuous-valued
regression target.

## Dataset

- 800 molecules, `BCF_training.csv` (from the same MLCE_book repository
  as the mutagenicity dataset).
- No missing values, no duplicate rows.
- **Target:** `Experimental value [log(L/kg)]`, log-transformed BCF
  (standard practice for this endpoint, since raw BCF spans several
  orders of magnitude).
- **Features (14):** `NumAromaticRings`, `NumHAcceptors`,
  `NumHeteroatoms`, `NumRotatableBonds`, `NumValenceElectrons`, `qed`,
  `TPSA`, `MolMR`, `BalabanJ`, `BertzCT`, `fr_COO`, `fr_COO2`,
  `fr_halogen`, `MolWt`, `MolLogP`. Eight of these overlap with the
  mutagenicity descriptor set; `NumAromaticRings`, `NumHAcceptors`,
  `NumHeteroatoms`, `NumRotatableBonds`, `fr_COO`, `fr_COO2`, and
  `fr_halogen` are new, including RDKit fragment counts for specific
  functional groups rather than only bulk/aggregate properties.

## Target distribution

| Statistic | Value |
|---|---|
| Count | 800 |
| Mean | 1.793 |
| Std | 1.332 |
| Min | -1.700 |
| 25% | 0.661 |
| Median | 1.755 |
| 75% | 2.812 |
| Max | 5.694 |

The distribution is not a single smooth peak, it shows a bimodal-ish
shape: a tall peak around 0.3-0.5, a dip near 1.5-2, and a second,
smaller bump around 2-2.5, before tapering off toward 5.

## Explaining the distribution shape

Two descriptors show clear, chemically interpretable, opposite-direction
relationships with BCF, explaining the bimodal pattern:

**Halogens (`fr_halogen`)**, associated with substantially higher BCF:

| `fr_halogen` present | Mean log(L/kg) |
|---|---|
| No | 0.912 |
| Yes | 1.948 |

Molecules containing at least one halogen fragment average over a full
log unit higher (roughly 10x higher BCF), consistent with the known
bioaccumulative tendency of halogenated organics (e.g. PCBs,
organochlorine pesticides).

**Carboxylic acid groups (`fr_COO` / `fr_COO2`)**, associated with
substantially lower BCF:

| Group | Low BCF (≤2) | High BCF (>2) |
|---|---|---|
| `fr_COO` / `fr_COO2` mean count | 0.124 | 0.003 |

Molecules with carboxylic acid groups are almost exclusively found in
the lower-BCF range, consistent with the reduced bioaccumulation
potential of ionizable, water-soluble functional groups, which tend to
be excreted rather than stored in fatty tissue.

Together, these two relationships account for much of the bimodal shape:
the upper cluster is disproportionately halogenated, non-acid molecules;
the lower cluster is enriched in carboxylic-acid-containing molecules.

## Data quality notes

- One row (SMILES `O=C(O)c1nc(c(c(N)c1Cl)Cl)Cl`, target -1.700) has a
  corrupted `CAS` value (`01/02/1918`, apparently a misparsed date from
  the source file). Since `CAS` is not used as a model feature, this does
  not affect modeling and the row was retained.
- No other data quality issues found; the dataset required no cleaning
  beyond what was already done upstream.

## Outlier check

**Target:** a boxplot of `Experimental value [log(L/kg)]` showed no
outliers, the full range (-1.70 to 5.69) falls within 1.5×IQR of the
quartiles.

**Features:** a boxplot across all 15 descriptors showed clear outliers
in `BertzCT` (up to 3,402) and `MolWt` (up to 1,053), all other
descriptors showed no notable outliers. The highest-BertzCT/MolWt rows
were inspected individually:

| SMILES (truncated) | BertzCT | MolWt | log(L/kg) |
|---|---|---|---|
| `O=S(=O)(O)c7cccc6c7(cc(N=Nc1...` | 3401.6 | 979.0 | 0.498 |
| `O=S(=O)(O)c6cc5ccc(O)c(N=Nc1...` | 2841.8 | 786.9 | 1.851 |
| `O=S(=O)(O)OCCS(=O)(=O)c4ccc(...` | 2739.0 | 903.9 | 0.541 |
| `O=S(=O)(O)c5cc(ccc5(C=Cc1cc...` | 2603.6 | 881.0 | 0.960 |
| `O([Sn](CC(c1ccccc1)(C)C)(CC...` | 1869.1 | 1052.7 | 2.863 |

These are legitimate molecules, not data errors: large sulfonated azo
dyes (repeated sulfonic acid groups, azo linkages, multiple aromatic
rings) and one organotin compound. Despite their size and structural
complexity, most have low-to-moderate BCF values. This suggests
complexity/size alone does not drive bioaccumulation; their high
polarity (multiple ionizable sulfonic acid groups) likely explains the
low BCF despite large size, consistent with the carboxylic-acid-group
finding above.

**No rows were removed.** All identified outliers are genuine, informative
data points, and the dataset is small enough (800 rows) that removing
them would both shrink the training set and discard useful signal about
how polarity, not size, governs bioaccumulation.  

## Baseline model: Linear Regression

Evaluated via 10-fold cross-validation (`KFold`, shuffle=True,
random_state=42), using all 15 descriptors, standardised with
`StandardScaler`.

| Metric | Validation | Train |
|---|---|---|
| RMSE | 0.937 ± 0.085 | — |
| MAE | 0.745 ± 0.044 | — |
| R² | 0.490 ± 0.133 | 0.544 |

**Context:** the target's standard deviation is 1.332, so an RMSE of
0.937 (about 30% lower) confirms the model is learning real signal, not
just predicting the mean. MAE of 0.745 in log space corresponds to
predictions typically within roughly 5.6x of the true BCF value.

**Overfitting check:** train R² (0.544) and validation R² (0.490) are
close, a small, healthy gap, consistent with Linear Regression's limited
flexibility (a constrained linear model can't easily memorize training
noise). This establishes a reference point for later models: any model
showing a much wider train/validation gap should be treated as overfit,
a real risk given the dataset's small size (800 rows, 15 features).

**R² variance across folds (±0.133) is notably wider than seen in
mutagenicity's classification CV** (e.g. Random Forest's ±0.010 there),
expected given BCF's much smaller fold sizes (~80 molecules vs. ~575).

## Next steps

- kNN Regressor, Random Forest Regressor, XGBoost Regressor, same
  10-fold CV comparison, with train/validation R² reported for each to
  check for overfitting.
- Random Forest's built-in OOB score as an additional sanity check.

## kNN Regressor (default, k=5)

| Metric | Linear Regression | kNN (k=5) |
|---|---|---|
| RMSE | 0.937 ± 0.085 | **0.764 ± 0.084** |
| MAE | 0.745 ± 0.044 | **0.572 ± 0.060** |
| Validation R² | 0.490 ± 0.133 | **0.662 ± 0.074** |
| Train R² | 0.544 | 0.786 |

kNN clearly outperforms Linear Regression on every metric, consistent
with the EDA finding that BCF's relationship to the descriptors is
non-linear and feature-interaction-driven (halogens and acid groups
pulling in opposite directions), structure a single linear model can't
capture well.

**Overfitting check:** the train/validation R² gap (0.786 vs. 0.662,
~0.12) is noticeably wider than Linear Regression's (0.544 vs. 0.490,
~0.05). This is a mild overfitting signal, plausible given the small,
untuned k=5 on a dataset of only 800 rows. A k-sweep is planned next, to
find the validation-optimal k and check whether a larger k narrows this
gap, mirroring the tuning approach used for mutagenicity's kNN, but here
also explicitly checking the overfitting gap, not just validation score.

## Next steps

- k-sweep for kNN Regressor (range 1-30, smaller than mutagenicity's
  1-99 given the much smaller dataset), tracking both validation
  performance and the train/validation gap.
- Random Forest Regressor and XGBoost Regressor, same 10-fold CV
  comparison with train/validation R² reported.
- Random Forest's built-in OOB score as an additional sanity check.

## kNN Regressor: k-sweep (range 1-30, 10-fold CV)

Train and validation R² tracked across k to both find the best k and
check whether tuning narrows the overfitting gap seen at k=5.

**k=1** (maximum overfitting, reference point): train R² = 1.0 (perfect,
each point is its own nearest neighbor), validation R² = 0.50, a gap of
0.50, the clearest possible illustration of memorization.

As k increases, train R² declines steadily while validation R² rises
sharply then plateaus around 0.66-0.667 from roughly k=5 to k=15, a
broad, stable region rather than a sharp optimum.

**Best k = 7:**

| Metric | k=5 (default) | k=7 (tuned) |
|---|---|---|
| RMSE | 0.764 | **0.756** |
| MAE | 0.572 | **0.570** |
| Validation R² | 0.662 ± 0.074 | **0.669 ± 0.077** |
| Train R² | 0.786 | 0.761 |
| Train-validation gap | 0.124 | **0.092** |

Unlike mutagenicity's kNN tuning (where k barely affected results
under LOO), tuning k here gave both a small genuine performance
improvement and a meaningfully narrower overfitting gap, a cleaner case
for tuning actually mattering.

## Next steps

- Random Forest Regressor and XGBoost Regressor, same 10-fold CV
  comparison with train/validation R² reported, overfitting risk
  especially worth watching given the small dataset (800 rows, 15
  features).
  
## Random Forest and XGBoost (default)

Evaluated via the same 10-fold CV, with `return_train_score=True` to
check for overfitting. `StandardScaler` was tested and confirmed to have
no effect on either model's results (tree-based splits are
threshold-based, not distance-based) and was removed from both
pipelines.

| | Train R² | Validation R² | Gap |
|---|---|---|---|
| Random Forest | 0.960 | 0.721 | 0.239 |
| XGBoost | 0.999 | 0.693 | 0.306 |

Both models show substantial overfitting, far beyond what was seen with
Linear Regression (gap 0.054) or tuned kNN (gap 0.092). This is
consistent with the small dataset size: 800 rows and 15 features gives
these flexible ensemble methods far less data to constrain against than
mutagenicity's 5,758 rows did for the same model types and a smaller
8-feature set.

## Random Forest and XGBoost (tuned via RandomizedSearchCV)

Tuned via `RandomizedSearchCV` (25 iterations, 10-fold CV, scoring=R²),
searching primarily over complexity-limiting hyperparameters
(`max_depth`, `min_samples_leaf`/`min_child_weight`, regularization).

| | Train R² | Validation R² | Gap |
|---|---|---|---|
| Random Forest (tuned) | 0.935 | 0.732 | 0.203 |
| **XGBoost (tuned)** | **0.913** | **0.734** | **0.179** |

**XGBoost improved substantially** on both validation score and
overfitting gap (0.306 → 0.179), and is now the best-performing model
overall. **Random Forest improved only marginally** (gap 0.239 → 0.203);
the search selected `max_depth=None` (unconstrained) despite capped
options being available, suggesting bagging's inherent regularization is
not as responsive to these hyperparameters as boosting's is.

**Neither model fully eliminated overfitting.** This is treated as a
genuine limitation of the dataset size (800 rows, 15 features) rather
than a tuning failure: more training data would likely close this gap
further than additional hyperparameter search could. Worth noting for
context: even with the remaining gap, XGBoost's validation R² (0.734) is
the strongest result across all four models tried.

## Model comparison, summary

| Model | RMSE | MAE | Validation R² | Train-Val Gap |
|---|---|---|---|---|
| Linear Regression | 0.937 | 0.745 | 0.490 | 0.054 |
| kNN (k=7, tuned) | 0.756 | 0.570 | 0.669 | 0.092 |
| Random Forest (tuned) | 0.679 | 0.502 | 0.732 | 0.203 |
| **XGBoost (tuned)** | **0.679** | **0.505** | **0.734** | **0.179** |

**XGBoost (tuned) is the final model**, with the best validation R² and
the tightest overfitting gap among the two ensemble methods.

## Why more data would likely help

The remaining overfitting gap in both Random Forest (0.203) and XGBoost
(0.179), even after tuning, is best explained by dataset size rather than
insufficient hyperparameter search. A few reasons to expect more data
specifically, not more tuning, to close this gap further:

- **Row-to-feature ratio.** 800 rows for 15 features gives each tree
  relatively few examples to learn robust splits from; mutagenicity's
  5,758 rows for 8 features gave a much larger ratio, and its ensembles
  showed far less overfitting (Random Forest's default gap there was
  effectively 0, versus 0.203-0.239 here) despite using the same model
  families and similar hyperparameter defaults.
- **Hyperparameter tuning has a ceiling.** Constraining tree depth or
  adding regularization can only prevent a model from *using* capacity
  it doesn't have good data to support; it cannot manufacture the
  additional examples needed to make deeper, more expressive trees
  generalize reliably. The 25-iteration random search already explored
  a wide range of constraints, including fairly shallow, heavily
  regularized configurations, yet validation R² plateaued around 0.73.
- **Precedent in this dataset's own behavior.** Linear Regression,
  despite being the least flexible model tried, showed almost no
  overfitting (gap 0.054), confirming the issue isn't data quality or
  the models' inherent unsuitability, it's that the data is genuinely
  limited relative to how expressive the better-performing models need
  to be to capture BCF's non-linear structure.
- **Practical implication:** with more labeled BCF data, the same tuned
  XGBoost configuration would likely show both a higher validation R²
  and a narrower train-validation gap, without changing the modeling
  approach itself. This is a dataset-scale limitation rather than a
  methodological one, worth stating plainly given the OECD's emphasis on
  honest reporting of a model's limitations alongside its performance.

  **Decision: XGBoost (tuned) is the final model**, used going forward for
the BCF prediction layer.

## Model validation

### RDKit prediction pipeline

`src/bcf_descriptors.py` and `src/predict_bcf.py` were built and
validated the same way as the mutagenicity pipeline: all 15 descriptors
(the 8 shared with mutagenicity, already validated there, plus the 7
new ones, `NumAromaticRings`, `NumHAcceptors`, `NumHeteroatoms`,
`NumRotatableBonds`, `fr_COO`, `fr_COO2`, `fr_halogen`) were recomputed
via RDKit for a known training molecule and matched the CSV exactly.

### Residual error on a training molecule

The molecule with the corrupted CAS field (chlorinated pyridine
carboxylic acid, true value -1.700) showed a large prediction error
(predicted -0.603, diff 1.097). This was confirmed as a genuine model
residual, not a pipeline bug, by predicting directly from the CSV's
precomputed descriptors (bypassing RDKit entirely) and getting the same
result. With a tuned train R² of 0.913 (not 1.0), some training
molecules inevitably carry more residual error than others; this
appears to be one of them.

### Spread across 5 random training molecules

| True | Predicted | Diff |
|---|---|---|
| 0.930 | 1.107 | 0.177 |
| 3.477 | 3.245 | 0.232 |
| 0.278 | 0.985 | 0.707 |
| 2.510 | 1.862 | 0.648 |
| 2.421 | 2.013 | 0.408 |

Average difference (~0.43) is broadly consistent with the reported MAE
(0.505). The worst case in this sample was another sulfonated aromatic
amine, a structural family that may carry somewhat higher error
generally (worth further investigation if the model is extended).

### DDT: real-world validation on a novel molecule

DDT (`ClC(Cl)(c1ccc(Cl)cc1)c1ccc(Cl)cc1`, not in the training set) was
predicted at log(L/kg) = 4.14 (BCF ≈ 13,718 L/kg), near the top of the
training data's range (max 5.694). This is strongly consistent with
DDT's well-documented real-world status as one of the most extensively
studied bioaccumulative chemicals, a primary example cited in PBT
(persistent, bioaccumulative, toxic) substance classifications. This
validates that the halogen-driven relationship identified in EDA
(`fr_halogen` associated with ~10x higher BCF) generalizes correctly to
a genuinely novel, well-characterized molecule, not just within the
training distribution.

## Conclusion

The BCF regression phase is complete. XGBoost (tuned) is the final
model, achieving validation R² = 0.734 with RMSE = 0.679. Real-world
validation on DDT and spot-checks against training molecules confirm
the model has learned chemically meaningful, generalizable relationships
(halogenation driving higher bioaccumulation, polarity driving lower),
not just dataset-specific noise.

**The most promising path to further improving this model is more
labeled training data, not further tuning.** The persistent
train-validation overfitting gap (0.179 even after a 25-iteration
randomized search) is best explained by the dataset's small size (800
rows for 15 features) rather than suboptimal hyperparameters, as argued
earlier; Linear Regression's near-zero gap on the same data rules out
data quality as the cause. Additional BCF measurements, particularly
for underrepresented structural classes like the sulfonated aromatics
that showed higher residual error, would likely narrow this gap and
improve generalization beyond what hyperparameter tuning alone can
achieve.
