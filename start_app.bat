@echo off
echo ===================================================
echo 🚀 Job Crawler - Démarrage sécurisé
echo ===================================================

echo.
echo [1/4] Activation de l'environnement virtuel...
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate
) else (
    echo ❌ Erreur: .venv non trouvé. Veuillez créer l'environnement virtuel.
    pause
    exit /b
)

echo.
echo [2/4] Vérification des dépendances...
pip install -r requirements.txt > nul
if %errorlevel% neq 0 (
    echo ❌ Erreur lors de l'installation des dépendances.
    pause
    exit /b
)

echo.
echo [3/4] Vérification de Playwright...
python -c "import playwright.sync_api" 2>nul
if %errorlevel% neq 0 (
    echo    Installation de Playwright...
    pip install playwright
    playwright install chromium
)

echo.
echo [4/4] Lancement de l'application...
echo.
streamlit run app.py

pause
