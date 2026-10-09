# Fresh Commvault Assistant

A Windows desktop helper that launches the organization's Commvault installer and automates the observed client installation steps. The technician accepts the license and enters credentials; CommServe connectivity is required to complete registration.

## Requirements

- Windows 10/11, 64-bit
- Python 3.15 for the current development setup
- `pywinauto` and `pyinstaller` from `requirements.txt`
- Commvault installation media supplied by the organization
- Company network or VPN for CommServe registration

## Local CommServe configuration

Copy `config.example.py` to `config.py` and set `COMM_SERVE` to the CommServe hostname provided by your organization. `config.py` is ignored by Git so environment-specific server names are not committed.

## Installer media

The licensed Commvault media is intentionally not tracked in this repository. Obtain it through the organization's approved software distribution channel and place its complete `WinX64` directory beside `main.py`. The directory must include `LaunchInstaller.exe` and the remaining vendor files.

## Run from source

```powershell
py -m pip install -r requirements.txt
py main.py
```

The assistant requests administrator approval when needed. The technician must accept the license agreement and enter credentials. The installer automation uses the CommServe configured in `config.py`.

## Build a portable Windows folder

With the organization-provided `WinX64` folder present, run `build_portable.ps1` from PowerShell. The output is written to `release\Fresh Commvault Assistant` and contains the executable plus the complete installer media. Distribute it only through organization-approved channels and only to devices authorized to use the Commvault license.

## Tests

```powershell
py -m unittest test_console_app
```