@echo off
REM Lanza el sistema en modo Invisible (solo servicios de fondo).

echo Iniciando el Sistema POS en modo Invisible...
echo Este modo no abrira ninguna ventana de navegador.

REM Llama directamente al Python del entorno virtual para ejecutar el script
CALL .\venv\Scripts\python.exe start_pos.py invisible

pause