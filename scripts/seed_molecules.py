import asyncio
import csv
from pathlib import Path

from sqlalchemy.dialects.postgresql import insert

from app.core.database import SessionLocal, engine
from app.models import Molecule
from app.services.chemistry.structure import build_molecule

CATALOG_PATH = Path(__file__).resolve().parents[1] / "data" / "molecules_catalog.csv"


async def seed_molecules() -> int:
    with CATALOG_PATH.open(encoding="utf-8") as file:
        rows = [
            {
                "formula": row["formula"],
                "name": {"vi": row["name_vi"], "en": row["name_en"] or None},
                "smiles": row["smiles"],
                "data": build_molecule(row["smiles"]),
                "source": "rdkit",
            }
            for row in csv.DictReader(file)
        ]

    statement = insert(Molecule).values(rows)
    async with SessionLocal() as session:
        await session.execute(
            statement.on_conflict_do_update(
                index_elements=[Molecule.formula],
                set_={
                    "name": statement.excluded.name,
                    "smiles": statement.excluded.smiles,
                    "data": statement.excluded.data,
                    "source": statement.excluded.source,
                },
            )
        )
        await session.commit()
    await engine.dispose()
    return len(rows)


if __name__ == "__main__":
    print(f"Seeded {asyncio.run(seed_molecules())} molecules")
