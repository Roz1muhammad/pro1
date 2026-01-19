from django.db import models
from django.conf import settings
from app1.validators import validate_image_size

class Product(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,   # ✅ TO‘G‘RI JOY
        on_delete=models.CASCADE,
        related_name='products'
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        upload_to='products/',
        validators=[validate_image_size]
    )
