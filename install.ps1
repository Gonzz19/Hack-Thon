Param()
try {
    if (Get-Command mamba -ErrorAction SilentlyContinue) {
        mamba env create -f environment.yml
    } elseif (Get-Command conda -ErrorAction SilentlyContinue) {
        conda env create -f environment.yml
    } else {
        python -m venv .venv
        .\.venv\Scripts\Activate.ps1
        pip install -r requirements.txt
    }
    Write-Host "Environment ready. Activate with: conda activate hackaton or .\\.venv\\Scripts\\Activate.ps1"
} catch {
    Write-Error "Failed to create environment: $_"
    exit 1
}
