import rasterio
import numpy as np
import pandas as pd
import networkx as nx
from scipy.ndimage import distance_transform_edt
from skimage.transform import resize
from scipy.spatial import cKDTree
from pathlib import Path
from geopy.distance import geodesic

# === CONFIGURACIÓN GENERAL ===
data_dir = Path("../data")         # carpeta donde están los .tif
ports_file = data_dir / "UpdatedPub150.csv"  # archivo de puertos
coastal_threshold = 50             # píxeles para considerar "costa"
step_coast = 3                     # densidad cerca de tierra
step_open = 100                    # densidad mar adentro
resize_factor = 1.0
max_connection_km = 50             # radio máximo de conexión (~50 km)
k_neighbors = 4                    # cantidad de vecinos más cercanos


# === FUNCIONES AUXILIARES ===
def haversine_distance(lat1, lon1, lat2, lon2):
    """Distancia en km entre dos coordenadas (usa geodesic)."""
    return geodesic((lat1, lon1), (lat2, lon2)).km

def path_is_over_ocean(i1, j1, i2, j2, ocean_mask, num_points=20):
    """Verifica si el segmento entre dos nodos pasa solo por océano."""
    rows = np.linspace(i1, i2, num_points).astype(int)
    cols = np.linspace(j1, j2, num_points).astype(int)
    return np.all(ocean_mask[rows, cols])

# === 1. Leer puertos (PUB150) ===
ports_df = pd.read_csv(ports_file)


# Normalizar nombres
ports_df.columns = [c.strip().lower().replace(" ", "") for c in ports_df.columns]

# Fijar columnas directamente
lat_col = "latitude"
lon_col = "longitude"


print(f"⚙️ {len(ports_df)} puertos con coordenadas válidas después de limpieza.\n")


print(f"⚓ Se cargaron {len(ports_df)} puertos desde {ports_file.name}")

# === 2. Procesar todos los archivos .tif ===
tif_files = list(data_dir.glob("*.tif"))
print(f"🌍 Se encontraron {len(tif_files)} archivos TIFF en {data_dir}")

for tif_path in tif_files:
    print(f"\n🌊 Procesando: {tif_path.name}")

    # === 3. Leer el archivo GEBCO ===
    with rasterio.open(tif_path) as src:
        elev = src.read(1)
        transform = src.transform
        bounds = src.bounds  # para saber lat/lon del área cubierta

    # Calcular límites geográficos
    lon_min, lat_min, lon_max, lat_max = bounds.left, bounds.bottom, bounds.right, bounds.top
    print(f"📍 Extensión geográfica: Lon({lon_min} → {lon_max}), Lat({lat_min} → {lat_max})")

    if resize_factor < 1.0:
        elev = resize(elev,
                      (int(elev.shape[0]*resize_factor),
                       int(elev.shape[1]*resize_factor)),
                      anti_aliasing=True)

    # === 4. Crear máscara del océano ===
    ocean_mask = elev < 0
    if not np.any(ocean_mask):
        print("⚠️ Sin océano, saltando.")
        continue

    dist_to_land = distance_transform_edt(ocean_mask == 1)

    # === 5. Generar nodos oceánicos ===
    points = []
    rows, cols = elev.shape
    for i in range(0, rows, 5):
        for j in range(0, cols, 5):
            if ocean_mask[i, j]:
                d = dist_to_land[i, j]
                if d < coastal_threshold:
                    if (i % step_coast == 0) and (j % step_coast == 0):
                        points.append((i, j, elev[i, j]))
                else:
                    if (i % step_open == 0) and (j % step_open == 0):
                        points.append((i, j, elev[i, j]))

    points = np.array(points)
    print(f"→ {len(points)} nodos oceánicos")

    if len(points) == 0:
        continue

    # === 6. Convertir índices a coordenadas geográficas ===
    lats, lons, depths = [], [], []
    for i, j, depth in points:
        lon, lat = rasterio.transform.xy(transform, i, j)
        lats.append(lat)
        lons.append(lon)
        depths.append(depth)

    nodes_df = pd.DataFrame({
        "latitud": lats,
        "longitud": lons,
        "profundidad": depths
    })

    # === 7. Agregar puertos dentro del área del .tif ===
    ports_in_tile = ports_df[
        (ports_df[lat_col] >= lat_min) & (ports_df[lat_col] <= lat_max) &
        (ports_df[lon_col] >= lon_min) & (ports_df[lon_col] <= lon_max)
    ].copy()

    if ports_in_tile is not None and len(ports_in_tile) > 0:
        print(f"⚓ Agregando {len(ports_in_tile)} puertos en esta región...")

        # Asegurar que las columnas existan y sean numéricas
        ports_in_tile = ports_in_tile.copy()
        ports_in_tile[lat_col] = pd.to_numeric(ports_in_tile[lat_col], errors="coerce")
        ports_in_tile[lon_col] = pd.to_numeric(ports_in_tile[lon_col], errors="coerce")
        ports_in_tile = ports_in_tile.dropna(subset=[lat_col, lon_col])

        if len(ports_in_tile) > 0:
            port_nodes = pd.DataFrame({
                "latitud": ports_in_tile[lat_col].values,
                "longitud": ports_in_tile[lon_col].values,
                "profundidad": np.zeros(len(ports_in_tile))  # nivel del mar
            })
            nodes_df = pd.concat([nodes_df, port_nodes], ignore_index=True)
            print(f"✅ {len(port_nodes)} puertos agregados como nodos.")
        else:
            print("⚓ Todos los puertos en esta región tenían coordenadas inválidas. Saltando...")
    else:
        print("⚓ Sin puertos en esta región.")


    # === 8. Crear conexiones (usando KDTree) ===
    print("🔗 Generando conexiones entre nodos...")
    coords = np.column_stack((nodes_df["latitud"], nodes_df["longitud"]))
    tree = cKDTree(coords)

    edges = []
    G = nx.Graph()

    for idx1, n1 in nodes_df.iterrows():
        lat1, lon1 = n1["latitud"], n1["longitud"]
        i1, j1 = None, None
        if idx1 < len(points):  # si es nodo oceánico
            i1, j1, _ = points[idx1]

        dists, indices = tree.query((lat1, lon1), k=k_neighbors + 1)
        for dist, idx2 in zip(dists[1:], indices[1:]):
            if np.isnan(dist):
                continue
            n2 = nodes_df.loc[idx2]
            lat2, lon2 = n2["latitud"], n2["longitud"]

            dist_km = haversine_distance(lat1, lon1, lat2, lon2)
            if dist_km > max_connection_km:
                continue

            # Verificar que esté sobre océano (solo si ambos son oceánicos)
            if (i1 is not None) and (idx2 < len(points)):
                i2, j2, _ = points[idx2]
                if not path_is_over_ocean(i1, j1, i2, j2, ocean_mask):
                    continue

            edges.append({
                "lat_origen": lat1,
                "lon_origen": lon1,
                "lat_destino": lat2,
                "lon_destino": lon2,
                "distancia_km": dist_km
            })
            G.add_edge(idx1, idx2, weight=dist_km)

    print(f"✅ {len(edges)} conexiones válidas creadas")

    # === 9. Calcular árbol mínimo de conexiones ===
    shortest_edges = []
    for u, v, data in nx.minimum_spanning_edges(G, data=True):
        n1 = nodes_df.loc[u]
        n2 = nodes_df.loc[v]
        shortest_edges.append({
            "lat_origen": n1["latitud"],
            "lon_origen": n1["longitud"],
            "lat_destino": n2["latitud"],
            "lon_destino": n2["longitud"],
            "distancia_km": data["weight"]
        })

    # === 10. Guardar CSVs ===
    nodes_csv = data_dir / f"{tif_path.stem}_nodes.csv"
    edges_csv = data_dir / f"{tif_path.stem}_edges.csv"

    nodes_df.to_csv(nodes_csv, index=False)
    pd.DataFrame(shortest_edges).to_csv(edges_csv, index=False)

    print(f"🗺️ Nodos guardados en: {nodes_csv.name}")
    print(f"🧭 Aristas guardadas en: {edges_csv.name}")

print("\n🎉 Grafo completo generado para todos los archivos con puertos incluidos.")
