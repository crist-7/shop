from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@shared_task
def send_welcome_email_task(user_id):
    """
    异步任务：发送用户注册成功欢迎邮件
    """
    try:
        user = User.objects.get(id=user_id)
        subject = '欢迎注册电商平台'
        message = f'尊敬的 {user.username}，感谢您注册我们的电商平台！祝您购物愉快。'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        # 模拟发送邮件（如果未配置邮件服务器，仅记录日志）
        send_mail(subject, message, from_email, recipient_list, fail_silently=True)
        logger.info(f'欢迎邮件已发送给用户 {user.username} ({user.email})')
    except User.DoesNotExist:
        logger.error(f'用户 {user_id} 不存在，无法发送欢迎邮件')
    except Exception as e:
        logger.error(f'发送欢迎邮件时发生错误: {e}')