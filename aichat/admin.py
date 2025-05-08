from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Conversation, Message, KnowledgeBase, SystemSettings
from django.utils.translation import gettext_lazy as _


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'telegram_chat_id')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')


admin.site.register(User, CustomUserAdmin)

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'created_at', 'updated_at')
    list_filter = ('user',)
    search_fields = ('title', 'user__username')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'truncated_text', 'is_user_message', 'created_at')
    list_filter = ('conversation__user', 'is_user_message')

    def truncated_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text

    truncated_text.short_description = 'Text'


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ('truncated_question', 'truncated_answer', 'confidence_score', 'last_used', 'usage_count')
    search_fields = ('question_pattern', 'answer')
    list_filter = ('confidence_score',)

    def truncated_question(self, obj):
        return obj.question_pattern[:50] + '...' if len(obj.question_pattern) > 50 else obj.question_pattern

    truncated_question.short_description = 'Question'

    def truncated_answer(self, obj):
        return obj.answer[:50] + '...' if len(obj.answer) > 50 else obj.answer

    truncated_answer.short_description = 'Answer'


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')