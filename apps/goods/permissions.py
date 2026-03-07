from rest_framework import permissions


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    自定义权限校验：
    - 允许所有人进行只读操作 (GET, HEAD, OPTIONS)
    - 仅允许后台管理员进行写操作 (POST, PUT, PATCH, DELETE)
    """

    def has_permission(self, request, view):
        # 1. 如果是安全的方法（只读，不修改数据库），直接放行
        if request.method in permissions.SAFE_METHODS:
            return True

        # 2. 如果是危险的方法（增删改），必须要求用户已登录，且是管理员 (is_staff)
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)