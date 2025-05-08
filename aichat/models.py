from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    telegram_chat_id = models.CharField(max_length=50, blank=True, null=True)
    # Добавляем related_name для разрешения конфликтов
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to.'),
        related_name='aichat_user_set',
        related_query_name='aichat_user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='aichat_user_set',
        related_query_name='aichat_user',
    )

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')


class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-updated_at']


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField()
    is_user_message = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_ai_generated = models.BooleanField(default=False)
    sources = models.JSONField(default=list, blank=True)
    # sources = models.JSONField(blank=True, null=True)  # Для хранения источников информации

    class Meta:
        ordering = ['created_at']


class KnowledgeBase(models.Model):
    question_pattern = models.TextField()
    answer = models.TextField()
    sources = models.JSONField(blank=True, null=True)
    confidence_score = models.FloatField(default=0.0)
    last_used = models.DateTimeField(auto_now=True)
    usage_count = models.IntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['question_pattern']),
        ]


class SystemSettings(models.Model):
    name = models.CharField(max_length=100, unique=True)
    value = models.JSONField()
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name