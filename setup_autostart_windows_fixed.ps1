# ================================================================
# 🚀 CONFIGURAR INICIO AUTOMÁTICO - SISTEMA POS AVANZADO
# ================================================================
param(
    [switch]$Remove,
    [switch]$Force
)

$AppName = "SistemaPOSAvanzado"
$ProjectDir = "C:\InventarioBarras"
$ScriptPath = Join-Path $ProjectDir "autostart_pos.bat"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
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

function Test-SystemRequirements {
    Write-ColorOutput "Verificando requisitos del sistema..." "Yellow"
    $issues = @()
    
    try {
        $pythonVersion = & python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ Python instalado: $pythonVersion" "Green"
        } else {
            $issues += "Python no está instalado o no está en PATH"
        }
    } catch {
        $issues += "Python no está instalado o no está en PATH"
    }
    
    if (-not (Test-Path $ProjectDir)) {
        $issues += "Directorio del proyecto no encontrado: $ProjectDir"
    } else {
        Write-ColorOutput "✓ Directorio del proyecto encontrado" "Green"
    }
    
    if (-not (Test-Path $ScriptPath)) {
        $issues += "Script de autostart no encontrado: $ScriptPath"
    } else {
        Write-ColorOutput "✓ Script de autostart encontrado" "Green"
    }
    
    if ($issues.Count -gt 0) {
        Write-Host ""
        Write-ColorOutput "PROBLEMAS ENCONTRADOS:" "Red"
        foreach ($issue in $issues) {
            Write-ColorOutput "✗ $issue" "Red"
        }
        return $false
    }
    
    Write-ColorOutput "✓ Todos los requisitos están completos" "Green"
    return $true
}

function Add-AutoStart {
    Write-ColorOutput "Configurando inicio automático..." "Yellow"
    
    try {
        $StartupCommand = "`"$ScriptPath`" auto"
        
        # Registro de Windows
        $RegPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
        Set-ItemProperty -Path $RegPath -Name $AppName -Value $StartupCommand -Force
        Write-ColorOutput "✓ Entrada de registro creada" "Green"
        
        # Acceso directo en escritorio
        $DesktopPath = [Environment]::GetFolderPath('Desktop')
        $DesktopShortcut = Join-Path $DesktopPath "Sistema POS Avanzado.lnk"
        
        $WshShell = New-Object -comObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut($DesktopShortcut)
        $Shortcut.TargetPath = $ScriptPath
        $Shortcut.WorkingDirectory = $ProjectDir
        $Shortcut.Description = "Sistema POS Avanzado - Control Manual"
        $Shortcut.Save()
        
        Write-ColorOutput "✓ Acceso directo en escritorio creado" "Green"
        
        Write-Host ""
        Write-ColorOutput "================================================================" "Green"
        Write-ColorOutput "           CONFIGURACIÓN COMPLETADA EXITOSAMENTE" "Green"
        Write-ColorOutput "================================================================" "Green"
        Write-Host ""
        Write-ColorOutput "El Sistema POS se iniciará automáticamente al arrancar Windows" "Green"
        Write-Host ""
        Write-ColorOutput "CARACTERÍSTICAS:" "Yellow"
        Write-ColorOutput "• Backend API se inicia automáticamente" "White"
        Write-ColorOutput "• Frontend web se abre automáticamente" "White"
        Write-ColorOutput "• Interfaz lista para trabajar en el navegador" "White"
        Write-ColorOutput "• Ejecución minimizada en segundo plano" "White"
        Write-Host ""
        Write-ColorOutput "CONTROL MANUAL:" "Yellow"
        Write-ColorOutput "• Acceso directo: 'Sistema POS Avanzado' en escritorio" "White"
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
            Write-ColorOutput "! Entrada de registro no encontrada" "Yellow"
        }
        
        # Remover acceso directo del escritorio
        $DesktopPath = [Environment]::GetFolderPath('Desktop')
        $DesktopShortcut = Join-Path $DesktopPath "Sistema POS Avanzado.lnk"
        
        if (Test-Path $DesktopShortcut) {
            $response = Read-Host "¿Remover acceso directo del escritorio? (s/N)"
            if ($response -match "^[sS]") {
                Remove-Item $DesktopShortcut -Force
                Write-ColorOutput "✓ Acceso directo removido" "Green"
            }
        }
        
        if ($removed) {
            Write-Host ""
            Write-ColorOutput "Inicio automático desactivado exitosamente" "Green"
        }
        
        return $true
    }
    catch {
        Write-ColorOutput "ERROR: $($_.Exception.Message)" "Red"
        return $false
    }
}

# SCRIPT PRINCIPAL
Show-Header

if (-not (Test-SystemRequirements)) {
    Write-ColorOutput "Por favor corrija los problemas antes de continuar" "Red"
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""

if ($Remove) {
    $success = Remove-AutoStart
} else {
    # Verificar si ya está configurado
    $RegPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
    $CurrentValue = Get-ItemProperty -Path $RegPath -Name $AppName -ErrorAction SilentlyContinue
    
    if ($CurrentValue -and -not $Force) {
        Write-ColorOutput "El inicio automático ya está configurado" "Yellow"
        $response = Read-Host "¿Reconfigurar? (s/N)"
        if (-not ($response -match "^[sS]")) {
            exit 0
        }
    }
    
    $success = Add-AutoStart
}

if ($success) {
    Write-ColorOutput "Operación completada exitosamente" "Green"
    
    if (-not $Remove) {
        Write-Host ""
        $response = Read-Host "¿Probar el sistema ahora? (S/n)"
        if (-not ($response -match "^[nN]")) {
            Write-ColorOutput "Iniciando sistema..." "Yellow"
            Start-Process -FilePath $ScriptPath -WorkingDirectory $ProjectDir
        }
    }
} else {
    Write-ColorOutput "La operación falló" "Red"
    exit 1
}

Write-Host ""
Read-Host "Presiona Enter para continuar"