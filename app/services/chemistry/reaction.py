import math
from typing import Any

import numpy as np
from scipy.optimize import linear_sum_assignment

ATOM_PADDING = 1.2
GRID_GAP = 0.8


def _layout_side(
    coefficients: dict[str, int], structures: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Expand species by coefficient and place each molecule copy on a grid centred at origin."""
    instances = [
        structures[formula] for formula, count in coefficients.items() for _ in range(count)
    ]
    radius = max(
        max((math.dist(atom["pos"], (0, 0, 0)) for atom in s["atoms"]), default=0)
        for s in instances
    )
    cell = 2 * (radius + ATOM_PADDING) + GRID_GAP
    columns = math.ceil(math.sqrt(len(instances)))
    rows = math.ceil(len(instances) / columns)

    atoms: list[dict[str, Any]] = []
    bonds: list[list[int]] = []
    for index, structure in enumerate(instances):
        row, column = divmod(index, columns)
        offset = ((column - (columns - 1) / 2) * cell, ((rows - 1) / 2 - row) * cell, 0.0)
        base = len(atoms)
        atoms.extend(
            {
                "el": atom["el"],
                "pos": [round(p + o, 3) for p, o in zip(atom["pos"], offset, strict=True)],
                "molecule": index,
            }
            for atom in structure["atoms"]
        )
        bonds.extend([base + a, base + b, order] for a, b, order in structure["bonds"])
    return {"atoms": atoms, "bonds": bonds}


def _map_atoms(left: list[dict[str, Any]], right: list[dict[str, Any]]) -> list[list[int]]:
    """Pair each reactant atom with a product atom of the same element, minimising travel."""
    mapping: list[list[int]] = []
    for element in sorted({atom["el"] for atom in left}):
        left_ids = [i for i, atom in enumerate(left) if atom["el"] == element]
        right_ids = [i for i, atom in enumerate(right) if atom["el"] == element]
        cost = np.array(
            [[math.dist(left[i]["pos"], right[j]["pos"]) for j in right_ids] for i in left_ids]
        )
        rows, columns = linear_sum_assignment(cost)
        mapping.extend([left_ids[r], right_ids[c]] for r, c in zip(rows, columns, strict=True))
    return sorted(mapping)


def build_reaction(
    left: dict[str, int], right: dict[str, int], structures: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    left_side = _layout_side(left, structures)
    right_side = _layout_side(right, structures)
    return {
        "left": left_side,
        "right": right_side,
        "mapping": _map_atoms(left_side["atoms"], right_side["atoms"]),
    }
