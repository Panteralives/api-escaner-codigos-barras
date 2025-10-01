@echo off
REM ================================================================
REM 🚀 INSTALADOR DE INICIO AUTOMÁTICO - SISTEMA POS AVANZADO
REM ================================================================
REM Script para configurar inicio automático optimizado
REM ================================================================

title Instalador Inicio Automático - Sistema POS

echo.
echo ================================================================
echo    INSTALADOR DE INICIO AUTOMÁTICO - SISTEMA POS AVANZADO
echo ================================================================
echo.

REM Cambiar al directorio del proyecto
cd /d "C:\InventarioBarras"

REM Verificar que estemos en el directorio correcto
if not exist "autostart_pos_system.py" (
    echo ERROR: Script de autostart no encontrado
    echo Directorio actual: %CD%
    echo.
    echo Verifica que el proyecto esté en C:\InventarioBarras
    pause
    exit /b 1
)

echo [INFO] Directorio del proyecto: %CD%
echo [INFO] Script encontrado: autostart_pos_system.py
echo.

REM Preguntar qué método usar
echo Selecciona el método de inicio automático:
echo.
echo 1. Carpeta de Inicio (Recomendado - más simple)
echo 2. Registro de Windows (Avanzado - más control)
echo 3. Ambos métodos (Máxima compatibilidad)
echo.
set /p METODO=Selecciona una opción (1/2/3): 

if "%METODO%"=="1" goto :install_startup
if "%METODO%"=="2" goto :install_registry
if "%METODO%"=="3" goto :install_both
echo.
echo ERROR: Opción inválida
pause
exit /b 1

:install_startup
echo.
echo [INFO] Instalando en carpeta de Inicio...
call :create_startup_shortcut
echo [OK] Configuración completada - Método: Carpeta de Inicio
goto :test_installation

:install_registry
echo.
echo [INFO] Instalando en Registro de Windows...
call :create_registry_entry
echo [OK] Configuración completada - Método: Registro
goto :test_installation

:install_both
echo.
echo [INFO] Instalando ambos métodos...
call :create_startup_shortcut
call :create_registry_entry
echo [OK] Configuración completada - Método: Ambos
goto :test_installation

:create_startup_shortcut
REM Crear acceso directo en carpeta de inicio
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set SHORTCUT_PATH=%STARTUP_FOLDER%\Sistema POS Avanzado.lnk

echo [INFO] Creando acceso directo en: %STARTUP_FOLDER%

REM Crear archivo VBS para generar el acceso directo
echo Set oWS = WScript.CreateObject("WScript.Shell") > create_shortcut.vbs
echo sLinkFile = "%SHORTCUT_PATH%" >> create_shortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> create_shortcut.vbs
echo oLink.TargetPath = "python" >> create_shortcut.vbs
echo oLink.Arguments = "autostart_pos_system.py" >> create_shortcut.vbs
echo oLink.WorkingDirectory = "%CD%" >> create_shortcut.vbs
echo oLink.Description = "Sistema POS Avanzado - Inicio Automático" >> create_shortcut.vbs
echo oLink.Save >> create_shortcut.vbs

REM Ejecutar el script VBS
cscript //nologo create_shortcut.vbs
del create_shortcut.vbs

if exist "%SHORTCUT_PATH%" (
    echo [OK] Acceso directo creado exitosamente
) else (
    echo [ERROR] No se pudo crear el acceso directo
)
goto :eof

:create_registry_entry
REM Agregar entrada al registro
set KEY_PATH=HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
set VALUE_NAME=SistemaPOSAvanzado
set COMMAND=python "%CD%\autostart_pos_system.py"

echo [INFO] Agregando entrada al registro...
echo [INFO] Clave: %KEY_PATH%
echo [INFO] Valor: %VALUE_NAME%
echo [INFO] Comando: %COMMAND%

reg add "%KEY_PATH%" /v "%VALUE_NAME%" /t REG_SZ /d "%COMMAND%" /f

if errorlevel 1 (
    echo [ERROR] No se pudo agregar la entrada al registro
) else (
    echo [OK] Entrada de registro creada exitosamente
)
goto :eof

:test_installation
echo.
echo ================================================================
echo                    CONFIGURACIÓN COMPLETADA
echo ================================================================
echo.
echo El Sistema POS Avanzado se iniciará automáticamente cuando
echo arranque Windows.
echo.
echo CONFIGURACIÓN APLICADA:
if "%METODO%"=="1" echo - Carpeta de Inicio: %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
if "%METODO%"=="2" echo - Registro de Windows: HKCU\Software\Microsoft\Windows\CurrentVersion\Run
if "%METODO%"=="3" echo - Carpeta de Inicio + Registro de Windows
echo.
echo PARA DESINSTALAR:
echo 1. Ejecuta: uninstall_autostart.bat
echo 2. O elimina manualmente los accesos/entradas creados
echo.

REM Preguntar si probar ahora
set /p TEST=¿Deseas probar el sistema ahora? (S/N): 

if /i "%TEST%"=="S" (
    echo.
    echo [INFO] Probando sistema de inicio automático...
    echo [INFO] Esto abrirá el sistema completo (Backend + Frontend)
    echo [INFO] Presiona Ctrl+C en la nueva ventana para detener
    echo.
    timeout 3 >nul
    start "Sistema POS - Prueba" python autostart_pos_system.py
    echo.
    echo [OK] Sistema iniciado en ventana separada
    echo [INFO] El navegador debería abrirse automáticamente
) else (
    echo.
    echo [INFO] El sistema se iniciará automáticamente en el próximo reinicio
)

echo.
echo ================================================================
echo.
pause
exit /b 0