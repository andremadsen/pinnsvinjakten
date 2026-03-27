@echo off
REM ============================================================
REM  aktiver_miljø.bat
REM  Starter Pinnsvin-spillet!
REM  Åpner appen i nettleser.
REM ============================================================

REM --- Naviger til mappen der batch-filen ligger (root)
cd /d "%~dp0"

echo.
echo  ===================================================
echo   Pinnsvin-spillet til Håvard!
echo  ===================================================
echo.

REM --- Opprett virtuelt miljø dersom det ikke finnes ---
IF NOT EXIST "%cd%\.venv\" (
    CALL py -3.13 -m venv .venv
)
IF %errorlevel% NEQ 0 EXIT /B
) else (
    echo [2/4] Virtuelt miljø (.venv) finnes allerede.
)

REM --- Aktiver virtuelt miljø ---
call .venv\Scripts\activate.bat

REM --- Installer / oppdater avhengigheter ---
echo [3/4] Installerer avhengigheter fra requirements.txt ...
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
if %errorlevel% neq 0 (
    echo [FEIL] pip install feilet for kjerneavhengigheter. Sjekk internett-tilgang.
    pause
    exit /b 1
)

echo [4/4] Starter AMLvibe ...
echo.
echo  Appen åpnes i nettleseren på http://localhost:8501
echo  Trykk CTRL+C i dette vinduet for å stoppe serveren.
echo.

REM --- Åpne nettleser etter 3 sekunder (i bakgrunnen) ---
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:8501"

REM --- Start Streamlit ---
python -m streamlit run app.py --server.headless true --server.port 8501 --server.address 0.0.0.0

pause
