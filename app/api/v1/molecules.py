from fastapi import APIRouter

from app.core.database import DbSession
from app.schemas.chemistry import MoleculeDetail, MoleculeSummary
from app.services.chemistry import service

router = APIRouter(prefix="/molecules", tags=["chemistry"])


@router.get("")
async def list_molecules(db: DbSession) -> list[MoleculeSummary]:
    molecules = await service.list_molecules(db)
    return [
        MoleculeSummary.model_validate({"formula": m.formula, "name": m.name}) for m in molecules
    ]


@router.get("/{formula}")
async def get_molecule(formula: str, db: DbSession) -> MoleculeDetail:
    molecule = await service.get_molecule(db, formula)
    return MoleculeDetail.model_validate(
        {
            "formula": molecule.formula,
            "name": molecule.name,
            "smiles": molecule.smiles,
            "structure": molecule.data,
        }
    )
