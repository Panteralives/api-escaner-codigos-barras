@echo off
REM ================================================================
REM LANZADOR POS COMPLETAMENTE INVISIBLE
REM ================================================================

REM Ejecutar script PowerShell en modo completamente oculto
powershell -WindowStyle Hidden -ExecutionPolicy Bypass -File "lanzar_pos_invisible.ps1"

REM Esta ventana batch se cierra inmediatamente
exit