# stop_all.ps1
Write-Host "Arrêt de tous les services..." -ForegroundColor Yellow

# Arrêter Docker Compose
docker-compose down

# Arrêter les processus Python du projet (optionnel)
Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*generate_prometheus*" -or 
    $_.CommandLine -like "*gradio_app*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "✅ Tous les services arrêtés" -ForegroundColor Green