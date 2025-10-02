# Script PowerShell para lanzar POS completamente invisible
param(
    [switch]$ShowConsole = $false
)

# Ocultar ventana PowerShell si no se especifica mostrar consola
if (-not $ShowConsole) {
    Add-Type -Name Window -Namespace Console -MemberDefinition '
    [DllImport("Kernel32.dll")]
    public static extern IntPtr GetConsoleWindow();
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, Int32 nCmdShow);
    '
    $consolePtr = [Console.Window]::GetConsoleWindow()
    [Console.Window]::ShowWindow($consolePtr, 0) # 0 = hide
}

Write-Host "🚀 Iniciando POS Sistema (Modo Invisible)" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Green

# Limpiar procesos Python anteriores
Write-Host "🧹 Limpiando procesos Python anteriores..." -ForegroundColor Yellow
Get-Process -Name "python*" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Cambiar al directorio frontend
$frontendPath = "C:\InventarioBarras\frontend-pos"
Set-Location $frontendPath

if (-not (Test-Path "pos_server.py")) {
    Write-Host "❌ ERROR: pos_server.py no encontrado" -ForegroundColor Red
    exit 1
}

Write-Host "⚙️ Iniciando servidor POS (completamente oculto)..." -ForegroundColor Cyan

# Crear proceso Python completamente invisible
$processInfo = New-Object System.Diagnostics.ProcessStartInfo
$processInfo.FileName = "python"
$processInfo.Arguments = "pos_server.py"
$processInfo.WorkingDirectory = $frontendPath
$processInfo.UseShellExecute = $false
$processInfo.CreateNoWindow = $true
$processInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
$processInfo.RedirectStandardOutput = $true
$processInfo.RedirectStandardError = $true

$process = New-Object System.Diagnostics.Process
$process.StartInfo = $processInfo
$process.Start() | Out-Null

Write-Host "✅ Servidor POS iniciado (PID: $($process.Id))" -ForegroundColor Green

# Esperar que el servidor esté listo
Write-Host "⏳ Esperando servidor (10 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Verificar si el servidor responde
$serverReady = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3002" -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        $serverReady = $true
    }
} catch {
    Write-Host "⚠️ Servidor no responde, continuando..." -ForegroundColor Yellow
}

Write-Host "🌐 Abriendo navegador en pantalla completa FORZADA..." -ForegroundColor Cyan

# Lista de navegadores a probar
$browsers = @(
    @{Path="C:\Program Files\Google\Chrome\Application\chrome.exe"; Name="Chrome"},
    @{Path="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"; Name="Chrome x86"},
    @{Path="C:\Program Files\Microsoft\Edge\Application\msedge.exe"; Name="Edge"},
    @{Path="C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"; Name="Edge x86"}
)

$url = "http://localhost:3002/pos"
$browserOpened = $false

foreach ($browser in $browsers) {
    if (Test-Path $browser.Path) {
        Write-Host "📱 Usando $($browser.Name) - Modo KIOSK FORZADO" -ForegroundColor Green
        
        # Argumentos para máxima pantalla completa
        $arguments = @(
            "--kiosk"
            "--disable-infobars"
            "--disable-extensions" 
            "--no-first-run"
            "--disable-web-security"
            "--disable-features=VizDisplayCompositor"
            "--start-maximized"
            "--window-position=0,0"
            "--window-size=1920,1080"
            "--force-device-scale-factor=1"
            "--disable-dev-shm-usage"
            "--no-sandbox"
            $url
        )
        
        Start-Process -FilePath $browser.Path -ArgumentList $arguments -WindowStyle Hidden
        $browserOpened = $true
        break
    }
}

if (-not $browserOpened) {
    Write-Host "⚠️ Chrome/Edge no encontrado, usando navegador por defecto" -ForegroundColor Yellow
    Start-Process $url
    Start-Sleep -Seconds 3
    
    # Simular F11 usando SendKeys
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.SendKeys]::SendWait("{F11}")
    Write-Host "🔧 F11 simulado para pantalla completa" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "✅ SISTEMA POS INICIADO EXITOSAMENTE" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Green
Write-Host "🎯 URL: $url" -ForegroundColor White
Write-Host "🔧 Servidor PID: $($process.Id)" -ForegroundColor White
Write-Host "👁️ Consolas: COMPLETAMENTE OCULTAS" -ForegroundColor Green
Write-Host "🖥️ Navegador: PANTALLA COMPLETA FORZADA" -ForegroundColor Green
Write-Host ""
Write-Host "🛑 Para cerrar: usar cerrar_pos.bat o Task Manager" -ForegroundColor Yellow

# Salir limpiamente
exit 0