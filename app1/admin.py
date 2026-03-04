# app1/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models.user_models import User, Otp

# ==========================================
# User admin
# ==========================================
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('username', 'email', 'full_name', 'phone', 'region', 'birth_year', 'is_verified', 'is_active', 'is_staff')
    list_filter = ('region', 'is_verified', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone', 'full_name')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'phone', 'region', 'birth_year')}),
        ('Permissions', {'fields': ('is_verified', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'full_name', 'phone', 'region', 'birth_year', 'is_verified', 'is_active', 'is_staff')}
        ),
    )


# ==========================================
# OTP admin
# ==========================================
@admin.register(Otp)
class OtpAdmin(admin.ModelAdmin):

    list_filter = ('is_used', 'created')
    search_fields = ('user__username', 'user__email')


from django.contrib import admin
from .models import Product, ProductImage


# ==========================
# ProductImage Inline
# ==========================
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # nechta bo'sh rasm qo'shish joyi chiqsin
    readonly_fields = ()
    fields = ("image",)


# ==========================
# Product Admin
# ==========================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "owner",
        "price",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "name",
        "description",
        "owner__username",
    )

    ordering = ("-created_at",)

    inlines = [ProductImageInline]


# ==========================
# ProductImage Admin (alohida ham ko‘rish uchun)
# ==========================
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "image",
    )

    search_fields = (
        "product__name",
    )



#test
