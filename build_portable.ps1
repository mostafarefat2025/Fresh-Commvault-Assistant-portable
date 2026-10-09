$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

py -3.15 -m PyInstaller `
    --noconfirm `
    --onedir `
    --windowed `
    --uac-admin `
    --name "Fresh Commvault Assistant" `
    --workpath "build_portable_v2" `
    --distpath "release" `
    --collect-all pywinauto `
    --collect-all comtypes `
    main.py

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed with exit code $LASTEXITCODE."
}

Copy-Item -Path (Join-Path $PSScriptRoot "WinX64") `
    -Destination (Join-Path $PSScriptRoot "release\Fresh Commvault Assistant\WinX64") `
    -Recurse -Force

$pythonDirectory = Split-Path (py -3.15 -c "import sys; print(sys.executable)") -Parent
Copy-Item -Path (Join-Path $pythonDirectory "python3.dll") `
    -Destination (Join-Path $PSScriptRoot "release\Fresh Commvault Assistant\_internal\python3.dll") `
    -Force

Write-Host "Portable build created at: $PSScriptRoot\release\Fresh Commvault Assistant"