# Build fpfa-setup-<version>.exe with Inno Setup 6.
# Run from any directory on Windows.
#
#   packaging\build_installer.ps1
#   packaging\build_installer.ps1 -BuildApp
#   packaging\build_installer.ps1 -Version 0.1.0
#
# Uses app\dist\fpfa\fpfa.exe when that file is already there. If it is
# missing, or if -BuildApp is set, runs build_app.ps1 first.
# ISCC.exe is taken from %LOCALAPPDATA%\Programs\Inno Setup 6, then
# Program Files. Prints the setup exe path. Upload that file to a GitHub Release.

param(
    [switch]$BuildApp,
    [string]$Version = ""
)

$ErrorActionPreference = "Stop"
$Packaging = $PSScriptRoot
$App = Split-Path -Parent $Packaging
$DistDir = Join-Path $App "dist"
$Exe = Join-Path $DistDir "fpfa\fpfa.exe"
$Iss = Join-Path $Packaging "installer.iss"

if ($BuildApp -or -not (Test-Path -LiteralPath $Exe)) {
    if (-not (Test-Path -LiteralPath $Exe)) {
        Write-Host "fpfa.exe is not in $DistDir\fpfa. Running build_app.ps1."
    }
    & (Join-Path $Packaging "build_app.ps1")
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

if (-not (Test-Path -LiteralPath $Exe)) {
    Write-Host "Missing $Exe"
    exit 1
}

if (-not $Version) {
    $init = Join-Path $App "fpfa\__init__.py"
    $found = Select-String -LiteralPath $init -Pattern '__version__\s*=\s*"([^"]+)"' | Select-Object -First 1
    if (-not $found) {
        Write-Host "Could not read __version__ from $init. Pass -Version."
        exit 1
    }
    $Version = $found.Matches[0].Groups[1].Value
}

if ($Version -notmatch '^\d+\.\d+\.\d+$') {
    Write-Host "Version must look like 0.1.0. Got: $Version"
    exit 1
}

$candidates = New-Object System.Collections.Generic.List[string]
if ($env:LOCALAPPDATA) {
    $candidates.Add((Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe"))
}
if ($env:ProgramFiles) {
    $candidates.Add((Join-Path $env:ProgramFiles "Inno Setup 6\ISCC.exe"))
}
if (${env:ProgramFiles(x86)}) {
    $candidates.Add((Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe"))
}

$Iscc = $null
foreach ($candidate in $candidates) {
    if (Test-Path -LiteralPath $candidate) {
        $Iscc = $candidate
        break
    }
}
if (-not $Iscc) {
    $cmd = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    if ($cmd) { $Iscc = $cmd.Source }
}
if (-not $Iscc) {
    Write-Host "ISCC.exe was not found. Install Inno Setup 6."
    Write-Host "Looked in:"
    foreach ($candidate in $candidates) { Write-Host "  $candidate" }
    exit 1
}

$OutName = "fpfa-setup-$Version"
& $Iscc "/DMyAppVersion=$Version" "/O$DistDir" "/F$OutName" $Iss
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$Setup = Join-Path $DistDir "$OutName.exe"
if (-not (Test-Path -LiteralPath $Setup)) {
    Write-Host "ISCC finished but $Setup is missing."
    exit 1
}
Write-Host "Built $Setup"
