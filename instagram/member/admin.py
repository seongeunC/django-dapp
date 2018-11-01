from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import SignupForm

User = get_user_model()


class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('추가 정보', {'fields': ('wallet_address','img_profile', 'gender', 'user_classification','like_posts')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('추가 정보', {
            'fields': ('wallet_address','img_profile', 'gender', 'user_classification','like_posts'),
        }),
    )
    add_form = SignupForm


admin.site.register(User, UserAdmin)
