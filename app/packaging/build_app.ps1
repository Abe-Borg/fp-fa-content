# Build a Windows folder with fpfa.exe and a seed content pack.
# Run from any directory. Requires Python 3.11+ on PATH as py.
# Next: packaging\build_installer.ps1, then upload dist\fpfa-setup-<version>.exe to a GitHub Release.
$ErrorActionPreference = "Stop"
$App = Split-Path -Parent $PSScriptRoot
Set-Location $App
py -3 -m pip install -r requirements.txt pyinstaller
py -3 packaging\build_app.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "Built $App\dist\fpfa\fpfa.exe"
