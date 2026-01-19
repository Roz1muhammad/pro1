from django.core.exceptions import ValidationError

def validate_image_size(image):
    max_size = 10 * 1024 * 1024  # 10 MB
    if image.size > max_size:
        raise ValidationError("Rasm hajmi 10 MB dan oshmasligi kerak.")
