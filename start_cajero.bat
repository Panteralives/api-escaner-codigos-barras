@echo off
REM Lanza el sistema en modo Cajero (interfaz de punto de venta).

echo Iniciando el Sistema POS en modo Cajero...
echo.

REM Llama directamente al Python del entorno virtual para ejecutar el script
CALL .\venv\Scripts\python.exe start_pos.py cajero

pause