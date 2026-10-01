"""Predict mutagenicity from a SMILES string using the trained model."""

import joblib
import pandas as pd
from pathlib import Path
from src.descriptors import compute_descriptors, DESCRIPTOR_COLUMNS

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "best_classifier.pkl"
model = joblib.load(MODEL_PATH)

def predict_mutagenicity(smiles: str) -> dict:
    """
    Predict mutagenicity for a molecule given its SMILES string.

    Args:
        smiles (str): A SMILES string representing the molecule.

    Returns:
        dict: prediction (0 or 1), label, and probability of the predicted class.
    """
    data = compute_descriptors(smiles)
    df = pd.DataFrame([data], columns=DESCRIPTOR_COLUMNS)

    prediction = model.predict(df)[0]
    probabilities = model.predict_proba(df)[0]

    label = "Mutagenic" if prediction == 1 else "Non-mutagenic"
    probability = probabilities[prediction]

    return {
        "prediction": int(prediction),
        "label": label,
        "probability": float(probability),
    }


if __name__ == "__main__":
    smiles = input("Enter a SMILES string: ")
    result = predict_mutagenicity(smiles)
    print(result)