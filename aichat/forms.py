from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Conversation, Message  # Все модели в одном импорте


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'telegram_chat_id')


class ConversationForm(forms.ModelForm):
    class Meta:
        model = Conversation
        fields = ('title',)
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название беседы...'
            }),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Введите ваше сообщение...'
            }),
        }