import os
from celery import Celery

# 设置 Django 默认配置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Mall_Backend.settings')

app = Celery('Mall_Shop')

# 使用字符串以确保工作进程不必序列化配置对象
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动从所有已注册的 app 中加载 tasks.py
app.autodiscover_tasks()