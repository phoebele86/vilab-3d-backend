import mimetypes
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1 import api_router
from app.core.config import settings

mimetypes.add_type("model/gltf-binary", ".glb")

app = FastAPI(title="ViLab 3D API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# Local development only: serve 3D files from the sibling assets repo.
if settings.assets_dir and Path(settings.assets_dir).is_dir():
    app.mount("/api/assets", StaticFiles(directory=settings.assets_dir), name="assets")
