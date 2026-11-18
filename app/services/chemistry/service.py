import asyncio
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Molecule, Reaction
from app.services.chemistry.balancer import balance, format_equation
from app.services.chemistry.errors import ChemistryError
from app.services.chemistry.parser import equation_key, parse_equation
from app.services.chemistry.reaction import build_reaction


async def list_molecules(db: AsyncSession) -> list[Molecule]:
    return list(await db.scalars(select(Molecule).order_by(Molecule.id)))


async def get_molecule(db: AsyncSession, formula: str) -> Molecule:
    molecule = await db.scalar(select(Molecule).where(Molecule.formula == formula))
    if molecule is None:
        raise ChemistryError(
            "unknown_molecule", f"{formula} is not in the catalog", formula=formula
        )
    return molecule


async def get_reaction(db: AsyncSession, equation: str) -> dict[str, Any]:
    reactants, products = parse_equation(equation)
    key = equation_key(reactants, products)

    cached = await db.scalar(select(Reaction).where(Reaction.equation_key == key))
    if cached is not None:
        return cached.data

    rows = await db.scalars(select(Molecule).where(Molecule.formula.in_(reactants + products)))
    structures = {row.formula: row.data for row in rows}
    missing = [formula for formula in reactants + products if formula not in structures]
    if missing:
        raise ChemistryError(
            "unknown_molecule", f"Not in the catalog: {', '.join(missing)}", formulas=missing
        )

    # chempy and scipy are CPU-bound, keep them off the event loop.
    left, right = await asyncio.to_thread(balance, reactants, products)
    geometry = await asyncio.to_thread(build_reaction, left, right, structures)
    data = {
        "equation_key": key,
        "balanced": format_equation(left, right),
        "reactants": [{"formula": f, "coefficient": c} for f, c in left.items()],
        "products": [{"formula": f, "coefficient": c} for f, c in right.items()],
        **geometry,
    }

    await db.execute(insert(Reaction).values(equation_key=key, data=data).on_conflict_do_nothing())
    await db.commit()
    return data
