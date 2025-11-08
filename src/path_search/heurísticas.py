import math
from typing import Tuple, Optional

Coord = Tuple[int, int]

def manhattan_steps(a: Coord, b: Coord) -> int:
    """Pasos mínimos en una grilla 4-vecinos."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# ---------- 1) Heurística de TIEMPO (ruta más rápida) ----------
def h_time(n: Coord,
           goal: Coord,
           *,
           cell_nm: float = 1.0,      # millas náuticas por celda
           v_max_kn: float = 20.0     # velocidad máxima posible (nudos)
           ) -> float:
    """
    Lower bound del tiempo restante (horas).
    Admisible: asume mejor caso (ir en línea recta y a v_max sin penalizaciones).
    """
    steps = manhattan_steps(n, goal)
    per_step_time_h = cell_nm / max(1e-9, v_max_kn)  # h = d/v_max
    return steps * per_step_time_h

# ---------- 2) Heurística de COMBUSTIBLE (menor consumo) ----------
def h_fuel(n: Coord,
           goal: Coord,
           *,
           cell_nm: float = 1.0,         # millas náuticas por celda
           fuel_per_nm_base: float = 0.05  # consumo base (p.ej., toneladas por NM)
           ) -> float:
    """
    Lower bound del combustible restante.
    Admisible: asume mar calmo (sin viento/olas ni penalizaciones).
    """
    steps = manhattan_steps(n, goal)
    per_step_fuel = fuel_per_nm_base * cell_nm
    return steps * per_step_fuel

# ---------- 3) Heurística de SEGURIDAD (ruta más segura) ----------
def h_safe(n: Coord,
           goal: Coord,
           *,
           global_min_edge_risk: Optional[float] = 0.0
           ) -> float:
    """
    Lower bound del 'riesgo' acumulado restante.
    Si desconocés el mínimo global de riesgo o hay aristas con riesgo 0, usa 0.0 (admisible).
    Si sabés que TODAS las aristas tienen riesgo >= r_min > 0, ponelo para tener una h más informativa.
    """
    steps = manhattan_steps(n, goal)
    r_min = max(0.0, float(global_min_edge_risk or 0.0))
    return steps * r_min


# ---------- Heurística combinada (tiempo + combustible + seguridad) ----------
def h_combined(n: Coord,    
                goal: Coord,
                *,
                cell_nm: float = 1.0,
                v_max_kn: float = 20.0,
                fuel_per_nm_base: float = 0.05,
                global_min_edge_risk: Optional[float] = 0.0,
                w_time: float = 1.0,
                w_fuel: float = 1.0,
                w_safe: float = 1.0
                ) -> float:
     """
     Heurística combinada ponderada de tiempo, combustible y seguridad.
     """
     h_t = h_time(n, goal, cell_nm=cell_nm, v_max_kn=v_max_kn)
     h_f = h_fuel(n, goal, cell_nm=cell_nm, fuel_per_nm_base=fuel_per_nm_base)
     h_s = h_safe(n, goal, global_min_edge_risk=global_min_edge_risk)
     return w_time * h_t + w_fuel * h_f + w_safe * h_s