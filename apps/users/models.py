from django.db import models
from django.contrib.auth.models import AbstractUser

class UserProfile(AbstractUser):
    """
    自定义用户模型：继承默认的 AbstractUser，增加商城所需的额外字段
    """
    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号码", null=True, blank=True)
    avatar = models.ImageField(upload_to="avatar/image/%Y/%m", default="default_avatar.png", verbose_name="头像", null=True, blank=True)

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username