from rest_framework import serializers
from .models.user_models import User

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'full_name', 'region', 'birth_year', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create_temp_user(self, validated_data):
        """
        Faqat parolni xesh qiladi va temp user ma’lumotini qaytaradi,
        lekin bazaga saqlamaydi
        """
        password = validated_data.pop('password')
        temp_user = User(**validated_data)
        temp_user.set_password(password)
        return temp_user


class OtpVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


from rest_framework import serializers
from .models.product_models import Product, ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']


from rest_framework import serializers
from .models.product_models import Product, ProductImage

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'images', 'created_at']

    def create(self, validated_data):
        images_data = self.context['request'].FILES.getlist('images')  # <--- fayllar shu yerda olinadi
        user = self.context['request'].user

        product = Product.objects.create(owner=user, **validated_data)

        for image in images_data:
            ProductImage.objects.create(product=product, image=image)
        return product

    def update(self, instance, validated_data):
        images_data = self.context['request'].FILES.getlist('images')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if images_data:
            instance.images.all().delete()
            for image in images_data:
                ProductImage.objects.create(product=instance, image=image)

        return instance

