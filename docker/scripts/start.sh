#!/bin/bash
set -e

# ============================================================
# 生产环境启动脚本
# 功能：等待数据库 -> 执行迁移 -> 收集静态文件 -> 启动 Gunicorn
# ============================================================

echo "Waiting for database to be ready..."

# 磉待数据库就绪（最多等待 30 秒）
for i in {1..30}; do
    if mysqladmin ping -h "${DATABASE_HOST}" --silent 2>/dev/null; then
        echo "Database is ready!"
        break
    fi
    sleep 1
done

if [ $? -ne 0 ]; then
    echo "Error: Database is not ready after 30 seconds"
    exit 1
fi

# 执行数据库迁移
echo "Running database migrations..."
python manage.py migrate --noinput
# 收集静态文件
echo "Collecting static files..."
python manage.py collectstatic --noinput
# 启动 Gunicorn（4 workers）
echo "Starting Gunicorn with 4 workers..."
exec gunicorn --bind 0.0.0.0:8000 --workers 4 Mall_Backend.wsgi:application
