@echo off
REM ================================================================
REM 🚀 CONFIGURAR INICIO AUTOMÁTICO - SISTEMA POS SIMPLE
REM ================================================================

title Configurar Inicio Automático - Sistema POS
color 0B

echo.
echo ================================================================
echo           CONFIGURAR INICIO AUTOMÁTICO - SISTEMA POS
echo ================================================================
echo.

REM Verificar que estemos en el directorio correcto
cd /d "C:\InventarioBarras"

if not exist "autostart_pos.bat" (
    echo ❌ Error: Script autostart_pos.bat no encontrado
    echo 📁 Asegúrate de estar en el directorio correcto
    pause
    exit /b 1
)

echo [%time%] Configurando inicio automático...
echo.

REM Configurar entrada en el registro de Windows
echo 📋 Agregando entrada al registro de Windows...
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "SistemaPOSAvanzado" /t REG_SZ /d "\"C:\InventarioBarras\autostart_pos.bat\" auto" /f

if errorlevel 1 (
    echo ❌ Error configurando registro
    pause
    exit /b 1
)

echo ✅ Entrada de registro creada exitosamente

REM Crear acceso directo en el escritorio
echo 📋 Creando acceso directo en el escritorio...

powershell -command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Sistema POS Avanzado.lnk'); $Shortcut.TargetPath = 'C:\InventarioBarras\autostart_pos.bat'; $Shortcut.WorkingDirectory = 'C:\InventarioBarras'; $Shortcut.Description = 'Sistema POS Avanzado - Control Manual'; $Shortcut.Save()}"

echo ✅ Acceso directo creado en el escritorio

echo.
echo ================================================================
echo           CONFIGURACIÓN COMPLETADA EXITOSAMENTE
echo ================================================================
echo.
echo ✅ El Sistema POS se iniciará automáticamente cuando Windows arranque
echo.
echo 📋 CARACTERÍSTICAS:
echo    • Backend API se inicia automáticamente
echo    • Frontend web se abre automáticamente  
echo    • Interfaz lista para trabajar en el navegador
echo    • Ejecución minimizada en segundo plano
echo.
echo 🎯 CONTROL MANUAL:
echo    • Acceso directo: 'Sistema POS Avanzado' en escritorio
echo    • Para detener: Ctrl+C en ventana de comandos
echo.
echo 🔧 PARA DESACTIVAR:
echo    • Ejecuta: setup_remove_autostart.bat
echo    • O usar msconfig (Win + R, escribir msconfig)
echo.
echo ================================================================

set /p RESPUESTA=¿Deseas probar el sistema ahora? (S/n): 

if /i "%RESPUESTA%"=="n" goto :end
if /i "%RESPUESTA%"=="N" goto :end

echo.
echo [%time%] Iniciando sistema de prueba...
start "" "autostart_pos.bat"

:end
echo.
echo 👋 Configuración completada
pause