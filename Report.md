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