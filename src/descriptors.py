from rdkit import Chem
from rdkit.Chem import Descriptors

import json
from pathlib import Path

DESCRIPTOR_COLUMN_PATH = Path(__file__).resolve().parents[1] /"models"/ "descriptor_columns.json"

with open(DESCRIPTOR_COLUMN_PATH, "r") as f:
    DESCRIPTOR_COLUMNS = json.load(f)

# Main Function
def compute_descriptors(smiles: str) -> dict:
    """
    Computes molecular descriptors for a given SMILES string.

    Args:
        smiles (str): A SMILES string representing the molecule.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES string: {smiles}")
    return {
        'NumValenceElectrons': Descriptors.NumValenceElectrons(mol),
        'qed': Descriptors.qed(mol),
        'TPSA': Descriptors.TPSA(mol),
        'MolMR': Descriptors.MolMR(mol),
        'BalabanJ': float(Descriptors.BalabanJ(mol)),
        'BertzCT': Descriptors.BertzCT(mol),
        'MolWt': Descriptors.MolWt(mol),
        'MolLogP': Descriptors.MolLogP(mol),
    }
     
    
if __name__ == "__main__":
    test_smiles = "CCO"  # ethanol, or use your validated one from earlier
    result = compute_descriptors(test_smiles)
    print(result)