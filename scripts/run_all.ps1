param([string]$Python = 'python')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$previousDirectory = Get-Location
$oldLicense = $env:GRB_LICENSE_FILE
$temporaryLicense = $null
$oldUtf8 = $env:PYTHONUTF8
try {
    Set-Location -LiteralPath $projectRoot
    $env:PYTHONUTF8 = '1'
    # IBM/Gurobi native Windows libraries may not read Unicode license paths.
    # Stage only the restricted license shipped by gurobipy, never a user key.
    if (-not $env:GRB_LICENSE_FILE) {
        $packagedLicense = & $Python -c 'import pathlib,gurobipy;print(pathlib.Path(gurobipy.__file__).parent/"gurobi.lic")'
        if ($LASTEXITCODE -ne 0) { throw 'Khong nap duoc gurobipy. Cai requirements.txt truoc.' }
        if (Test-Path -LiteralPath $packagedLicense) {
            $temporaryLicense = Join-Path ([IO.Path]::GetTempPath()) "nqueens-packaged-gurobi-$PID.lic"
            if ($temporaryLicense -match '[^\x00-\x7F]') { throw 'Can dat TEMP den thu muc ASCII truoc khi chay Gurobi.' }
            Copy-Item -LiteralPath $packagedLicense -Destination $temporaryLicense
            $env:GRB_LICENSE_FILE = $temporaryLicense
        }
    }
    & $Python -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw 'Kiem thu khong dat.' }
    & $Python scripts/benchmark.py --suite main --limit 30
    if ($LASTEXITCODE -ne 0) { throw 'Loi tap chinh.' }
    & $Python scripts/benchmark.py --suite large --limit 30
    if ($LASTEXITCODE -ne 0) { throw 'Loi tap mo rong.' }
    & $Python scripts/analyze.py
    if ($LASTEXITCODE -ne 0) { throw 'Loi tong hop.' }
    & $Python scripts/build_report.py
    if ($LASTEXITCODE -ne 0) { throw 'Loi cap nhat bao cao.' }
} finally {
    if ($temporaryLicense -and (Test-Path -LiteralPath $temporaryLicense)) {
        Remove-Item -LiteralPath $temporaryLicense
    }
    $env:GRB_LICENSE_FILE = $oldLicense
    $env:PYTHONUTF8 = $oldUtf8
    Set-Location -LiteralPath $previousDirectory
}
