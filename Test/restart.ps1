# 重启 Django 和 Vite 服务
$conns = Get-NetTCPConnection -LocalPort 8000,5173 -State Listen -ErrorAction SilentlyContinue
foreach ($conn in $conns) {
    $proc = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
    if ($proc) {
        Write-Output "Stopping port $($conn.LocalPort) PID $($conn.OwningProcess) ($($proc.ProcessName))"
        Stop-Process -Id $conn.OwningProcess -Force
    }
}
Start-Sleep -Seconds 2
Write-Output "All stopped"
