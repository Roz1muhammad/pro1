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

        validated_data = serializer.validated_data.copy()
        email = validated_data.pop('email').strip().lower()
        password = validated_data.pop('password')

        # User yaratish
        user = User.objects.create(
            is_active=False,
            email=email,
            **validated_data
        )
        user.set_password(password)
        user.save()

        # OTP yaratish (faqat email bilan)
        otp_code = str(random.randint(100000, 999999))
        otp = Otp.objects.create(email=email, code=otp_code)

        print(f"📤 OTP Data being sent: {{email: {email}, code: {otp_code}}}")

        return Response({
            'detail': 'Sizning emailingizga OTP jo‘natildi',
            'otp': otp_code  # faqat dev/testing
        }, status=201)


# =============================
# OTP VERIFY API
# =============================
class OtpVerifyAPIView(APIView):
    def post(self, request):
        serializer = OtpVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email'].strip().lower()
        code = serializer.validated_data['code']

        # Userni olish
        try:
            user = User.objects.get(email__iexact=email, is_active=False)
        except User.DoesNotExist:
            return Response({'detail': 'Bunday user mavjud emas'}, status=404)

        # Oxirgi ishlatilmagan OTPni olish
        try:
            otp = Otp.objects.filter(email__iexact=email, is_used=False).latest('created')
        except Otp.DoesNotExist:
            return Response({'detail': 'Noto‘g‘ri OTP'}, status=400)

        # OTP muddati tekshirish
        if otp.is_expired():
            return Response({'detail': 'OTP muddati o‘tgan'}, status=400)

        # Maksimal urinishlar
        if otp.tries >= 3:
            return Response({'detail': 'Siz 3 urinishni tugatdingiz, OTP endi ishlamaydi'}, status=400)

        otp.tries += 1
        otp.save()

        if otp.code != code:
            return Response({'detail': 'Noto‘g‘ri OTP'}, status=400)

        # User faollashtirish
        user.is_active = True
        user.is_verified = True
        user.save()

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
        }, status=200)


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
