# Hackaton – Setup rápido

## Opción A: Conda/Mamba (recomendada)
1. `mamba env create -f environment.yml` **o** `conda env create -f environment.yml`
2. `conda activate hackaton`
3. `python -m src.main`

**Alternativa automática**
- macOS/Linux: `bash install.sh`
- Windows: `powershell -ExecutionPolicy Bypass -File install.ps1`

## Opción B: venv + pip/uv (sin Conda)
```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows:
.\.venv\Scripts\Activate.ps1

# Instalar (usa uv si está disponible, sino pip)
uv pip sync requirements.txt  # recomendado
# o:
pip install -r requirements.txt

python -m src.main
```