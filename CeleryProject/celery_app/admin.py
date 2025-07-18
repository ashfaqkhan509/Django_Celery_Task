from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Order, UserProfile


class CustomUserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2"),
        }),
    )

    list_display = ("username", "email", "first_name", "last_name", "is_staff")

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("user", "product_name", "price", "created_at")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "image", "created_at")