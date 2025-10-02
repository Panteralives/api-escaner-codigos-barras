@echo off
REM ============================================================
REM SISTEMA POS - SCRIPT DE INICIO BATCH (RESPALDO)
REM ============================================================
REM
REM Este archivo sirve como respaldo para iniciar el sistema
REM si el método del registro de Windows no funciona.
REM
REM Uso: Hacer doble clic o colocar en carpeta de Inicio
REM ============================================================

echo.
echo ============================================================
echo INICIANDO SISTEMA POS - INVENTARIO BARRAS
echo ============================================================
echo.

REM Cambiar al directorio del proyecto
cd /d "C:\InventarioBarras"

REM Verificar que el directorio existe
if not exist "C:\InventarioBarras\start_basic.py" (
    echo ERROR: No se encontro el archivo start_basic.py
    echo Verifica que el proyecto este en C:\InventarioBarras\
    pause
    exit /b 1
)

echo Directorio del proyecto: %CD%
echo Iniciando con Python...
echo.

REM Intentar iniciar con Python
python start_basic.py

REM Si hay error, mostrar mensaje y esperar
if errorlevel 1 (
    echo.
    echo ============================================================
    echo ERROR: El sistema no pudo iniciarse correctamente
    echo ============================================================
    echo.
    echo Posibles soluciones:
    echo 1. Verifica que Python este instalado y en PATH
    echo 2. Ejecuta: python start_basic.py --diagnostic
    echo 3. Revisa los logs en start_basic.log
    echo.
    pause
)