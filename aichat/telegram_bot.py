import logging
import signal
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from django.conf import settings
from asgiref.sync import sync_to_async
from django.db import transaction
from aichat.models import User, Conversation, Message
from aichat.machine_learning.model_manager import AIModelManager
from functools import partial

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize the AI model manager
ai_manager = AIModelManager()

# Cache for processed message IDs to prevent duplicates
processed_message_ids = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, ai_manager: AIModelManager) -> None:
    """Обработчик команды /start."""
    user = update.effective_user
    telegram_chat_id = str(update.effective_chat.id)

    logger.info(f"Received /start command from chat_id: {telegram_chat_id}")

    try:
        django_user = await sync_to_async(User.objects.get)(telegram_chat_id=telegram_chat_id)
        welcome_message = (
            f"Привет, {django_user.first_name or django_user.username}!\n"
            "Я - AIchat, ваш интеллектуальный помощник. "
            "Задайте мне вопрос, и я постараюсь на него ответить."
        )
    except User.DoesNotExist:
        welcome_message = (
            "Привет! Я - AIchat, интеллектуальный помощник.\n"
            "К сожалению, у вас нет доступа к системе. "
            "Обратитесь к администратору для получения доступа.\n"
            f"Ваш chat_id: {telegram_chat_id} (передайте его администратору)"
        )

    await update.message.reply_text(welcome_message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE, ai_manager: AIModelManager) -> None:
    """Обработчик текстовых сообщений."""
    telegram_chat_id = str(update.effective_chat.id)
    message_text = update.message.text
    message_id = update.message.message_id

    if not message_text.strip():
        await update.message.reply_text("Пожалуйста, введите сообщение.")
        return

    logger.info(f"Received message from chat_id {telegram_chat_id}, message_id {message_id}: {message_text}")

    # Проверяем, не было ли сообщение уже обработано
    if message_id in processed_message_ids:
        logger.warning(f"Duplicate message_id {message_id} from chat_id {telegram_chat_id}, ignoring")
        return
    processed_message_ids.add(message_id)

    try:
        # Находим пользователя
        user = await sync_to_async(User.objects.select_related().get)(telegram_chat_id=telegram_chat_id)

        # Создаем или находим беседу
        conversation, created = await sync_to_async(
            Conversation.objects.get_or_create
        )(user=user, title=f"Telegram Chat {telegram_chat_id}")

        # Проверяем на дублирование сообщения
        if await sync_to_async(Message.objects.filter)(
            conversation=conversation,
            text=message_text,
            is_user_message=True
        ).exists():
            logger.warning(f"Duplicate message text '{message_text}' in conversation {conversation.id}, ignoring")
            await update.message.reply_text("Это сообщение уже было отправлено. Попробуйте другой запрос.")
            return

        # Используем транзакцию для атомарного сохранения
        async with transaction.atomic():
            # Сохранение сообщения пользователя
            user_message = await sync_to_async(Message.objects.create)(
                conversation=conversation,
                text=message_text,
                is_user_message=True
            )

            # Обрабатываем сообщение через AIModelManager
            response = await sync_to_async(ai_manager.process_message)(
                message_text=message_text,
                user=user,
                conversation_id=conversation.id
            )

            if not response['success']:
                raise ValueError(response.get('error', 'Failed to process message'))

            # Сохранение ответа ИИ
            ai_message = await sync_to_async(Message.objects.create)(
                conversation=conversation,
                text=response['answer'],
                is_user_message=False,
                is_ai_generated=True,
                sources=response.get('sources', [])
            )

        # Формируем ответ
        final_message = response['answer']
        if response.get('sources'):
            sources_text = "\n\nИсточники:\n" + "\n".join(
                f"- {source['text']} ({source['url']})" for source in response['sources'] if source.get('url')
            )
            final_message += sources_text

        logger.debug(f"Sending response to chat_id {telegram_chat_id}, conversation {conversation.id}: {final_message}")
        await update.message.reply_text(final_message)

    except User.DoesNotExist:
        await update.message.reply_text(
            f"У вас нет доступа к системе. Обратитесь к администратору.\n"
            f"Ваш chat_id: {telegram_chat_id} (передайте его администратору)"
        )
    except Exception as e:
        logger.exception(f"Error processing message for chat_id {telegram_chat_id}, message_id {message_id}: {str(e)}")
        await update.message.reply_text(
            "Произошла ошибка при обработке вашего сообщения. Пожалуйста, попробуйте позже."
        )

def setup_telegram_bot():
    """Инициализация и запуск Telegram бота."""
    bot_token = settings.TELEGRAM_BOT_TOKEN
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN is not set in settings")
        raise ValueError("TELEGRAM_BOT_TOKEN is not set")

    ai_manager = AIModelManager()
    application = Application.builder().token(bot_token).build()

    application.add_handler(CommandHandler('start', partial(start, ai_manager=ai_manager)))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, partial(handle_message, ai_manager=ai_manager)))

    def handle_shutdown(signal, frame, app):
        logger.info("Received shutdown signal, stopping bot...")
        app.stop_running()
        logger.info("Telegram bot stopped")

    signal.signal(signal.SIGINT, partial(handle_shutdown, app=application))
    signal.signal(signal.SIGTERM, partial(handle_shutdown, app=application))

    logger.info("Starting Telegram bot polling...")
    application.run_polling(allowed_updates=["message"])
    logger.info("Telegram bot stopped")

def start_bot():
    """Функция для запуска бота из Django."""
    setup_telegram_bot()