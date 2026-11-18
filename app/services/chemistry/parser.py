import re

from app.services.chemistry.errors import ChemistryError

ARROW_PATTERN = re.compile(r"\s*(?:->|→|=>|=)\s*")
LEADING_COEFFICIENT = re.compile(r"^\d+\s*")
FORMULA_PATTERN = re.compile(r"^(?:[A-Z][a-z]?\d*|\((?:[A-Z][a-z]?\d*)+\)\d+)+$")


def _parse_side(side: str) -> list[str]:
    formulas = [LEADING_COEFFICIENT.sub("", part.strip()) for part in side.split("+")]
    for formula in formulas:
        if not FORMULA_PATTERN.match(formula):
            raise ChemistryError(
                "invalid_formula", f"Invalid formula: {formula!r}", formula=formula
            )
    return formulas


def parse_equation(equation: str) -> tuple[list[str], list[str]]:
    """Split 'H2 + O2 -> H2O' into species; user coefficients are dropped because we rebalance."""
    sides = ARROW_PATTERN.split(equation.strip())
    if len(sides) != 2 or not all(sides):
        raise ChemistryError("invalid_equation", "Equation must have exactly one arrow")

    reactants, products = (_parse_side(side) for side in sides)
    if len(set(reactants)) != len(reactants) or len(set(products)) != len(products):
        raise ChemistryError("invalid_equation", "A species is repeated on one side")
    if set(reactants) & set(products):
        raise ChemistryError("invalid_equation", "A species appears on both sides")
    return reactants, products


def equation_key(reactants: list[str], products: list[str]) -> str:
    return f"{' + '.join(sorted(reactants))} -> {' + '.join(sorted(products))}"
