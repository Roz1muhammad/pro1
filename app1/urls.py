from django.urls import path
from .views import RegisterAPIView, OtpVerifyAPIView, LoginAPIView, LogoutAPIView
from app1.views import (
    ProductCreateAPIView,
    ProductListAPIView,
    ProductDetailAPIView,
    ProductUpdateAPIView,
    ProductDeleteAPIView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('otp-verify/', OtpVerifyAPIView.as_view(), name='otp-verify'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
###############################################################################
    path('products/', ProductListAPIView.as_view()),
    path('products/create/', ProductCreateAPIView.as_view()),
    path('products/<int:pk>/', ProductDetailAPIView.as_view()),
    path('products/<int:pk>/update/', ProductUpdateAPIView.as_view()),
    path('products/<int:pk>/delete/', ProductDeleteAPIView.as_view()),

##################################################################################
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
