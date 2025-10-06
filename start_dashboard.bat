@echo off
REM Lanza el sistema en modo Dashboard (panel de análisis).

echo Iniciando el Sistema POS en modo Dashboard...
echo.

REM Llama directamente al Python del entorno virtual para ejecutar el script
CALL .\venv\Scripts\python.exe start_pos.py dashboard

pause
