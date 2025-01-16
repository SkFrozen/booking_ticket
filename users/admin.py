from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.urls import path
from django.utils.html import format_html

from .models import User


class CacheAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "is_staff", "is_active")
    list_display_links = ("id", "username")
    list_filter = ("is_staff", "is_active")
    search_fields = ("username", "email")
    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active")}),
    )

    change_list_template = "admin/clear_cache.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "clear-cache/",
                self.admin_site.admin_view(self.clear_cache),
                name="clear-cache",
            ),
        ]
        return custom_urls + urls

    def clear_cache(self, request):
        cache.clear()  # Очистка кеша
        self.message_user(request, "Кеш успешно очищен!")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


@admin.register(User)
class UserAdmin(CacheAdmin):
    pass
