from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.static import serve
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from goods.views import ProductViewSet, CategoryViewSet, BannerViewSet,ImageUploadView
from users.views import UserViewSet
from trade.views import ShoppingCartViewSet, OrderViewSet, DashboardSummaryView




router = DefaultRouter()
router.register(r'goods', ProductViewSet, basename="goods")
# 3. 【新增】注册用户模块路由
router.register(r'users', UserViewSet, basename="users")
router.register(r'shopcarts', ShoppingCartViewSet, basename="shopcarts")
router.register(r'orders', OrderViewSet, basename="orders")
router.register(r'category', CategoryViewSet, basename="category")
router.register(r'banners', BannerViewSet, basename="banners")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
    path('api/', include(router.urls)),

    # 4. 【新增】配置 JWT 登录认证接口
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/upload/', ImageUploadView.as_view(), name='image-upload'),
    path('api/dashboard/summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)