# Cómo añadir una librería al proyecto (guía rápida)

Este archivo es temporal: puedes borrarlo antes de entregar el proyecto. Está pensado para que tus compañeros entiendan, paso a paso, cómo agregar una dependencia al repositorio y dejarlo reproducible.

1) Decidir el gestor que usamos

- Si usamos Conda/Mamba para el entorno: actualizar `environment.yml`.
- Si usamos `venv`/pip o Docker: actualizar `requirements.txt`.
- Si la librería es sólo para desarrollo (tests/linter): actualizar `requirements-dev.txt`.

2) Instalar localmente en tu entorno (PowerShell)

- Si usas Conda/Mamba:
  ```powershell
  conda activate hackaton
  conda install nombre-paquete
  # o, si el paquete sólo está en pip:
  pip install nombre-paquete
  ```

- Si usas venv (fallback):
  ```powershell
  .\.venv\Scripts\Activate.ps1
  pip install nombre-paquete==versión
  ```

Ejemplo (instalar FastAPI):
```powershell
pip install fastapi==0.100.0
```

3) Congelar o anotar la dependencia en los archivos del repo

- Opción automática (congelar todas las dependencias actuales):
  ```powershell
  pip freeze > requirements.txt
  ```
  Esto sobrescribirá `requirements.txt` con todas las dependencias instaladas en tu entorno.

- Opción manual (recomendada para control más fino):
  - Abre `requirements.txt` y añade una línea con la dependencia y versión exacta, por ejemplo:
    ```text
    fastapi==0.100.0
    ```
  - Si usas Conda y quieres que `environment.yml` refleje la nueva librería, edita `environment.yml` y agrega la dependencia en la sección `dependencies:` o dentro de `- pip:` si es paquete pip-only.

4) Probar que la aplicación arranca y que no hay errores

```powershell
python -m src.main
# o correr tests si existen:
pytest -q
```

5) Actualizar Docker (si aplica)

- Si el `Dockerfile` instala desde `requirements.txt`, reconstruye la imagen para incluir la nueva dependencia:
```powershell
docker build -t hackaton:latest .
```

6) Commit y push de los cambios

Haz commit sólo de los archivos que corresponden a la dependencia (no subas `.env` ni entornos locales):

```powershell
git add requirements.txt environment.yml
git commit -m "Add <paquete> dependency"
git push -u origin <tu-rama>
```

7) Buenas prácticas

- Pinea versiones exactas (`==`) para reproducibilidad en entregas.
- Separar dependencias de runtime y de desarrollo (`requirements.txt` vs `requirements-dev.txt`).
- No subas `.venv/` ni `.env` al repo; usa `.env.example` para compartir variables no secretas.
- Si quieres control avanzado de dependencias, considera `pip-tools` (`pip-compile`) o `poetry`.

8) Cómo revertir (si algo sale mal)

- Desinstalar localmente:
  ```powershell
  pip uninstall nombre-paquete
  ```
- Quitar la línea correspondiente de `requirements.txt` o `environment.yml`, volver a commit.

9) Nota final

Este archivo es una guía rápida para el equipo. Recuerda borrarlo antes de la entrega si no quieres dejar documentación temporal en el repo.
