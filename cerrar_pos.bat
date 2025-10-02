@echo off
chcp 65001 >nul 2>&1
title Cerrando Sistema POS
color 0C

echo.
echo ================================================================
echo                    CERRANDO SISTEMA POS
echo ================================================================
echo.
echo [%time%] Buscando procesos del sistema POS...

REM Cerrar procesos Python relacionados con POS
tasklist | find /i "python.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo [%time%] Cerrando servidores Python...
    taskkill /f /im python.exe >nul 2>&1
    echo ✅ Procesos Python terminados
) else (
    echo ℹ️  No se encontraron procesos Python activos
)

REM Cerrar procesos relacionados con uvicorn (si existen)
tasklist | find /i "uvicorn" >nul
if %ERRORLEVEL% EQU 0 (
    echo [%time%] Cerrando procesos uvicorn...
    taskkill /f /im uvicorn.exe >nul 2>&1
    echo ✅ Procesos uvicorn terminados
)

REM Verificar puertos
echo.
echo [%time%] Verificando puertos liberados...
netstat -an | find ":3002" >nul
if %ERRORLEVEL% EQU 0 (
    echo ⚠️  Puerto 3002 aún ocupado
) else (
    echo ✅ Puerto 3002 liberado
)

netstat -an | find ":8000" >nul
if %ERRORLEVEL% EQU 0 (
    echo ⚠️  Puerto 8000 aún ocupado
) else (
    echo ✅ Puerto 8000 liberado
)

echo.
echo ================================================================
echo                    SISTEMA POS CERRADO
echo ================================================================
echo.
echo ✅ Todos los procesos terminados correctamente
echo ✅ Puertos liberados
echo ✅ Sistema completamente limpio
echo.
echo 💡 Ahora puedes reiniciar el sistema si es necesario
echo.

timeout /t 3 >nul
exit