"""Predict Experimental value [log(L/kg)] from a SMILES string using the trained model."""

import joblib
import pandas as pd
from pathlib import Path
from src.bcf_descriptors import bcf_compute_descriptors, BCF_DESCRIPTOR_COLUMNS
 

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "best_bcf_regressor.pkl"
model_bcf = joblib.load(MODEL_PATH)

def predict_bcf(smiles: str) -> dict:
    """
    Predict BCF for a molecule given its SMILES string.

    Args:
        smiles (str): A SMILES string representing the molecule.
    """
    data = bcf_compute_descriptors(smiles)
    df = pd.DataFrame([data], columns=BCF_DESCRIPTOR_COLUMNS)

    prediction = model_bcf.predict(df)[0]

    return {
        "prediction_log": float(prediction),
        "prediction_bcf": float(10 ** prediction),
        "display": f"{10 ** prediction:.2f} L/kg, (log(L/kg): {prediction:.2f})"
    }

if __name__ == "__main__":
    smiles = input("Enter a SMILES string: ")
    result = predict_bcf(smiles)
    print(result)
