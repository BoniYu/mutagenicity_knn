"""Shared data loading for the mutagenicity QSPR project."""

from pathlib import Path
import pandas as pd

# Project root = parent of the src/ folder this file lives in
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "mutagenicity_kNN.csv"

TARGET_COL = "Experimental value"
NON_FEATURE_COLS = [
    "Unnamed: 0", "Id", "CAS", "SMILES", "Status",
    "Experimental value", "Predicted value",
]


def load_clean_data(path=DATA_PATH):
    """Load the dataset and drop rows where VEGA returned 'Non Predicted'."""
    df = pd.read_csv(path)
    df_clean = df[df["Predicted value"].isin(["0", "1"])]
    assert len(df_clean) == 5758, f"Expected 5758 rows, got {len(df_clean)}"
    return df_clean


def get_features_and_target(df_clean):
    """Return descriptor features X and the mutagenicity label y."""
    X = df_clean.drop(columns=NON_FEATURE_COLS)
    y = df_clean[TARGET_COL]
    return X, y