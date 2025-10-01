# Script para detectar lector de código de barras
# Ejecutar con: powershell -ExecutionPolicy Bypass .\detectar_scanner.ps1

Write-Host "🔍 Detectando lectores de código de barras USB..." -ForegroundColor Green
Write-Host "=" * 60

Write-Host "`n📱 DISPOSITIVOS HID (Human Interface Device):" -ForegroundColor Yellow
Get-WmiObject -Class Win32_PnPEntity | Where-Object { 
    $_.Name -match "HID|Input|Scanner|Barcode" 
} | ForEach-Object {
    Write-Host "  ✅ $($_.Name) - $($_.DeviceID)" -ForegroundColor White
}

Write-Host "`n🔌 PUERTOS SERIALES (COM):" -ForegroundColor Yellow  
Get-WmiObject -Class Win32_PnPEntity | Where-Object { 
    $_.Name -match "COM\d+|Serial|USB.*Port" 
} | ForEach-Object {
    Write-Host "  ✅ $($_.Name) - $($_.DeviceID)" -ForegroundColor White
}

Write-Host "`n📺 DISPOSITIVOS USB GENÉRICOS:" -ForegroundColor Yellow
Get-WmiObject -Class Win32_PnPEntity | Where-Object { 
    $_.Name -match "USB.*Device|Unknown|Composite" 
} | ForEach-Object {
    Write-Host "  ✅ $($_.Name) - $($_.DeviceID)" -ForegroundColor White
}

Write-Host "`n🔧 PUERTOS COM DISPONIBLES:" -ForegroundColor Yellow
[System.IO.Ports.SerialPort]::getportnames() | ForEach-Object {
    Write-Host "  ✅ Puerto $_" -ForegroundColor White
}

Write-Host "`n" + "=" * 60
Write-Host "💡 INSTRUCCIONES:" -ForegroundColor Cyan
Write-Host "1. Desconecta el scanner" -ForegroundColor White
Write-Host "2. Ejecuta este script" -ForegroundColor White  
Write-Host "3. Conecta el scanner" -ForegroundColor White
Write-Host "4. Ejecuta el script otra vez" -ForegroundColor White
Write-Host "5. Compara las diferencias" -ForegroundColor White