"""
自定义 CSRF 失败处理视图
用于前后端分离架构，返回 JSON 格式错误信息，而不是 HTML 页面
"""
from django.http import JsonResponse


def csrf_failure(request, reason=""):
    """
    自定义 CSRF 验证失败处理视图
    返回 JSON 格式错误响应，便于前端 Vue.js 应用友好处理

    :param request: HTTP 请求对象
    :param reason: 失败原因字符串
    :return: JsonResponse 包含错误详情
    """
    # 构建 JSON 响应数据，返回简洁的错误信息
    response_data = {
        "detail": "CSRF校验失败"
    }

    # 设置响应头
    headers = {
        'Content-Type': 'application/json',
        'X-CSRF-Required': 'true',
    }

    return JsonResponse(response_data, status=403, headers=headers)