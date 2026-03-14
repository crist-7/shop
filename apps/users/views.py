# @Version  :2.0
# @Author   :crist
# @File     :views.py
# @Desc     :用户管理视图集（注册、详情、修改密码、获取当前用户信息）

from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    UserRegSerializer,
    UserDetailSerializer,
    ChangePasswordSerializer
)
from .tasks import send_welcome_email_task

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    用户管理视图集

    功能：
    - 用户注册（POST /api/users/）
    - 用户列表/详情（GET /api/users/）
    - 修改密码（POST /api/users/change_password/）
    - 获取当前用户信息（GET /api/users/info/）
    """
    queryset = User.objects.all().order_by('-date_joined')

    def get_permissions(self):
        """
        权限控制

        规则：
        - create（注册）：允许匿名访问
        - 其他所有操作：需要认证
        """
        if self.action == 'create':
            return (AllowAny(),)
        return (IsAuthenticated(),)

    def get_serializer_class(self):
        """
        序列化器选择

        规则：
        - create（注册）：使用 UserRegSerializer
        - change_password：使用 ChangePasswordSerializer
        - 其他：使用 UserDetailSerializer
        """
        if self.action == "create":
            return UserRegSerializer
        if self.action == "change_password":
            return ChangePasswordSerializer
        return UserDetailSerializer

    def create(self, request, *args, **kwargs):
        """
        用户注册接口

        响应：
        - 用户基本信息
        - JWT access token
        - JWT refresh token
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        # 生成 JWT Token
        refresh = RefreshToken.for_user(user)

        re_dict = serializer.data
        re_dict["token"] = str(refresh.access_token)
        re_dict["refresh"] = str(refresh)
        re_dict["name"] = user.username

        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        """创建用户时异步发送欢迎邮件"""
        user = serializer.save()
        # 异步发送欢迎邮件
        send_welcome_email_task.apply_async(args=[user.id])
        return user

    def get_queryset(self):
        """
        查询集过滤

        规则：
        - 管理员：可查看所有用户
        - 普通用户：只能查看自己的信息
        """
        user = self.request.user
        if user.is_staff:
            return User.objects.all().order_by('-date_joined')
        return User.objects.filter(id=user.id).order_by('-date_joined')

    # ============================================================
    # 自定义路由：修改密码
    # ============================================================
    @action(
        methods=['POST'],
        detail=False,
        url_path='change_password',
        url_name='change-password'
    )
    def change_password(self, request):
        """
        修改密码接口

        路由: POST /api/users/change_password/

        请求体:
        {
            "old_password": "原密码",
            "new_password": "新密码",
            "confirm_password": "确认新密码"
        }

        响应:
        {
            "message": "密码修改成功"
        }

        安全说明：
        - 需要用户已登录（IsAuthenticated）
        - 原密码验证通过后才能修改
        - 新密码会自动加密存储
        """
        serializer = self.get_serializer(
            data=request.data,
            context={'user': request.user}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "密码修改成功"
        }, status=status.HTTP_200_OK)

    # ============================================================
    # 自定义路由：获取当前用户信息
    # ============================================================
    @action(
        methods=['GET'],
        detail=False,
        url_path='info',
        url_name='user-info'
    )
    def info(self, request):
        """
        获取当前登录用户信息

        路由: GET /api/users/info/

        响应:
        {
            "id": 1,
            "username": "admin",
            "mobile": "13800138000",
            "email": "admin@example.com",
            "is_active": true,
            "date_joined": "2024-01-01T00:00:00Z"
        }

        用途：
        - 前端个人中心页面展示
        - 避免前端需要先获取用户 ID 再请求详情的两步操作
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
