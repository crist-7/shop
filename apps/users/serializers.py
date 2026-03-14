# @Version  :2.0
# @Author   :crist
# @File     :serializers.py
# @Desc     :用户相关序列化器（注册、详情、修改密码）

import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

# 获取自定义的 UserProfile 模型
User = get_user_model()


class UserRegSerializer(serializers.ModelSerializer):
    """
    用户注册序列化器

    功能：
    - 接收用户名、手机号、密码
    - 自动加密密码存储
    - 验证手机号格式和唯一性
    """
    # 将密码设置为 write_only，确保它只用于接收，永远不会在 API 响应中返回给前端
    password = serializers.CharField(
        style={'input_type': 'password'},
        help_text="密码",
        label="密码",
        write_only=True,
        min_length=6,
        error_messages={
            "min_length": "密码长度不能小于 6 位",
            "required": "请填写密码",
            "blank": "密码不能为空"
        }
    )

    class Meta:
        model = User
        fields = ("username", "mobile", "password")

    def validate_mobile(self, mobile):
        """局部钩子：验证手机号码格式与唯一性"""
        if not re.match(r"^1[3-9]\d{9}$", mobile):
            raise serializers.ValidationError("手机号码格式非法")
        if User.objects.filter(mobile=mobile).exists():
            raise serializers.ValidationError("该手机号已经被注册")
        return mobile

    def create(self, validated_data):
        """全局钩子：重写 create 方法，确保密码被加密保存"""
        user = super(UserRegSerializer, self).create(validated_data)
        # 核心：将明文密码转换为密文
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详情序列化器

    功能：
    - 用于获取用户列表和详情
    - 只返回安全的字段，不包含密码
    """
    class Meta:
        model = User
        fields = ("id", "username", "mobile", "email", "is_active", "date_joined")
        read_only_fields = ("id", "date_joined")


class ChangePasswordSerializer(serializers.Serializer):
    """
    修改密码序列化器

    功能：
    - 验证旧密码是否正确
    - 验证新密码格式和复杂度
    - 验证两次输入的新密码是否一致

    安全设计：
    - 所有字段设置为 write_only，确保密码不会在响应中返回
    - 使用 Django 内置的密码验证器检查密码强度
    """

    # 原密码
    old_password = serializers.CharField(
        style={'input_type': 'password'},
        help_text="原密码",
        label="原密码",
        write_only=True,
        error_messages={
            "required": "请输入原密码",
            "blank": "原密码不能为空"
        }
    )

    # 新密码
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        help_text="新密码",
        label="新密码",
        write_only=True,
        min_length=6,
        error_messages={
            "min_length": "新密码长度不能小于 6 位",
            "required": "请输入新密码",
            "blank": "新密码不能为空"
        }
    )

    # 确认密码
    confirm_password = serializers.CharField(
        style={'input_type': 'password'},
        help_text="确认密码",
        label="确认密码",
        write_only=True,
        min_length=6,
        error_messages={
            "min_length": "确认密码长度不能小于 6 位",
            "required": "请输入确认密码",
            "blank": "确认密码不能为空"
        }
    )

    def validate_old_password(self, value):
        """
        局部钩子：验证原密码是否正确

        原理：
        - 从 context 中获取当前用户对象
        - 使用 Django 的 check_password 方法验证密码
        """
        user = self.context.get('user')
        if not user:
            raise serializers.ValidationError("无法获取当前用户信息")

        if not user.check_password(value):
            raise serializers.ValidationError("原密码错误")

        return value

    def validate_new_password(self, value):
        """
        局部钩子：验证新密码复杂度

        原理：
        - 使用 Django 内置的密码验证器
        - 检查密码长度、常见密码、数字密码、相似性等
        """
        try:
            # 使用 Django 的密码验证器（在 settings.AUTH_PASSWORD_VALIDATORS 中配置）
            validate_password(value)
        except Exception as e:
            # 将验证错误转换为序列化器错误
            raise serializers.ValidationError(str(e))

        return value

    def validate(self, attrs):
        """
        全局钩子：跨字段验证

        验证逻辑：
        1. 新密码与确认密码必须一致
        2. 新密码不能与原密码相同（防止用户未实际修改密码）
        """
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        old_password = attrs.get('old_password')

        # 验证1：新密码与确认密码一致
        if new_password != confirm_password:
            raise serializers.ValidationError({
                "confirm_password": "两次输入的新密码不一致"
            })

        # 验证2：新密码不能与原密码相同
        if new_password == old_password:
            raise serializers.ValidationError({
                "new_password": "新密码不能与原密码相同"
            })

        return attrs

    def save(self, **kwargs):
        """
        保存新密码

        原理：
        - 从 context 获取用户对象
        - 使用 set_password 方法加密存储新密码
        """
        user = self.context.get('user')
        if not user:
            raise serializers.ValidationError("无法获取当前用户信息")

        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()

        return user
