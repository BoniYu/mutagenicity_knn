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

## Next steps

- Build `X` (features) and `y` (target).
- Baseline model (likely kNN regression, mirroring the classification
  project's structure).
- Compare kNN Regressor, Linear Regression, Random Forest Regressor,
  XGBoost Regressor via cross-validation (regression metrics: RMSE, MAE,
  R²).
- Given the small dataset size (800 rows vs. 5,758 for mutagenicity),
  cross-validation will be used as the primary evaluation method rather
  than a single train/test split.