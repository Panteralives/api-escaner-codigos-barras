@echo off
REM ================================================================
REM Script de Instalación Automática - PC de Producción
REM Sistema de Escáner de Códigos de Barras
REM ================================================================

echo.
echo 🚀 INSTALACION DEL SISTEMA DE ESCANER DE CODIGOS DE BARRAS
echo ============================================================
echo.

REM Verificar si Python está instalado
echo 🔍 Verificando instalación de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado. Por favor instala Python primero.
    echo 💡 Descargar desde: https://python.org/downloads
    echo 💡 O desde Microsoft Store: Python 3.11
    pause
    exit /b 1
)

echo ✅ Python encontrado:
python --version

REM Verificar pip
echo.
echo 🔍 Verificando pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip no encontrado. Reinstala Python con pip incluido.
    pause
    exit /b 1
)

echo ✅ pip encontrado:
pip --version

REM Actualizar pip
echo.
echo 📦 Actualizando pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ⚠️ No se pudo actualizar pip, pero continuamos...
)

REM Instalar dependencias
echo.
echo 📦 Instalando dependencias del proyecto...
echo Esto puede tomar varios minutos...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Error instalando dependencias.
    echo 💡 Verifica conexión a Internet y permisos de administrador
    pause
    exit /b 1
)

echo ✅ Dependencias instaladas correctamente

REM Copiar configuración de producción
echo.
echo ⚙️ Configurando para entorno de producción...
if exist ".env.production" (
    copy ".env.production" ".env" >nul
    echo ✅ Configuración de producción aplicada
) else (
    echo ⚠️ Archivo .env.production no encontrado
)

REM Inicializar base de datos
echo.
echo 🗄️ Inicializando base de datos...
python run.py --init-db
if errorlevel 1 (
    echo ❌ Error inicializando base de datos
    pause
    exit /b 1
)

echo ✅ Base de datos inicializada

REM Crear script de inicio
echo.
echo 🚀 Creando script de inicio automático...
echo @echo off > start_production.bat
echo REM Script de inicio automático para producción >> start_production.bat
echo cd /d "%~dp0" >> start_production.bat
echo echo Iniciando sistema de inventario... >> start_production.bat
echo start "API Inventario" cmd /k "python run.py" >> start_production.bat
echo timeout /t 10 /nobreak ^>nul >> start_production.bat
echo start "Frontend Inventario" cmd /k "python run.py --frontend" >> start_production.bat

echo ✅ Script de inicio creado: start_production.bat

REM Probar instalación
echo.
echo 🧪 Probando instalación...
python run.py --info
if errorlevel 1 (
    echo ⚠️ Advertencia: Error en prueba del sistema
)

echo.
echo ============================================================
echo ✅ ¡INSTALACIÓN COMPLETADA EXITOSAMENTE!
echo ============================================================
echo.
echo 📋 PRÓXIMOS PASOS:
echo.
echo 1. Conectar el lector de código de barras USB
echo 2. Verificar que Windows detecta el dispositivo
echo 3. Ejecutar: python run.py --check-camera
echo 4. Probar el sistema: python run.py
echo 5. Para inicio automático: copiar start_production.bat a la carpeta de inicio
echo.
echo 📁 Carpeta de inicio: Win+R, escribir 'shell:startup', Enter
echo 🌐 API estará en: http://localhost:8000
echo 🖥️ Frontend estará en: http://localhost:8501
echo.
echo ============================================================
pause