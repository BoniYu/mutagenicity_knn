# Report: Mutagenicity QSPR — kNN Baseline

## Data

- 5,764 molecules from the Ames mutagenicity dataset (Hansen et al. 2009 benchmark
  merged with the Japan Health Ministry Ames (Q)SAR project).
- 8 precomputed descriptors: `NumValenceElectrons`, `qed`, `TPSA`, `MolMR`,
  `BalabanJ`, `BertzCT`, `MolWt`, `MolLogP`.
- Target: `Experimental value` (1 = mutagenic, 0 = non-mutagenic).
- 6 rows where VEGA returned "Non Predicted" were dropped, leaving 5,758 molecules.
- Class balance: 56.4% mutagenic, 43.6% non-mutagenic.

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