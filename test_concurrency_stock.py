#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
并发库存扣减测试脚本
=====================
用于验证防超卖机制的有效性

运行方式:
    cd D:\dissertation\shop
    python test_concurrency_stock.py
"""

import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import django
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Mall_Backend.settings')
django.setup()

# 禁用所有 Elasticsearch 信号
from django.conf import settings
settings.ELASTICSEARCH_DSL_AUTOSYNC = False

try:
    from django_elasticsearch_dsl.registries import registry
    registry._indices = {}
    registry._documents = {}
except Exception:
    pass

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import F
from goods.models import Product, Category
from trade.models import OrderInfo, OrderGoods

User = get_user_model()


class ConcurrencyTestResult:
    def __init__(self):
        self.success_count = 0
        self.failure_count = 0
        self.lock = threading.Lock()

    def add_success(self):
        with self.lock:
            self.success_count += 1

    def add_failure(self):
        with self.lock:
            self.failure_count += 1


def setup_test_data():
    """创建测试数据"""
    print("\n" + "="*60)
    print("[Step 1] Setup Test Data")
    print("="*60)

    # 清理旧数据
    OrderGoods.objects.filter(order__order_sn__startswith="CONC_TEST").delete()
    OrderInfo.objects.filter(order_sn__startswith="CONC_TEST").delete()
    User.objects.filter(username__startswith="conc_test_").delete()
    Product.objects.filter(name="Concurrent Test Product").delete()
    Category.objects.filter(name="Concurrent Test Category").delete()

    # 创建分类
    category = Category.objects.create(name="Concurrent Test Category")

    # 创建商品 - 初始库存10
    product = Product.objects.create(
        name="Concurrent Test Product",
        category=category,
        shop_price=Decimal('99.99'),
        market_price=Decimal('99.99'),
        goods_num=10,
        sold_num=0,
        goods_sn="CONC001",
        goods_brief="Test product for concurrency"
    )

    print(f"  Product: {product.name}")
    print(f"  Initial Stock: {product.goods_num}")
    print(f"  Initial Sold: {product.sold_num}")

    # 创建订单
    orders = []
    for i in range(20):
        user = User.objects.create_user(
            username=f"conc_test_{i}",
            email=f"test{i}@test.com",
            password="test123"
        )

        order = OrderInfo.objects.create(
            user=user,
            order_sn=f"CONC_TEST_{int(time.time())}_{i:03d}",
            order_mount=Decimal('99.99'),
            pay_status="PAYING",
            address="Test Address",
            signer_name=f"User {i}",
            signer_mobile="13800138000"
        )

        OrderGoods.objects.create(
            order=order,
            goods=product,
            goods_num=1,
            price=Decimal('99.99')
        )

        orders.append(order)

    print(f"  Created {len(orders)} pending orders")
    return product, orders


def simulate_payment(thread_id, order_id, product_id, result):
    """模拟支付请求"""
    try:
        with transaction.atomic():
            # 锁定订单
            order = OrderInfo.objects.select_for_update().get(id=order_id)

            if order.pay_status != "PAYING":
                result.add_failure()
                return

            # 获取订单商品
            order_goods = order.goods.all()

            for item in order_goods:
                # F表达式原子更新库存
                updated = Product.objects.filter(
                    id=product_id,
                    goods_num__gte=item.goods_num
                ).update(
                    goods_num=F('goods_num') - item.goods_num,
                    sold_num=F('sold_num') + item.goods_num
                )

                if not updated:
                    result.add_failure()
                    return

            # 更新订单状态
            from django.utils import timezone
            order.pay_status = "TRADE_SUCCESS"
            order.pay_time = timezone.now()
            order.save()

            result.add_success()

    except Exception:
        result.add_failure()


def run_test(product, orders):
    """运行并发测试"""
    print("\n" + "="*60)
    print("[Step 2] Run Concurrency Test (50 threads)")
    print("="*60)

    result = ConcurrencyTestResult()
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = []
        for i in range(50):
            order = orders[i % len(orders)]
            futures.append(executor.submit(simulate_payment, i, order.id, product.id, result))

        for future in as_completed(futures):
            pass

    elapsed = time.time() - start_time
    print(f"  Completed in {elapsed:.2f}s")
    return result


def verify_results(product, result):
    """验证结果"""
    print("\n" + "="*60)
    print("[Step 3] Verify Results")
    print("="*60)

    product.refresh_from_db()

    success_orders = OrderInfo.objects.filter(
        pay_status="TRADE_SUCCESS",
        order_sn__startswith="CONC_TEST"
    ).count()

    print(f"\n  Request Stats:")
    print(f"    Total: {result.success_count + result.failure_count}")
    print(f"    Success: {result.success_count}")
    print(f"    Failed: {result.failure_count}")

    print(f"\n  Stock Verification:")
    print(f"    Initial: 10")
    print(f"    Final: {product.goods_num}")
    print(f"    Sold: {product.sold_num}")

    print(f"\n  Data Consistency:")
    print(f"    Successful Orders: {success_orders}")
    print(f"    Stock Deducted: {10 - product.goods_num}")

    print("\n" + "="*60)
    print("[Step 4] Test Conclusions")
    print("="*60)

    all_passed = True

    # 检查1: 库存非负
    if product.goods_num >= 0:
        print(f"  [PASS] Stock >= 0: {product.goods_num}")
    else:
        print(f"  [FAIL] Stock < 0: {product.goods_num} (OVERSOLD!)")
        all_passed = False

    # 检查2: 数据一致性
    deducted = 10 - product.goods_num
    if deducted == success_orders:
        print(f"  [PASS] Consistency: deducted({deducted}) == orders({success_orders})")
    else:
        print(f"  [FAIL] Inconsistency: deducted({deducted}) != orders({success_orders})")
        all_passed = False

    # 检查3: 无超卖
    if success_orders <= 10:
        print(f"  [PASS] No Oversell: orders({success_orders}) <= initial(10)")
    else:
        print(f"  [FAIL] Oversell: orders({success_orders}) > initial(10)")
        all_passed = False

    # 检查4: 销量一致
    if product.sold_num == success_orders:
        print(f"  [PASS] Sold Count: {product.sold_num} == {success_orders}")
    else:
        print(f"  [FAIL] Sold Mismatch: {product.sold_num} != {success_orders}")
        all_passed = False

    print("\n" + "="*60)
    if all_passed:
        print(">>> ALL CHECKS PASSED! Anti-oversell verified! <<<")
    else:
        print("!!! SOME CHECKS FAILED! <<<")
    print("="*60)

    return all_passed


def cleanup():
    """清理测试数据"""
    print("\n" + "="*60)
    print("[Step 5] Cleanup")
    print("="*60)

    OrderGoods.objects.filter(order__order_sn__startswith="CONC_TEST").delete()
    OrderInfo.objects.filter(order_sn__startswith="CONC_TEST").delete()
    User.objects.filter(username__startswith="conc_test_").delete()
    Product.objects.filter(name="Concurrent Test Product").delete()
    Category.objects.filter(name="Concurrent Test Category").delete()

    print("  Cleanup completed")


def main():
    print("\n" + "="*60)
    print("  Concurrency Stock Test - Anti-Oversell Verification")
    print("="*60)
    print("\nTest Scenario:")
    print("  - Initial Stock: 10")
    print("  - Pending Orders: 20 (each order buys 1)")
    print("  - Concurrent Requests: 50")
    print("  - Expected: Max 10 orders succeed, final stock = 0")

    try:
        product, orders = setup_test_data()
        result = run_test(product, orders)
        all_passed = verify_results(product, result)
        cleanup()
        sys.exit(0 if all_passed else 1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
