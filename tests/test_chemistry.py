from collections import Counter

import pytest

from app.services.chemistry.balancer import balance, format_equation
from app.services.chemistry.errors import ChemistryError
from app.services.chemistry.parser import equation_key, parse_equation
from app.services.chemistry.reaction import build_reaction
from app.services.chemistry.structure import build_molecule

SMILES = {"H2": "[H][H]", "O2": "O=O", "H2O": "O", "CH4": "C", "CO2": "O=C=O"}


@pytest.mark.parametrize("arrow", ["->", "→", "=", "=>"])
def test_parse_equation_accepts_arrows_and_drops_coefficients(arrow: str) -> None:
    assert parse_equation(f"2H2 + O2 {arrow} 2H2O") == (["H2", "O2"], ["H2O"])


@pytest.mark.parametrize("equation", ["H2 + O2", "H2 -> O2 -> H2O", "h2 -> H2O", "H2 + H2 -> H4"])
def test_parse_equation_rejects_malformed_input(equation: str) -> None:
    with pytest.raises(ChemistryError):
        parse_equation(equation)


def test_equation_key_ignores_species_order() -> None:
    assert equation_key(["O2", "H2"], ["H2O"]) == equation_key(["H2", "O2"], ["H2O"])


def test_balance_methane_combustion() -> None:
    left, right = balance(["CH4", "O2"], ["CO2", "H2O"])

    assert left == {"CH4": 1, "O2": 2}
    assert right == {"CO2": 1, "H2O": 2}
    assert format_equation(left, right) == "CH4 + 2O2 -> CO2 + 2H2O"


def test_balance_rejects_impossible_reaction() -> None:
    with pytest.raises(ChemistryError) as error:
        balance(["H2"], ["O2"])
    assert error.value.code == "unbalanceable"


def test_build_molecule_keeps_bond_orders() -> None:
    carbon_dioxide = build_molecule("O=C=O")

    assert [atom["el"] for atom in carbon_dioxide["atoms"]] == ["O", "C", "O"]
    assert sorted(order for *_, order in carbon_dioxide["bonds"]) == [2, 2]


def test_reaction_conserves_and_maps_every_atom() -> None:
    structures = {formula: build_molecule(smiles) for formula, smiles in SMILES.items()}
    left, right = balance(["CH4", "O2"], ["CO2", "H2O"])
    reaction = build_reaction(left, right, structures)

    left_atoms, right_atoms = reaction["left"]["atoms"], reaction["right"]["atoms"]
    assert Counter(a["el"] for a in left_atoms) == Counter(a["el"] for a in right_atoms)
    assert sorted(i for i, _ in reaction["mapping"]) == list(range(len(left_atoms)))
    assert sorted(j for _, j in reaction["mapping"]) == list(range(len(right_atoms)))
    assert all(left_atoms[i]["el"] == right_atoms[j]["el"] for i, j in reaction["mapping"])
