#!/bin/sh

# 等待数据库就绪
echo "等待数据库就绪..."
sleep 10

# 注意：现在使用环境变量配置数据库和Redis连接
# 请确保设置了以下环境变量：
# DATABASE_HOST, DATABASE_PORT, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD
# REDIS_HOST, REDIS_PORT
# DEBUG, ALLOWED_HOSTS

# 运行数据库迁移
echo "运行数据库迁移..."
python manage.py migrate

# 收集静态文件
echo "收集静态文件..."
python manage.py collectstatic --noinput

# 启动 Gunicorn
echo "启动 Gunicorn 服务器..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 Mall_Backend.wsgi:application