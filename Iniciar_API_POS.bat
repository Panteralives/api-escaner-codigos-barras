@echo off
REM ================================================
REM 🚀 SISTEMA POS AVANZADO - INICIADOR API
REM Acceso directo para Windows
REM ================================================

title Sistema POS Avanzado - API
color 0A

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    🚀 SISTEMA POS AVANZADO                  ║
echo ║                  Iniciando desde acceso directo...          ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Cambiar al directorio del proyecto
cd /d "C:\InventarioBarras"

REM Verificar que estemos en el directorio correcto
if not exist "iniciar_api_completa.py" (
    echo ❌ Error: No se encontró el script de inicio
    echo 📁 Directorio actual: %CD%
    echo 💡 Asegúrate de que el archivo esté en: C:\InventarioBarras\
    pause
    exit /b 1
)

REM Ejecutar el script de Python
echo 🐍 Ejecutando script de inicio...
python iniciar_api_completa.py

REM Si el script falla, mostrar información de debug
if errorlevel 1 (
    echo.
    echo ❌ Error ejecutando el script
    echo 💡 Posibles soluciones:
    echo    1. Verificar que Python esté instalado: python --version
    echo    2. Instalar dependencias: pip install fastapi uvicorn
    echo    3. Ejecutar manualmente: python iniciar_api_completa.py
    echo.
    pause
)

echo.
echo 👋 Script terminado
pause