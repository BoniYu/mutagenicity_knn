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
4. **Further extensions (TBD)** — e.g. RDKit-generated descriptors instead
   of precomputed ones, a different chem-eng-relevant target property,
   model comparison beyond kNN, deployment as an interactive tool.

## Project structure
data/ raw datasets
notebooks/ exploratory and modeling notebooks
src/ reusable scripts (data download, preprocessing, modeling)
models/ saved trained models
reports/ figures, writeups, results


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

🚧 In progress — currently replicating the base tutorial.