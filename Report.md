# Report: Mutagenicity QSPR — kNN Baseline

## Dataset

- 5,764 molecules from the Ames mutagenicity dataset (Hansen et al. 2009
  benchmark merged with the Japan Health Ministry Ames (Q)SAR project).
- **Features:** 8 precomputed descriptors: `NumValenceElectrons`, `qed`,
  `TPSA`, `MolMR`, `BalabanJ`, `BertzCT`, `MolWt`, `MolLogP`.
- **Target:** `Experimental value` (1 = mutagenic, 0 = non-mutagenic).
- **Cleaning:** 6 rows where VEGA returned "Non Predicted" were removed,
  leaving 5,758 molecules.
- **Class balance:** about 56.4% mutagenic and 43.6% non-mutagenic.

## Methodology

- Features standardised with `StandardScaler`, fit on training data only
  (or per fold, for cross-validated evaluations).
- Models compared: kNN, Logistic Regression, Random Forest, XGBoost.
- k for kNN selected via 10-fold cross-validation.
- kNN also assessed with leave-one-out CV, to compare on equal footing with
  VEGA, whose developers used the same protocol.
- All four models compared with stratified 10-fold CV, reporting mean ± std
  for accuracy, F1 and ROC-AUC.
- XGBoost additionally tuned via `RandomizedSearchCV`.
- Benchmark: VEGA kNN reaches accuracy 0.800 and F1 0.824 on this dataset.

## VEGA benchmark

Evaluated over the full cleaned dataset (5,758 molecules), following VEGA's own
published evaluation protocol:

| Metric | Value |
|---|---|
| Accuracy | 0.800 |
| Precision | 0.817 |
| Recall | 0.832 |
| F1 | 0.824 |

## kNN — single train/test split (80/20, random_state=42)

k = 3, features standardised with `StandardScaler` fit on the training set only.

| Metric | Value |
|---|---|
| Accuracy | 0.699 |
| Precision | 0.722 |
| Recall | 0.754 |
| F1 | 0.738 |
| ROC-AUC | 0.691 |

## kNN — hyperparameter tuning

**k sweep, single validation split (90/10 of training data):** validation error
lowest around k ≈ 7–13, consistent with the tutorial's single-split curve.

**k sweep, 10-fold cross-validation** (`Pipeline` with `StandardScaler` +
`KNeighborsClassifier`, refit per fold to avoid leakage): validation
misclassification rate is flat at ~0.29–0.30 across roughly k = 7 to k = 40+.
Minimum at **k = 24**.

## kNN — leave-one-out evaluation

LOO used to compare against VEGA on equal footing, since VEGA's developers
evaluated it the same way. Scaler refit inside each fold.

| | k = 3 | k = 24 |
|---|---|---|
| Accuracy | 0.707 | 0.707 |
| Precision | 0.732 | 0.732 |
| Recall | 0.759 | 0.757 |
| F1 | 0.745 | 0.745 |

## Finding: tuning k did not improve performance

Despite the 10-fold CV sweep identifying k=24 as optimal, LOO performance is
essentially identical between k=3 and k=24. This is consistent with the CV
validation curve, which is flat across this whole range rather than showing a
sharp minimum.

**Interpretation:** kNN's performance on this dataset is capped by the
descriptor set (8 general physicochemical/topological descriptors), not by
the choice of k. This is a plausible partial explanation for the gap to
VEGA's 0.800 accuracy — VEGA's similarity measure likely captures more
structural detail than these 8 descriptors do.

## Open questions for the model comparison phase

- Can Logistic Regression, Random Forest or XGBoost close some of the gap to
  VEGA using the same 8 descriptors?
- Is the ~70% ceiling a property of the descriptor set (testable later with
  RDKit-derived fingerprints), or a limit of what any model can extract from
  this feature set?

## Model comparison (stratified 10-fold CV, default hyperparameters)

All models used the same 8 descriptors, standardised with `StandardScaler`
inside a `Pipeline` (fit per fold to avoid leakage). kNN used k=24, the value
selected by the earlier CV sweep.

| Model | Accuracy | F1 | ROC-AUC |
|---|---|---|---|
| kNN (k=24) | 0.709 ± 0.026 | 0.748 ± 0.023 | 0.770 ± 0.022 |
| Logistic Regression | 0.652 ± 0.023 | 0.710 ± 0.020 | 0.713 ± 0.022 |
| Random Forest | **0.748 ± 0.010** | **0.779 ± 0.010** | **0.820 ± 0.015** |
| XGBoost | 0.738 ± 0.014 | 0.774 ± 0.016 | 0.805 ± 0.017 |
| VEGA (benchmark, whole dataset) | 0.800 | 0.824 | n/a |

**Random Forest is the strongest model at default settings**, ahead of
XGBoost on every metric and with the tightest fold-to-fold variance (bagging's
variance-reduction advantage on a moderate-sized, low-dimensional dataset).
XGBoost is close behind and would likely benefit most from tuning
(`n_estimators`, `max_depth`, `learning_rate`, regularization), since its
main strength (iterative error correction) needs more headroom than default
settings give it here.

**Logistic Regression underperforms even the untuned kNN baseline**,
suggesting the relationship between these 8 descriptors and mutagenicity
isn't well captured by a linear decision boundary. Kept in the comparison as
the interpretable benchmark, consistent with the OECD's mechanistic
interpretation principle, despite not being competitive on accuracy.

**Random Forest closes roughly a third of the gap to VEGA** seen with kNN
(F1 0.779 vs. VEGA's 0.824, compared to kNN's 0.745–0.748), using the same
descriptor set — evidence that model choice, not just features, was
limiting kNN's ceiling.

## Open questions, updated

- Would tuning XGBoost (or Random Forest) close more of the remaining gap to
  VEGA, or is the descriptor set now the binding constraint?
- Feature importances (Random Forest, XGBoost) vs. Logistic Regression
  coefficients — do they agree on which descriptors matter most?  

## XGBoost hyperparameter tuning

Tuned via `RandomizedSearchCV` (25 iterations, stratified 10-fold CV,
optimizing F1) over `n_estimators`, `max_depth`, `learning_rate`,
`subsample`, `colsample_bytree`, `reg_alpha`, `reg_lambda`.

| | Accuracy | F1 | ROC-AUC |
|---|---|---|---|
| XGBoost (default) | 0.738 ± 0.014 | 0.774 ± 0.016 | 0.805 ± 0.017 |
| XGBoost (tuned) | 0.743 ± 0.018 | 0.775 ± 0.015 | 0.806 ± 0.018 |
| Random Forest (default) | **0.748 ± 0.010** | **0.779 ± 0.010** | **0.820 ± 0.015** |

Tuning gave a small, real improvement over XGBoost's own default (F1 0.774 →
0.775), but the tuned model still didn't reach Random Forest's default
performance on any metric, and its fold-to-fold variance was slightly wider
than the untuned version, not tighter.

## Why Random Forest is not tuned further

Random Forest is kept at default hyperparameters, for two reasons:

1. **Its variance at default is already low** (±0.010 accuracy across folds,
   the tightest of all models tested), which suggests it's already close to
   what this descriptor set and model family can extract, further tuning
   (mainly `n_estimators`, `max_depth`, `min_samples_leaf`) has little
   variance left to reduce.
2. **A real tuning effort on its closest competitor didn't beat it.** XGBoost
   was tuned via a 25-iteration randomized search (250 fits) over its most
   impactful hyperparameters, and still fell short of Random Forest's
   untuned result on every metric. This is treated as sufficient evidence
   that ~0.748 accuracy / ~0.779 F1 is close to the practical ceiling for
   tree-ensemble models on these 8 descriptors, rather than an artifact of
   insufficient tuning.

**Conclusion: Random Forest (default hyperparameters) is the final model**,
used going forward for the RDKit/SMILES prediction layer.

## Remaining open questions

- Would a richer feature set (e.g. RDKit fingerprints, rather than the 8
  precomputed descriptors) raise this ceiling, or is ~0.75-0.78 close to
  what's achievable on this dataset regardless of features?
- Feature importances (Random Forest) vs. Logistic Regression coefficients —
  do they agree on which descriptors matter most?  

## RDKit prediction layer

Built `src/descriptors.py` (SMILES → 8 descriptors, matching the training
feature set) and `src/predict.py` (descriptors → scaled → Random Forest →
prediction + confidence). Descriptor correctness was verified by comparing
RDKit-computed values against a known training-set molecule's precomputed
descriptors in the original CSV; values matched.

### Case study: nitrobenzene

Nitrobenzene (`O=[N+]([O-])c1ccccc1`, CAS 98-95-3) was used as a test case,
since nitro groups are a commonly cited mutagenicity-associated structural
feature. The model predicted **non-mutagenic (85% confidence)**.

Checking against the dataset confirmed nitrobenzene is in the training set
(row 5530), with a true experimental label of **non-mutagenic**, matching
the model's prediction. (An initial exact-string SMILES lookup missed this
row, since the dataset wrote the molecule with a different, but chemically
equivalent, atom ordering; a canonical-SMILES comparison found it.)

This is a useful illustration that structural alerts (like a nitro group)
are statistical tendencies across many molecules, not deterministic rules
for any individual molecule, context in the rest of the structure matters,
and that lookups comparing molecules by SMILES string must canonicalize
first, since the same molecule can be written multiple valid ways.

## Next: applicability domain check

`predict.py` currently returns a prediction for any valid SMILES, with no
indication of whether the molecule resembles anything in the training set.
The next phase adds a fingerprint-based (Tanimoto similarity) applicability
domain check, following VEGA's approach, so predictions on truly novel
molecules can be flagged as lower-confidence rather than presented with the
same apparent certainty as predictions on well-represented chemical space.  