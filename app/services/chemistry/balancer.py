from chempy import balance_stoichiometry

from app.services.chemistry.errors import ChemistryError


def balance(reactants: list[str], products: list[str]) -> tuple[dict[str, int], dict[str, int]]:
    try:
        left, right = balance_stoichiometry(set(reactants), set(products))
    except (ValueError, KeyError) as error:
        raise ChemistryError("unbalanceable", f"Cannot balance equation: {error}") from error

    # chempy returns sympy integers; keep the caller's species order.
    return (
        {formula: int(left[formula]) for formula in reactants},
        {formula: int(right[formula]) for formula in products},
    )


def format_equation(left: dict[str, int], right: dict[str, int]) -> str:
    def side(coefficients: dict[str, int]) -> str:
        return " + ".join(
            f"{count if count > 1 else ''}{formula}" for formula, count in coefficients.items()
        )

    return f"{side(left)} -> {side(right)}"
