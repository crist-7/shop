#!/bin/sh

# 等待数据库就绪
echo "等待数据库就绪..."
sleep 10

# 替换数据库主机为 Docker 服务名
echo "配置数据库连接..."
sed -i "s/'HOST': '127.0.0.1'/'HOST': 'db'/" /app/Mall_Backend/settings.py

# 替换 Redis 连接为 Docker 服务名
sed -i "s/127.0.0.1:6379/redis:6379/g" /app/Mall_Backend/settings.py

# 设置生产环境配置
echo "设置生产环境配置..."
sed -i "s/DEBUG = True/DEBUG = False/" /app/Mall_Backend/settings.py
sed -i "s/ALLOWED_HOSTS = \[\]/ALLOWED_HOSTS = \['\*'\]/" /app/Mall_Backend/settings.py

# 运行数据库迁移
echo "运行数据库迁移..."
python manage.py migrate

# 收集静态文件
echo "收集静态文件..."
python manage.py collectstatic --noinput

# 启动 Gunicorn
echo "启动 Gunicorn 服务器..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 Mall_Backend.wsgi:application