from pydantic import BaseModel, Field

from app.schemas.common import LocalizedText

type Vector3 = tuple[float, float, float]
# [begin atom index, end atom index, bond order]
type Bond = tuple[int, int, int]


class Atom(BaseModel):
    el: str
    pos: Vector3


class MoleculeStructure(BaseModel):
    atoms: list[Atom]
    bonds: list[Bond]


class MoleculeSummary(BaseModel):
    formula: str
    name: LocalizedText


class MoleculeDetail(MoleculeSummary):
    smiles: str
    structure: MoleculeStructure


class ReactionRequest(BaseModel):
    equation: str = Field(min_length=3, max_length=200, examples=["H2 + O2 -> H2O"])


class Species(BaseModel):
    formula: str
    coefficient: int


class ReactionAtom(Atom):
    molecule: int


class ReactionSide(BaseModel):
    atoms: list[ReactionAtom]
    bonds: list[Bond]


class ReactionDetail(BaseModel):
    equation_key: str
    balanced: str
    reactants: list[Species]
    products: list[Species]
    left: ReactionSide
    right: ReactionSide
    # [reactant atom index, product atom index]
    mapping: list[tuple[int, int]]
