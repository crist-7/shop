# 本地开发环境变量设置脚本（PowerShell）
# 使用方法：在 PowerShell 中执行： .\setup_local.ps1
# 或者直接复制下面的命令到你的终端

# 设置数据库连接（使用 Docker 容器）
$env:DATABASE_HOST = "localhost"
$env:DATABASE_PORT = "3307"
$env:DATABASE_NAME = "shop_db"
$env:DATABASE_USER = "root"
$env:DATABASE_PASSWORD = "root"

# 设置 Redis 连接（使用 Docker 容器）
$env:REDIS_HOST = "localhost"
$env:REDIS_PORT = "6379"

# 调试模式
$env:DEBUG = "True"

# 允许的主机（开发环境可以使用通配符）
$env:ALLOWED_HOSTS = "*"

# 显示设置的环境变量
Write-Host "环境变量已设置：" -ForegroundColor Green
Write-Host "DATABASE_HOST: $env:DATABASE_HOST"
Write-Host "DATABASE_PORT: $env:DATABASE_PORT"
Write-Host "REDIS_HOST: $env:REDIS_HOST"
Write-Host "DEBUG: $env:DEBUG"
Write-Host ""
Write-Host "接下来可以运行：" -ForegroundColor Yellow
Write-Host "1. 启动数据库和Redis: docker-compose -f docker-compose.dev.yml up db redis"
Write-Host "2. 安装Python依赖: pip install -r requirements.txt"
Write-Host "3. 运行数据库迁移: python manage.py migrate"
Write-Host "4. 启动Django开发服务器: python manage.py runserver"
Write-Host ""
Write-Host "或者使用 Docker 运行所有服务：" -ForegroundColor Yellow
Write-Host "docker-compose -f docker-compose.dev.yml up"