@echo off
REM Script para rodar API localmente (Windows)

echo 🚀 Iniciando API Resíduos SC...
echo.

REM Verificar se está no ambiente virtual
if not defined VIRTUAL_ENV (
    echo ⚠️  Ambiente virtual não ativado!
    echo    Execute: .venv\Scripts\activate
    echo.
    pause
    exit /b 1
)

REM Verificar se dependências estão instaladas
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo 📦 Instalando dependências...
    pip install -r requirements-api.txt
    echo.
)

REM Rodar API
echo ✅ Iniciando servidor...
echo 📍 Swagger UI: http://localhost:8000/docs
echo 📍 ReDoc: http://localhost:8000/redoc
echo 📍 Health: http://localhost:8000/health
echo.
echo Pressione Ctrl+C para parar o servidor
echo.

uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
