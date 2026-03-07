# @Version  :1.0
# @Author   :crist
# @File     :serializers.py.py
import re
from rest_framework import serializers
from django.contrib.auth import get_user_model

# 获取自定义的 UserProfile 模型
User = get_user_model()

class UserRegSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
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
    后台管理系统获取用户列表的序列化器
    """
    class Meta:
        model = User
        fields = ("id", "username", "mobile", "email", "is_active", "date_joined")
