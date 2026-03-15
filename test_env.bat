@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ============================================================
REM test_env.bat
REM Docker 环境一键测试脚本 (Windows CMD)
REM ============================================================

set WAIT_SECONDS=20
set LOG_LINES=50

echo ============================================================
echo   Docker 环境自动化测试脚本
echo ============================================================
echo.

REM Step 1: 清理
echo [Step 1/5] 清理旧容器和数据卷...
docker-compose down -v
echo 完成!
echo.

REM Step 2: 构建
echo [Step 2/5] 无缓存重新构建镜像 (这可能需要几分钟)...
docker-compose build --no-cache
if errorlevel 1 (
    echo 错误: 镜像构建失败!
    exit /b 1
)
echo 完成!
echo.

REM Step 3: 启动
echo [Step 3/5] 后台启动所有服务...
docker-compose up -d
if errorlevel 1 (
    echo 错误: 服务启动失败!
    exit /b 1
)
echo 完成!
echo.

REM Step 4: 等待
echo [Step 4/5] 等待服务启动 (!WAIT_SECONDS! 秒)...

REM 倒计时
set /a count=%WAIT_SECONDS%
:countdown
if !count! gtr 0 (
    set /p "=剩余: !count! 秒..." <nul
    timeout /t 1 /nobreak >nul
    set /a count-=1
    echo.
    goto countdown
)
echo 等待完成!
echo.

REM 检查健康状态
echo ------------------------------------------------------------
echo 容器健康状态检查:
echo ------------------------------------------------------------
echo.
echo [数据库 (db)]
docker ps --filter "name=shop-db" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.
echo [后端 (backend)]
docker ps --filter "name=shop-backend" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.
echo ------------------------------------------------------------
echo 所有服务概览:
echo ------------------------------------------------------------
docker-compose ps
echo.

REM Step 5: 日志
echo ------------------------------------------------------------
echo [Step 5/5] Backend 启动日志 (最近 !LOG_LINES! 行):
echo ------------------------------------------------------------
docker logs shop-backend --tail !LOG_LINES! 2>&1
echo.

REM 总结
echo ============================================================
echo   测试完成!
echo ============================================================
echo.
echo 访问地址:
echo   - 前端:     http://localhost
echo   - 后端 API: http://localhost:8000/api/
echo   - MySQL:    localhost:3307
echo   - Redis:    localhost:6379
echo   - ES:       http://localhost:9200
echo.
echo 停止所有服务: docker-compose down

pause
