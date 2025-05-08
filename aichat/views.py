import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.views.generic import ListView, DeleteView
from django.urls import reverse_lazy
from .models import Conversation, Message
from django.contrib.auth.models import User
from .machine_learning.model_manager import AIModelManager
from .machine_learning.response_handler import ResponseHandler

logger = logging.getLogger(__name__)

class ConversationDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление беседы пользователя."""
    model = Conversation
    template_name = 'aichat/admin/confirm_delete.html'
    success_url = reverse_lazy('conversations')

    def get_queryset(self):
        """Возвращает только чаты текущего пользователя."""
        return Conversation.objects.filter(user=self.request.user)

class ConversationListView(LoginRequiredMixin, ListView):
    """Список всех чатов пользователя."""
    model = Conversation
    template_name = 'aichat/admin/conversations.html'
    context_object_name = 'conversations'

    def get_queryset(self):
        """Возвращает только чаты, принадлежащие текущему пользователю."""
        return Conversation.objects.filter(user=self.request.user).order_by('-created_at')

@csrf_exempt
def handle_response(request):
    """Обработчик для API ответа."""
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            user_input = data.get("user_input", "")
            if not user_input:
                return JsonResponse({"success": False, "error": "Отсутствует пользовательский ввод"}, status=400)

            response_handler = ResponseHandler()
            response = response_handler.process_input(user_input)
            return JsonResponse({"success": True, "response": response})
        else:
            return JsonResponse({"success": False, "error": "Только POST-запросы разрешены"}, status=405)
    except Exception as e:
        logger.error(f"Error in handle_response: {str(e)}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)

def home(request):
    """Главная страница, доступная всем."""
    return render(request, 'aichat/home.html')

def user_login(request):
    """Кастомное представление для входа."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')

    return render(request, 'aichat/login.html')

@login_required
def user_logout(request):
    """Выход пользователя."""
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    """Панель управления."""
    try:
        conversations = Conversation.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'aichat/admin/dashboard.html', {'conversations': conversations})
    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        messages.error(request, "Не удалось загрузить панель управления")
        return redirect('home')

@login_required
def new_chat(request):
    """Создание нового чата."""
    try:
        conversation = Conversation.objects.create(user=request.user)
        return redirect('chat_detail', conversation_id=conversation.id)
    except Exception as e:
        logger.error(f"Error creating new chat: {str(e)}")
        messages.error(request, "Не удалось создать новый чат")
        return redirect('dashboard')

@login_required
def chat(request, conversation_id):
    """Просмотр конкретного чата."""
    try:
        conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
        messages = conversation.messages.all().order_by('created_at')
        return render(request, 'aichat/admin/chat.html', {
            'conversation': conversation,
            'messages': messages
        })
    except Exception as e:
        logger.error(f"Error loading chat {conversation_id}: {str(e)}")
        messages.error(request, "Не удалось загрузить чат")
        return redirect('dashboard')

@require_http_methods(["POST"])
@login_required
@csrf_exempt
def send_message(request, conversation_id):
    """Отправка сообщения."""
    try:
        conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
        data = json.loads(request.body) if request.body else {}
        message_text = data.get('text', '').strip()
        if not message_text:
            return JsonResponse({'success': False, 'error': 'Сообщение не может быть пустым'}, status=400)

        # Проверка на дублирование сообщения
        if Message.objects.filter(conversation=conversation, text=message_text, is_user_message=True).exists():
            return JsonResponse({'success': False, 'error': 'Сообщение уже существует'}, status=400)

        logger.debug(f"Sending message: {message_text} in conversation {conversation_id}")

        # Используем транзакцию для атомарного сохранения
        with transaction.atomic():
            # Сохранение сообщения пользователя
            user_message = Message.objects.create(
                conversation=conversation,
                text=message_text,
                is_user_message=True
            )

            # Обработка сообщения через AIModelManager
            ai_manager = AIModelManager()
            response = ai_manager.process_message(message_text, request.user, conversation_id)

            if not response['success']:
                raise Exception(response.get('error', 'Ошибка обработки сообщения'))

            # Сохранение ответа ИИ
            ai_message = Message.objects.create(
                conversation=conversation,
                text=response['answer'],
                is_user_message=False,
                is_ai_generated=True,
                sources=response.get('sources', [])
            )

        return JsonResponse({
            'success': True,
            'user_message': {
                'id': user_message.id,
                'text': user_message.text,
                'created_at': user_message.created_at.isoformat(),
                'is_user_message': user_message.is_user_message
            },
            'ai_message': {
                'id': ai_message.id,
                'text': ai_message.text,
                'sources': ai_message.sources,
                'created_at': ai_message.created_at.isoformat(),
                'is_user_message': ai_message.is_user_message
            }
        })
    except Exception as e:
        logger.error(f"Error in send_message for conversation {conversation_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Произошла ошибка при отправке сообщения'
        }, status=500)

@login_required
def get_messages(request, conversation_id):
    """Получение сообщений."""
    try:
        conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
        since_id = request.GET.get('since_id', 0)
        messages = conversation.messages.filter(id__gt=since_id).order_by('created_at').values(
            'id', 'text', 'is_user_message', 'created_at', 'sources'
        )
        logger.debug(f"Retrieved {len(messages)} messages for conversation {conversation_id} since_id={since_id}")
        return JsonResponse({
            'success': True,
            'messages': list(messages)
        })
    except Exception as e:
        logger.error(f"Error getting messages for conversation {conversation_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Не удалось загрузить сообщения'
        }, status=500)

@login_required
def user_list(request):
    """Список пользователей."""
    try:
        users = User.objects.all().order_by('username')
        return render(request, 'aichat/admin/users.html', {'users': users})
    except Exception as e:
        logger.error(f"Error loading user list: {str(e)}")
        messages.error(request, "Не удалось загрузить список пользователей")
        return redirect('dashboard')