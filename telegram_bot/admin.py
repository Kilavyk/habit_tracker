from django.contrib import admin
from .models import TelegramUser

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'chat_id', 'telegram_username']
    list_filter = ['user']
    search_fields = ['user__username', 'telegram_username']
