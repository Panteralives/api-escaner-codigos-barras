# ================================================================
# 🚀 CONFIGURAR INICIO AUTOMÁTICO - SISTEMA POS AVANZADO
# ================================================================
# Script PowerShell para configurar inicio automático en Windows
# 
# Autor: Claude AI Assistant
# Fecha: 01 de Octubre, 2025
# ================================================================

param(
    [switch]$Remove,
    [switch]$Force
)

# Configuración
$ErrorActionPreference = "Stop"
$AppName = "SistemaPOSAvanzado"
$ProjectDir = "C:\InventarioBarras"
$ScriptPath = Join-Path $ProjectDir "autostart_pos.bat"

# Colores para output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    switch ($Color) {
        "Green" { Write-Host $Message -ForegroundColor Green }
        "Red" { Write-Host $Message -ForegroundColor Red }
        "Yellow" { Write-Host $Message -ForegroundColor Yellow }
        "Cyan" { Write-Host $Message -ForegroundColor Cyan }
        default { Write-Host $Message }
    }
}

function Show-Header {
    Write-Host ""
    Write-ColorOutput "================================================================" "Cyan"
    Write-ColorOutput "           CONFIGURAR INICIO AUTOMÁTICO - SISTEMA POS" "Cyan"
    Write-ColorOutput "================================================================" "Cyan"
    Write-Host ""
}

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Add-AutoStart {
    Write-ColorOutput "Configurando inicio automático..." "Yellow"
    
    try {
        # Verificar que el script existe
        if (-not (Test-Path $ScriptPath)) {
            throw "El archivo de script no existe: $ScriptPath"
        }
        
        # Crear comando de inicio automático (minimizado)
        $StartupCommand = "`"$ScriptPath`" auto"
        
        # Método 1: Registro de Windows (para usuario actual)
        Write-ColorOutput "Agregando entrada al registro de Windows..." "Yellow"
        
        $RegPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
        Set-ItemProperty -Path $RegPath -Name $AppName -Value $StartupCommand -Force
        
        Write-ColorOutput "✓ Entrada de registro creada exitosamente" "Green"
        
        # Método 2: Carpeta de inicio como backup
        Write-ColorOutput "Creando acceso directo en carpeta de inicio..." "Yellow"
        
        $StartupFolder = [Environment]::GetFolderPath('Startup')
        $ShortcutPath = Join-Path $StartupFolder "$AppName.lnk"
        
        $WshShell = New-Object -comObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
        $Shortcut.TargetPath = "cmd.exe"
        $Shortcut.Arguments = "/c `"$StartupCommand`""
        $Shortcut.WorkingDirectory = $ProjectDir
        $Shortcut.WindowStyle = 7  # Minimized
        $Shortcut.Description = "Sistema POS Avanzado - Inicio Automático"
        $Shortcut.Save()
        
        Write-ColorOutput "✓ Acceso directo creado: $ShortcutPath" "Green"
        
        # Crear un acceso directo en el escritorio para control manual
        $DesktopPath = [Environment]::GetFolderPath('Desktop')
        $DesktopShortcut = Join-Path $DesktopPath "Sistema POS Avanzado.lnk"
        
        $DesktopSC = $WshShell.CreateShortcut($DesktopShortcut)
        $DesktopSC.TargetPath = $ScriptPath
        $DesktopSC.WorkingDirectory = $ProjectDir
        $DesktopSC.Description = "Sistema POS Avanzado - Control Manual"
        $DesktopSC.Save()
        
        Write-ColorOutput "✓ Acceso directo en escritorio: $DesktopShortcut" "Green"
        
        Write-Host ""
        Write-ColorOutput "================================================================" "Green"
        Write-ColorOutput "           CONFIGURACIÓN COMPLETADA EXITOSAMENTE" "Green"
        Write-ColorOutput "================================================================" "Green"
        Write-Host ""
        Write-ColorOutput "El Sistema POS Avanzado se iniciará automáticamente cuando" "Green"
        Write-ColorOutput "Windows arranque. El sistema:" "Green"
        Write-Host ""
        Write-ColorOutput "• Iniciará el backend API automáticamente" "White"
        Write-ColorOutput "• Iniciará el frontend web automáticamente" "White"
        Write-ColorOutput "• Abrirá la interfaz en el navegador lista para trabajar" "White"
        Write-ColorOutput "• Se ejecutará minimizado en segundo plano" "White"
        Write-Host ""
        Write-ColorOutput "CONTROL MANUAL:" "Yellow"
        Write-ColorOutput "• Acceso directo en escritorio: 'Sistema POS Avanzado'" "White"
        Write-ColorOutput "• Para detener: Ctrl+C en la ventana de comandos" "White"
        Write-Host ""
        Write-ColorOutput "DESACTIVAR AUTOSTART:" "Yellow"
        Write-ColorOutput "PowerShell: .\setup_autostart_windows.ps1 -Remove" "White"
        Write-Host ""
        
        return $true
    }
    catch {
        Write-ColorOutput "ERROR: $($_.Exception.Message)" "Red"
        return $false
    }
}

function Remove-AutoStart {
    Write-ColorOutput "Removiendo configuración de inicio automático..." "Yellow"
    
    try {
        $removed = $false
        
        # Remover del registro
        try {
            $RegPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
            Remove-ItemProperty -Path $RegPath -Name $AppName -ErrorAction Stop
            Write-ColorOutput "✓ Entrada de registro removida" "Green"
            $removed = $true
        }
        catch {
            Write-ColorOutput "! No se encontró entrada en registro (o ya fue removida)" "Yellow"
        }
        
        # Remover acceso directo de startup
        $StartupFolder = [Environment]::GetFolderPath('Startup')
        $ShortcutPath = Join-Path $StartupFolder "$AppName.lnk"
        
        if (Test-Path $ShortcutPath) {
            Remove-Item $ShortcutPath -Force
            Write-ColorOutput "✓ Acceso directo de startup removido" "Green"
            $removed = $true
        }
        else {
            Write-ColorOutput "! Acceso directo de startup no encontrado" "Yellow"
        }
        
        # Preguntar si remover acceso directo del escritorio
        $DesktopPath = [Environment]::GetFolderPath('Desktop')
        $DesktopShortcut = Join-Path $DesktopPath "Sistema POS Avanzado.lnk"
        
        if (Test-Path $DesktopShortcut) {
            $response = Read-Host "¿Remover también el acceso directo del escritorio? (s/N)"
            if ($response -match "^[sS]") {
                Remove-Item $DesktopShortcut -Force
                Write-ColorOutput "✓ Acceso directo del escritorio removido" "Green"
            }
        }
        
        if ($removed) {
            Write-Host ""
            Write-ColorOutput "================================================================" "Green"
            Write-ColorOutput "        INICIO AUTOMÁTICO DESACTIVADO EXITOSAMENTE" "Green"
            Write-ColorOutput "================================================================" "Green"
            Write-Host ""
            Write-ColorOutput "El Sistema POS ya NO se iniciará automáticamente." "Green"
            Write-Host ""
        }
        else {
            Write-ColorOutput "! No se encontraron configuraciones de autostart para remover" "Yellow"
        }
        
        return $true
    }
    catch {
        Write-ColorOutput "ERROR removiendo autostart: $($_.Exception.Message)" "Red"
        return $false
    }
        
        if ($removed) {
            Write-Host ""
            Write-ColorOutput "================================================================" "Green"
            Write-ColorOutput "        INICIO AUTOMÁTICO DESACTIVADO EXITOSAMENTE" "Green"
            Write-ColorOutput "================================================================" "Green"
            Write-Host ""
            Write-ColorOutput "El Sistema POS ya NO se iniciará automáticamente." "Green"
            Write-Host ""
        }
        else {
            Write-ColorOutput "! No se encontraron configuraciones de autostart para remover" "Yellow"
        }
        
        return $true
    }
    catch {
        Write-ColorOutput "ERROR removiendo autostart: $($_.Exception.Message)" "Red"
        return $false
    }
}

function Test-SystemRequirements {
    Write-ColorOutput "Verificando requisitos del sistema..." "Yellow"
    
    $issues = @()
    
    # Verificar Python
    try {
        $pythonVersion = & python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ Python instalado: $pythonVersion" "Green"
        }
        else {
            $issues += "Python no está instalado o no está en PATH"
        }
    }
    catch {
        $issues += "Python no está instalado o no está en PATH"
    }
    
    # Verificar directorio del proyecto
    if (-not (Test-Path $ProjectDir)) {
        $issues += "Directorio del proyecto no encontrado: $ProjectDir"
    }
    else {
        Write-ColorOutput "✓ Directorio del proyecto encontrado" "Green"
    }
    
    # Verificar script de autostart
    if (-not (Test-Path $ScriptPath)) {
        $issues += "Script de autostart no encontrado: $ScriptPath"
    }
    else {
        Write-ColorOutput "✓ Script de autostart encontrado" "Green"
    }
    
    # Verificar requirements.txt
    $RequirementsPath = Join-Path $ProjectDir "requirements.txt"
    if (-not (Test-Path $RequirementsPath)) {
        $issues += "Archivo requirements.txt no encontrado"
    }
    else {
        Write-ColorOutput "✓ Archivo requirements.txt encontrado" "Green"
    }
    
    if ($issues.Count -gt 0) {
        Write-Host ""
        Write-ColorOutput "PROBLEMAS ENCONTRADOS:" "Red"
        foreach ($issue in $issues) {
            Write-ColorOutput "✗ $issue" "Red"
        }
        Write-Host ""
        Write-ColorOutput "Por favor, corrija estos problemas antes de continuar." "Red"
        return $false
    }
    
    Write-ColorOutput "✓ Todos los requisitos del sistema están completos" "Green"
    return $true
}

# ================================================================
# SCRIPT PRINCIPAL
# ================================================================

Show-Header

# Verificar requisitos
if (-not (Test-SystemRequirements)) {
    Write-Host ""
    Write-ColorOutput "Presiona Enter para salir..." "Yellow"
    Read-Host
    exit 1
}

Write-Host ""

# Ejecutar acción solicitada
if ($Remove) {
    $success = Remove-AutoStart
}
else {
    # Verificar si ya está configurado
    $RegPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
    $CurrentValue = Get-ItemProperty -Path $RegPath -Name $AppName -ErrorAction SilentlyContinue
    
    if ($CurrentValue -and -not $Force) {
        Write-ColorOutput "El inicio automático ya está configurado." "Yellow"
        Write-ColorOutput "Comando actual: $($CurrentValue.$AppName)" "White"
        Write-Host ""
        
        $response = Read-Host "¿Reconfigurar el inicio automático? (s/N)"
        if (-not ($response -match "^[sS]")) {
            Write-ColorOutput "Operación cancelada." "Yellow"
            exit 0
        }
    }
    
    $success = Add-AutoStart
}

Write-Host ""
if ($success) {
    Write-ColorOutput "Operación completada exitosamente." "Green"
    
    if (-not $Remove) {
        Write-Host ""
        $response = Read-Host "¿Probar el sistema ahora? (S/n)"
        if (-not ($response -match "^[nN]")) {
            Write-ColorOutput "Iniciando sistema de prueba..." "Yellow"
            Start-Process -FilePath $ScriptPath -WorkingDirectory $ProjectDir
        }
    }
}
else {
    Write-ColorOutput "La operación no se completó correctamente." "Red"
    exit 1
}

Write-Host ""
Write-ColorOutput "Presiona Enter para continuar..." "Yellow"
Read-Host