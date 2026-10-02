from rdkit import Chem, DataStructs
from rdkit.Chem import rdFingerprintGenerator
from src.data_loader import load_clean_data, get_features_and_target

# Initialize the Morgan fingerprint generator
generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
# Generate fingerprints for the training data
df_clean = load_clean_data()
training_fingerprints = [generator.GetFingerprint(Chem.MolFromSmiles(s)) for s in df_clean['SMILES']]

# Function to check similarity of a new molecule to the training set 
def check_applicability_domain(smiles, threshold=0.7):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES string: {smiles}")

    fp_new = generator.GetFingerprint(mol)
    similarities = DataStructs.BulkTanimotoSimilarity(fp_new, training_fingerprints)
    max_similarity = max(similarities)

    return {
        'max_similarity': max_similarity,
        'in_domain': max_similarity >= threshold,
        'threshold': threshold,
    }
