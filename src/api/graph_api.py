

# no anda nada de esto 



# app/api/graph_api.py
from __future__ import annotations
import os, math, csv
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any

import networkx as nx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ... tus otros endpoints (ej. /route) sobre `router`
class Coord(BaseModel):
    lat: float
    lon: float


class RouteResp(BaseModel):
    total_distance_km: float
    node_ids: List[int]
    coords: List[Coord]
    # vessel_profile: dict
    # snapped: dict
    # warnings: List[str] = []

app = FastAPI(title="Graph API", version="1.0.0")

origins = os.getenv("CORS_ORIGINS", "*")
allow = origins.split(",") if origins and origins != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow,      # qué orígenes (dominios/puertos) pueden pegarle al API
    allow_credentials=True,   # si se permiten credenciales (cookies, Authorization, etc.)
    allow_methods=["*"],      # métodos HTTP permitidos (GET, POST, ...)
    allow_headers=["*"],      # headers permitidos (Content-Type, Authorization, ...)
)


@app.get("/health")
def health():
    return {"ok": True}

@app.on_event("startup")
def on_startup():
    base = Path(os.getenv("DATA_DIR", ".")).resolve()
    nodes = Path(os.getenv("NODES_CSV", "sudamerica_atlantico_sur_nodes.csv"))
    edges = Path(os.getenv("EDGES_CSV", "sudamerica_atlantico_sur_edges.csv"))
    nodes_path = nodes if nodes.is_absolute() else base / nodes
    edges_path = edges if edges.is_absolute() else base / edges


