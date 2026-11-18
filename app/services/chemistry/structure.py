from typing import Any

from rdkit import Chem
from rdkit.Chem import AllChem

from app.services.chemistry.errors import ChemistryError


def build_molecule(smiles: str) -> dict[str, Any]:
    """3D atom coordinates (Å, centred on the centroid) and bonds as [begin, end, order]."""
    parsed = Chem.MolFromSmiles(smiles)
    if parsed is None:
        raise ChemistryError("invalid_smiles", f"Invalid SMILES: {smiles!r}", smiles=smiles)

    molecule = Chem.AddHs(parsed)
    # Fixed seed keeps the geometry identical between seeding runs.
    if AllChem.EmbedMolecule(molecule, randomSeed=42) != 0:
        raise ChemistryError("embedding_failed", f"Cannot embed {smiles!r} in 3D", smiles=smiles)

    # MMFF has no parameters for some small species (H2, O2, CO, HCl), so fall back to UFF.
    if AllChem.MMFFHasAllMoleculeParams(molecule):
        AllChem.MMFFOptimizeMolecule(molecule)
    else:
        AllChem.UFFOptimizeMolecule(molecule)

    positions = molecule.GetConformer().GetPositions()
    centred = positions - positions.mean(axis=0)
    return {
        "atoms": [
            {"el": atom.GetSymbol(), "pos": [round(float(v), 3) for v in centred[atom.GetIdx()]]}
            for atom in molecule.GetAtoms()
        ],
        "bonds": [
            [bond.GetBeginAtomIdx(), bond.GetEndAtomIdx(), int(bond.GetBondTypeAsDouble())]
            for bond in molecule.GetBonds()
        ],
    }
