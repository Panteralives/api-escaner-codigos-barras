@echo off
REM ================================================================
REM Script de inicio automático para producción - Inventario Barras
REM ================================================================

REM Configurar ventana
title Inventario Barras - Modo Producción
color 0A

REM Mensaje de inicio
echo.
echo =====================================
echo   SISTEMA DE INVENTARIO - PRODUCCIÓN
echo =====================================
echo.
echo [%time%] Iniciando sistema...

REM Cambiar al directorio del proyecto
cd /d "C:\InventarioBarras\"
if errorlevel 1 (
    echo ERROR: No se pudo acceder al directorio del proyecto
    pause
    exit /b 1
)

REM Verificar que Python existe
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en PATH
    pause
    exit /b 1
)

REM Verificar dependencias
echo [%time%] Verificando sistema...
python run.py --check-hardware

REM Iniciar API en modo producción
echo.
echo [%time%] Iniciando API de inventario...
start "API-Inventario" /MIN cmd /c "python run.py 2>&1 | tee api.log"

REM Esperar a que la API inicie
echo [%time%] Esperando a que la API inicie...
timeout /t 15 /nobreak >nul

REM Verificar que la API está funcionando
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo WARNING: API no responde, intentando continuar...
    timeout /t 5 /nobreak >nul
)

REM Iniciar frontend en modo pantalla completa
echo [%time%] Iniciando frontend web...
start "Frontend-Inventario" cmd /c "python run.py --frontend"

REM Esperar un poco y abrir navegador automáticamente
timeout /t 10 /nobreak >nul
echo [%time%] Abriendo interfaz web...
start http://localhost:8501

echo.
echo =====================================
echo   SISTEMA INICIADO CORRECTAMENTE
echo =====================================
echo.
echo API:      http://localhost:8000
echo Frontend: http://localhost:8501
echo Documentación: http://localhost:8000/docs
echo.
echo Presiona cualquier tecla para cerrar esta ventana...
pause >nul
