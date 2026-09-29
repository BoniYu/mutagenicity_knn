# kNN QSPR

A machine learning project building k-nearest neighbours (kNN) (Q)SPR
(quantitative structure-property relationship) models to predict chemical
properties from molecular descriptors.

Starting point: the [MLCE_book kNN QSPR tutorial](https://edgarsmdn.github.io/MLCE_book/02_kNN_QSPR.html)
by Edgar Sanchez Medina, Antonio del Rio Chanona and Caroline Ganzer.
Dataset source: [MLCE_book repository](https://github.com/edgarsmdn/MLCE_book).

## Project plan

1. **Replicate the tutorial** — kNN classifier predicting Ames test
   mutagenicity from precomputed molecular descriptors, with train/test
   split, feature scaling, and comparison against the published VEGA kNN
   model.
2. **Hyperparameter tuning** — find the best k via validation split and
   k-fold cross-validation; evaluate with leave-one-out CV.
3. **Extend to regression** — bioconcentration factor (BCF) prediction,
   using the same workflow.
4. **Model comparison** — kNN vs Logistic Regression, Random Forest and XGBoost.
5. **Further extensions (planned)** — applicability domain check, RDKit
   descriptor calculation from SMILES, and deployment as a Streamlit app.

## Why this project

Mutagenicity is a key endpoint in chemical safety and regulatory assessment
(e.g. under REACH), where validated (Q)SAR predictions can support or replace
experimental testing. This project builds and compares interpretable ML models
for this endpoint.

## Dataset & Methodology

5,758 molecules, 8 precomputed descriptors, predicting Ames mutagenicity.

## Results

| Model | Accuracy | F1 | ROC-AUC |
|---|---|---|---|
| kNN (k = 24) | 0.709 ± 0.026 | 0.748 ± 0.023 | 0.770 ± 0.022 |
| Logistic Regression | 0.652 ± 0.023 | 0.710 ± 0.020 | 0.713 ± 0.022 |
| **Random Forest (final model)** | **0.748 ± 0.010** | **0.779 ± 0.010** | **0.820 ± 0.015** |
| XGBoost (tuned) | 0.743 ± 0.018 | 0.775 ± 0.015 | 0.806 ± 0.018 |
| VEGA kNN (benchmark) | 0.800 | 0.824 | n/a |

Random Forest, at default hyperparameters, was selected as the final model.


## Limitations

- VEGA's metrics cover the whole dataset and VEGA has effectively seen these
  molecules, so it is a benchmark to aim for rather than a strict like-for-like
  comparison.
- Only 8 generic descriptors are used; local reactive substructures that drive
  mutagenicity are not captured directly.
- Single-split results vary by a few points with the random seed, hence the
  use of cross-validation for the final comparison.




## Setup

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Data

- `mutagenicity_kNN.csv`: https://raw.githubusercontent.com/edgarsmdn/MLCE_book/main/references/mutagenicity_kNN.csv
- `BCF_training.csv`: https://raw.githubusercontent.com/edgarsmdn/MLCE_book/main/references/BCF_training.csv

## Status

✅ Classification phase complete — Random Forest selected as final model.
🚧 Next: RDKit/SMILES prediction layer, then BCF regression extension.

See [`Report.md`](Report.md) for detailed methodology and results.

## Trained model

The trained model (`models/best_classifier.pkl`) and descriptor column
order (`models/descriptor_columns.json`) are not tracked in git. To
regenerate them, run `notebooks/02_classification_models.ipynb` end to end.