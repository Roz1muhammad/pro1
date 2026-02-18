from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .models.user_models import User, Otp
from .user_serializer import RegisterSerializer, OtpVerifySerializer, LoginSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
import random
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from .models.product_models import Product
from .user_serializer import ProductSerializer
from .permissions import IsOwner

# =============================
# REGISTER API
# =============================
class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Faqat temp user yaratiladi (bazaga saqlanmaydi)
        temp_user = serializer.create_temp_user(serializer.validated_data)

        # OTP yaratish
        otp_code = str(random.randint(100000, 999999))
        otp = Otp.objects.create(code=otp_code)

        # Session yoki cache-ga saqlaymiz
        request.session['temp_user_data'] = {
            **serializer.validated_data,
            'password': temp_user.password  # xeshlangan parol
        }

        # Response-da OTPni yuborish (dev/testing uchun)
        return Response({
            'detail': 'Sizning emailingizga OTP jo‘natildi',
            'otp': otp.code
        }, status=201)

# =============================
# OTP VERIFY API
# =============================
class OtpVerifyAPIView(APIView):
    def post(self, request):
        serializer = OtpVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        temp_data = request.session.get('temp_user_data')
        if not temp_data or temp_data['email'] != email:
            return Response({'detail': 'Bunday user mavjud emas'}, status=404)

        try:
            otp = Otp.objects.filter(is_used=False).latest('created')
        except Otp.DoesNotExist:
            return Response({'detail': 'Noto‘g‘ri OTP'}, status=400)

        if otp.is_expired():
            return Response({'detail': 'OTP muddati o‘tgan'}, status=400)

        if otp.tries >= 3:
            return Response({'detail': 'Siz 3 urinishni tugatdingiz, OTP endi ishlamaydi'}, status=400)

        otp.tries += 1
        otp.save()

        if otp.code != code:
            return Response({'detail': 'Noto‘g‘ri OTP'}, status=400)

        # OTP to‘g‘ri → userni bazaga saqlaymiz
        user = User(**temp_data)
        user.is_active = True
        user.is_verified = True
        user.save()

        otp.user = user
        otp.is_used = True
        otp.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            'detail': 'Siz ro‘yxatdan o‘tdingiz',
            'user': {
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'region': user.region,
                'birth_year': user.birth_year,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })

# =============================
# LOGIN API
# =============================
class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(username=username, password=password)
        if not user:
            return Response({'detail': 'Username yoki parol noto‘g‘ri'}, status=400)

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': {
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'region': user.region,
                'birth_year': user.birth_year,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })

# =============================
# LOGOUT API
# =============================
class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({'detail': 'Refresh token kiritilmagan'}, status=400)

        try:
            token = RefreshToken(refresh_token)
        except Exception:
            return Response({'detail': 'Refresh token topilmadi'}, status=400)

        try:
            token.blacklist()
        except Exception:
            pass

        # Userni o‘chirib tashlaymiz
        user = request.user
        user.delete()

        # Development/testing uchun OTP
        otp_code = str(random.randint(100000, 999999))

        return Response({
            'detail': 'Siz muvaffaqiyatli logout qildingiz va user bazadan o‘chirildi',
            'otp': otp_code
        }, status=200)

# =============================
# PRODUCT CRUD
# =============================
class ProductCreateAPIView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}

class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductUpdateAPIView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_serializer_context(self):
        return {'request': self.request}

class ProductDeleteAPIView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'detail': 'Mahsulot o‘chirildi ✅'},
            status=status.HTTP_200_OK
        )
