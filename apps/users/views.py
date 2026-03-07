from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserRegSerializer, UserDetailSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    用户管理
    """
    queryset = User.objects.all().order_by('-date_joined')
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action == "create":
            return UserRegSerializer
        return UserDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        refresh = RefreshToken.for_user(user)
        re_dict = serializer.data
        re_dict["token"] = str(refresh.access_token)
        re_dict["refresh"] = str(refresh)
        re_dict["name"] = user.username
        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save()
