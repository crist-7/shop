# ============================================================
# test_env_quick.ps1
# Quick test - uses cached images (no rebuild)
# ============================================================

param(
    [int]$WaitSeconds = 20,
    [int]$LogLines = 50
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Docker Quick Test (using cached images)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Clean up
Write-Host "[Step 1/4] Cleaning old containers..." -ForegroundColor Yellow
docker-compose down -v 2>$null
Write-Host "Done!" -ForegroundColor Green
Write-Host ""

# Step 2: Start (skip build, use cache)
Write-Host "[Step 2/4] Starting services (using cached images)..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to start! Trying to build first..." -ForegroundColor Red
    docker-compose build
    docker-compose up -d
}
Write-Host "Done!" -ForegroundColor Green
Write-Host ""

# Step 3: Wait
Write-Host "[Step 3/4] Waiting for services ($WaitSeconds seconds)..." -ForegroundColor Yellow
for ($i = $WaitSeconds; $i -gt 0; $i--) {
    Write-Host "`rRemaining: $i seconds...   " -NoNewline
    Start-Sleep -Seconds 1
}
Write-Host "`rWait complete!              " -ForegroundColor Green
Write-Host ""

# Check health
Write-Host "------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "Container Health Status:" -ForegroundColor Cyan
Write-Host "------------------------------------------------------------" -ForegroundColor DarkGray

Write-Host "`n[Database]" -ForegroundColor White
docker ps --filter "name=shop-db" --format "table {{.Names}}`t{{.Status}}`t{{.Ports}}"

Write-Host "`n[Backend]" -ForegroundColor White
docker ps --filter "name=shop-backend" --format "table {{.Names}}`t{{.Status}}`t{{.Ports}}"

Write-Host "`n------------------------------------------------------------"
Write-Host "All Services:" -ForegroundColor Cyan
Write-Host "------------------------------------------------------------"
docker-compose ps
Write-Host ""

# Step 4: Logs
Write-Host "------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "[Step 4/4] Backend logs (last $LogLines lines):" -ForegroundColor Cyan
Write-Host "------------------------------------------------------------" -ForegroundColor DarkGray
docker logs shop-backend --tail $LogLines 2>&1
Write-Host ""

# Summary
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Test Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

$unhealthy = docker ps --filter "health=unhealthy" --format "{{.Names}}"
if ($unhealthy) {
    Write-Host "`nWARNING: Unhealthy containers: $unhealthy" -ForegroundColor Red
} else {
    Write-Host "`nAll services running!" -ForegroundColor Green
    Write-Host "`nAccess URLs:" -ForegroundColor Cyan
    Write-Host "  Frontend:  http://localhost"
    Write-Host "  Backend:   http://localhost:8000/api/"
    Write-Host "  MySQL:     localhost:3307"
    Write-Host "  Redis:     localhost:6379"
    Write-Host "  ES:        http://localhost:9200"
}

Write-Host "`nStop: docker-compose down" -ForegroundColor DarkGray
