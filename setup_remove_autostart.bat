@echo off
REM ================================================================
REM 🔧 REMOVER INICIO AUTOMÁTICO - SISTEMA POS
REM ================================================================

title Remover Inicio Automático - Sistema POS
color 0C

echo.
echo ================================================================
echo           REMOVER INICIO AUTOMÁTICO - SISTEMA POS
echo ================================================================
echo.

echo [%time%] Removiendo configuración de inicio automático...
echo.

REM Remover entrada del registro
echo 📋 Removiendo entrada del registro de Windows...
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "SistemaPOSAvanzado" /f 2>nul

if errorlevel 1 (
    echo ⚠️  No se encontró entrada en el registro (posiblemente ya removida)
) else (
    echo ✅ Entrada de registro removida exitosamente
)

REM Preguntar sobre el acceso directo del escritorio
echo.
set /p RESPUESTA=¿Remover también el acceso directo del escritorio? (s/N): 

if /i "%RESPUESTA%"=="s" (
    if exist "%USERPROFILE%\Desktop\Sistema POS Avanzado.lnk" (
        del "%USERPROFILE%\Desktop\Sistema POS Avanzado.lnk"
        echo ✅ Acceso directo del escritorio removido
    ) else (
        echo ⚠️  Acceso directo no encontrado
    )
) else (
    echo ℹ️  Acceso directo del escritorio mantenido
)

echo.
echo ================================================================
echo         INICIO AUTOMÁTICO DESACTIVADO EXITOSAMENTE
echo ================================================================
echo.
echo ✅ El Sistema POS ya NO se iniciará automáticamente
echo.
echo ℹ️  El acceso directo manual sigue disponible (si no fue removido)
echo.
echo ================================================================

echo.
pause