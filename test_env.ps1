# ============================================================
# test_env.ps1
# Docker Environment Test Script (Windows PowerShell)
# ============================================================

param(
    [int]$WaitSeconds = 20,
    [int]$LogLines = 50
)

$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Docker Environment Test Script" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Clean up
Write-Host "[Step 1/5] Cleaning old containers and volumes..." -ForegroundColor Yellow
docker-compose down -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Error during cleanup, continuing..." -ForegroundColor DarkYellow
}
Write-Host "Done!" -ForegroundColor Green
Write-Host ""

# Step 2: Build
Write-Host "[Step 2/5] Building images (no cache)..." -ForegroundColor Yellow
docker-compose build --no-cache
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "Done!" -ForegroundColor Green
Write-Host ""

# Step 3: Start
Write-Host "[Step 3/5] Starting services in background..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to start services!" -ForegroundColor Red
    exit 1
}
Write-Host "Done!" -ForegroundColor Green
Write-Host ""

# Step 4: Wait and check health
Write-Host "[Step 4/5] Waiting for services ($WaitSeconds seconds)..." -ForegroundColor Yellow

for ($i = $WaitSeconds; $i -gt 0; $i--) {
    Write-Host "`rRemaining: $i seconds...   " -NoNewline
    Start-Sleep -Seconds 1
}
Write-Host "`rWait complete!              " -ForegroundColor Green
Write-Host ""

# Check container health
Write-Host "------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "Container Health Status:" -ForegroundColor Cyan
Write-Host "------------------------------------------------------------" -ForegroundColor DarkGray

Write-Host ""
Write-Host "[Database (db)]" -ForegroundColor White
docker ps --filter "name=shop-db" --format "table {{.Names}}`t{{.Status}}`t{{.Ports}}"

Write-Host ""
Write-Host "[Backend]" -ForegroundColor White
docker ps --filter "name=shop-backend" --format "table {{.Names}}`t{{.Status}}`t{{.Ports}}"

Write-Host ""
Write-Host "------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "All Services:" -ForegroundColor Cyan
Write-Host "------------------------------------------------------------" -ForegroundColor DarkGray
docker-compose ps
Write-Host ""

# Step 5: Print backend logs
Write-Host "------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "[Step 5/5] Backend startup logs (last $LogLines lines):" -ForegroundColor Cyan
Write-Host "------------------------------------------------------------" -ForegroundColor DarkGray
docker logs shop-backend --tail $LogLines 2>&1
Write-Host ""

# Summary
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Test Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$unhealthy = docker ps --filter "health=unhealthy" --format "{{.Names}}"
if ($unhealthy) {
    Write-Host "WARNING: Unhealthy containers detected:" -ForegroundColor Red
    Write-Host "  - $unhealthy" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check logs with:" -ForegroundColor Yellow
    Write-Host "  docker logs shop-backend" -ForegroundColor White
    Write-Host "  docker logs shop-db" -ForegroundColor White
} else {
    Write-Host "All services running normally!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access URLs:" -ForegroundColor Cyan
    Write-Host "  - Frontend:  http://localhost" -ForegroundColor White
    Write-Host "  - Backend:   http://localhost:8000/api/" -ForegroundColor White
    Write-Host "  - MySQL:     localhost:3307" -ForegroundColor White
    Write-Host "  - Redis:     localhost:6379" -ForegroundColor White
    Write-Host "  - ES:        http://localhost:9200" -ForegroundColor White
}

Write-Host ""
Write-Host "Stop all services: docker-compose down" -ForegroundColor DarkGray
