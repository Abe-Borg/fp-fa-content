# Build a Windows folder with Cynosure.exe, a seed content pack, LICENSE.txt, and THIRD-PARTY-NOTICES.txt.
# Run from any directory. Requires Python 3.11+ on PATH as py.
# Next: packaging\build_installer.ps1, then upload dist\Cynosure-Setup-<version>.exe to a GitHub Release.
$ErrorActionPreference = "Stop"
$App = Split-Path -Parent $PSScriptRoot
Set-Location $App
py -3 -m pip install -r requirements.txt pyinstaller
py -3 packaging\build_app.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "Built $App\dist\Cynosure\Cynosure.exe"
