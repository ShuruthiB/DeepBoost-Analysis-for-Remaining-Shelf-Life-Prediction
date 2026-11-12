@echo off
REM Run from the PROJECT ROOT (the folder that contains backend, frontend and launcher.py):
REM     packaging\build_windows.bat
if not exist backend\main.py (
  echo ERROR: run this from the project root, not from the packaging folder or the kit folder.
  exit /b 1
)
if not exist frontend\package.json (
  echo ERROR: frontend folder not found - are you in the full project?
  exit /b 1
)

REM Use "python -m ..." everywhere: some managed PCs block pip.exe / pyinstaller.exe launchers.
python -m venv .venv-build || exit /b 1
set PY=.venv-build\Scripts\python.exe
%PY% -m pip install -r packaging\requirements-exe.txt || exit /b 1

cd frontend
call npm ci || exit /b 1
set VITE_API_BASE_URL=/api
call npm run build || exit /b 1
cd ..

%PY% -m PyInstaller packaging\spoilsense.spec --noconfirm || exit /b 1
echo.
echo Done: dist\SpoilSenseAI\SpoilSenseAI.exe
echo Zip the whole dist\SpoilSenseAI folder and upload the zip.
