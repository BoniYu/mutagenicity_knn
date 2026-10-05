from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors

import json
from pathlib import Path



DESCRIPTOR_COLUMN_PATH = Path(__file__).resolve().parents[1] /"models"/ "bcf_descriptor_columns.json"

with open(DESCRIPTOR_COLUMN_PATH, "r") as f:
    BCF_DESCRIPTOR_COLUMNS = json.load(f)

def bcf_compute_descriptors(smiles: str) -> dict:
    """
    Computes molecular descriptors for a given SMILES string.

    Args:
        smiles (str): A SMILES string representing the molecule.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES string: {smiles}")
    return {
        'NumAromaticRings': rdMolDescriptors.CalcNumAromaticRings(mol),
        'NumHAcceptors': rdMolDescriptors.CalcNumHBA(mol),
        'NumHeteroatoms': rdMolDescriptors.CalcNumHeteroatoms(mol),
        'NumRotatableBonds': rdMolDescriptors.CalcNumRotatableBonds(mol),
        'NumValenceElectrons': Descriptors.NumValenceElectrons(mol),
        'qed': Descriptors.qed(mol),
        'TPSA': Descriptors.TPSA(mol),
        'MolMR': Descriptors.MolMR(mol),
        'BalabanJ': float(Descriptors.BalabanJ(mol)),
        'BertzCT': Descriptors.BertzCT(mol),
        'fr_COO': Descriptors.fr_COO(mol),
        'fr_COO2': Descriptors.fr_COO2(mol),
        'fr_halogen': Descriptors.fr_halogen(mol),
        'MolWt': Descriptors.MolWt(mol),
        'MolLogP': Descriptors.MolLogP(mol),
    }


if __name__ == "__main__":
    test_smiles = "O=C(O)c1nc(c(c(N)c1Cl)Cl)Cl"  #  or use your validated one from earlier
    result = bcf_compute_descriptors(test_smiles)
    print(result)     