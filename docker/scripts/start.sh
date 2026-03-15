#!/bin/sh
set -e

# ============================================================
# 生产环境启动脚本
# 功能：等待数据库 -> 执行迁移 -> 收集静态文件 -> 启动 Gunicorn
# ============================================================

echo "Waiting for database to be ready..."

# 等待数据库就绪（最多等待 60 秒），使用 Python 检查连接
python -c "
import os
import time
import socket

host = os.environ.get('DATABASE_HOST', 'db')
port = int(os.environ.get('DATABASE_PORT', 3306))

for i in range(60):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            print('Database is ready!')
            exit(0)
    except Exception as e:
        pass
    time.sleep(1)
    print(f'Waiting for database... ({i+1}/60)')

print('Error: Database is not ready after 60 seconds')
exit(1)
"

if [ $? -ne 0 ]; then
    echo "Failed to connect to database"
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
