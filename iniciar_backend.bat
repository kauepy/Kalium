@echo off
chcp 65001 >nul
title Kalium Backend

echo ============================================================
echo                    KALIUM BACKEND
echo ============================================================
echo.

cd /d "%~dp0"

REM --- Verifica Python ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Instale Python 3.10+ de https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
echo [OK] Python:
python --version
echo.

REM --- Verifica main.py ---
if not exist "main.py" (
    echo [ERRO] main.py nao encontrado.
    pause
    exit /b 1
)

REM --- Cria/ativa venv ---
if not exist "venv\Scripts\python.exe" (
    echo [INFO] Criando ambiente virtual...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo [OK] venv ativado
echo.

REM --- Instala deps ---
echo [INFO] Verificando dependencias...
python -c "import fastapi, uvicorn, pydantic" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalando dependencias...
    python -m pip install --upgrade pip
    python -m pip install fastapi uvicorn pydantic
    if errorlevel 1 (
        echo [ERRO] Falha ao instalar dependencias.
        pause
        exit /b 1
    )
    echo [OK] Dependencias instaladas.
) else (
    echo [OK] Dependencias ja instaladas.
)
echo.

REM --- Menu de opcoes ---
echo O que voce quer fazer?
echo.
echo   1 - Iniciar servidor (indexacao automatica na primeira vez)
echo   2 - Re-indexar HTMLs e iniciar servidor
echo   3 - Apenas re-indexar (sem iniciar servidor)
echo   4 - Limpar banco e re-indexar do zero
echo.
set /p opcao="Escolha (1/2/3/4): "

if "%opcao%"=="2" (
    echo.
    echo [INFO] Re-indexando HTMLs...
    python indexar_html.py
    echo.
) else if "%opcao%"=="3" (
    echo.
    echo [INFO] Re-indexando HTMLs...
    python indexar_html.py
    echo.
    echo Concluido.
    pause
    exit /b 0
) else if "%opcao%"=="4" (
    echo.
    echo [INFO] Limpando banco e re-indexando do zero...
    python indexar_html.py --limpar
    echo.
    pause
    exit /b 0
)

REM --- Sobe o servidor ---
echo ============================================================
echo  Servidor em http://localhost:8000
echo  Health:  http://localhost:8000/health
echo  Docs:    http://localhost:8000/docs
echo  Reindex: POST http://localhost:8000/api/v1/admin/reindexar
echo ============================================================
echo  Ctrl+C para parar.
echo ============================================================
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 8000

echo.
echo Servidor parou.
pause