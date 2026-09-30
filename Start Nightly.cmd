@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\pythonw.exe" (
    echo.
    echo Nightly's virtual environment was not found.
    echo Run the setup steps in README.md once, then try again.
    echo.
    pause
    exit /b 1
)

set "NIGHTLY_PYTHON=%~dp0.venv\Scripts\pythonw.exe"
powershell.exe -NoProfile -Command "$running = @(Get-CimInstance Win32_Process -Filter \"Name = 'pythonw.exe'\"); foreach ($process in $running) { if ($process.ExecutablePath -eq $env:NIGHTLY_PYTHON -and $process.CommandLine -match 'bot\.py') { exit 10 } }"
if errorlevel 10 exit /b 0

start "" /b ".venv\Scripts\pythonw.exe" "bot.py"
exit /b
