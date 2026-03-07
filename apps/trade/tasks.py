from celery import shared_task
from .models import OrderInfo
import logging

logger = logging.getLogger(__name__)

@shared_task
def close_order_task(order_id):
    """
    异步任务：超时未支付自动关闭订单
    """
    try:
        order = OrderInfo.objects.get(id=order_id)
        if order.pay_status == "paying":  # 如果状态仍为待支付
            order.pay_status = "closed"
            order.save()
            logger.info(f"订单 {order_id} 超时未支付，已自动关闭")
    except OrderInfo.DoesNotExist:
        logger.error(f"订单 {order_id} 不存在")