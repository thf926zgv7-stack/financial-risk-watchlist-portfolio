param(
    [string]$PythonPath = "python"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "[1/3] Downloading real public SEC filing data..."
& $PythonPath (Join-Path $projectRoot "src\fetch_sec_real_data.py")

Write-Host "[2/3] Calculating transparent financial-health watch scores..."
& $PythonPath (Join-Path $projectRoot "src\analyze_real_sec_data.py")

Write-Host "[3/3] Creating the real-data dashboard..."
& $PythonPath (Join-Path $projectRoot "src\visualize_real_sec_data.py")

Write-Host "Done. Open outputs\real_sec\real_data_summary.md and real_sec_dashboard.html."
