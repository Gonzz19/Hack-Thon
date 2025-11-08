import rasterio
import numpy as np
import pandas as pd
from scipy.ndimage import distance_transform_edt
from skimage.transform import resize
from pathlib import Path

# === 1. Configuración general ===
data_dir = Path("../data")   # carpeta donde están los .tif
coastal_threshold = 50       # distancia en píxeles para considerar "cerca de la costa"
step_coast = 3              # densidad cerca de tierra
step_open = 100             # densidad mar adentro
resize_factor = 1.0          # 1.0 = no reducir, podés bajarlo si el tif es enorme

# === 2. Buscar todos los archivos .tif ===
tif_files = list(data_dir.glob("*.tif"))
print(f"Se encontraron {len(tif_files)} archivos TIFF en {data_dir}")

for tif_path in tif_files:
    print(f"\nProcesando: {tif_path.name}")

    # === 3. Leer el archivo GEBCO ===
    with rasterio.open(tif_path) as src:
        elev = src.read(1)  # matriz de elevaciones
        transform = src.transform  # para convertir (fila, col) → (lat, lon)

    print("Dimensiones:", elev.shape)

    # Opcional: reducir resolución para acelerar procesamiento
    if resize_factor < 1.0:
        elev = resize(elev, 
                      (int(elev.shape[0]*resize_factor), int(elev.shape[1]*resize_factor)), 
                      anti_aliasing=True)

    # === 4. Crear máscara del océano ===
    ocean_mask = elev < 0
    if not np.any(ocean_mask):
        print("⚠️ No hay océano en este archivo. Saltando...")
        continue

    # === 5. Calcular distancia a tierra ===
    dist_to_land = distance_transform_edt(ocean_mask == 1)

    # === 6. Muestreo adaptativo ===
    points = []
    rows, cols = elev.shape

    for i in range(0, rows, 5):  # barrido a saltos pequeños
        for j in range(0, cols, 5):
            if ocean_mask[i, j]:
                d = dist_to_land[i, j]
                # cerca de costa → más denso
                if d < coastal_threshold:
                    if (i % step_coast == 0) and (j % step_coast == 0):
                        points.append((i, j, elev[i, j]))
                # mar abierto → menos denso
                else:
                    if (i % step_open == 0) and (j % step_open == 0):
                        points.append((i, j, elev[i, j]))

    points = np.array(points)
    print(f"→ {len(points)} nodos generados")

    if len(points) == 0:
        print("⚠️ Sin nodos detectados. Saltando este archivo.")
        continue

    # === 7. Convertir a coordenadas geográficas ===
    lats, lons, depths = [], [], []
    for i, j, depth in points:
        lon, lat = rasterio.transform.xy(transform, i, j)
        lats.append(lat)
        lons.append(lon)
        depths.append(depth)

    # === 8. Crear DataFrame y guardar CSV ===
    df = pd.DataFrame({
        "latitud": lats,
        "longitud": lons,
        "profundidad": depths
    })

    csv_path = data_dir / f"{tif_path.stem}.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ CSV exportado: {csv_path.name}")

print("\n🎉 Conversión completa para todos los archivos .tif")
