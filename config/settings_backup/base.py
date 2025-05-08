import os
from pathlib import Path
from decouple import config

# Отладка: подтверждаем, что base.py загружен
print("Загружаем config/settings/base.py")

# Определяем базовую директорию проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Секретный ключ Django, получаем из переменной окружения или используем значение по умолчанию
SECRET_KEY = config('DJANGO_SECRET_KEY')

# Режим отладки (по умолчанию включен, переопределяется в production.py)
DEBUG = True

# Разрешенные хосты для обработки запросов (по умолчанию для разработки)
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Список установленных приложений Django
INSTALLED_APPS = [
    'django.contrib.admin',           # Панель администратора
    'django.contrib.auth',            # Аутентификация пользователей
    'django.contrib.contenttypes',    # Управление типами контента
    'django.contrib.sessions',        # Управление сессиями
    'django.contrib.messages',        # Сообщения для пользователей
    'django.contrib.staticfiles',     # Управление статическими файлами
    'aichat.apps.AichatConfig',      # Приложение aichat
    'crispy_forms',                  # Библиотека для улучшения форм
    'crispy_bootstrap5',             # Шаблоны Bootstrap 5 для crispy_forms
]

# Список middleware для обработки запросов
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',         # Безопасность
    'django.contrib.sessions.middleware.SessionMiddleware',  # Сессии
    'django.middleware.common.CommonMiddleware',             # Общие функции
    'django.middleware.csrf.CsrfViewMiddleware',             # Защита от CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Аутентификация
    'django.contrib.messages.middleware.MessageMiddleware',  # Сообщения
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # Защита от кликджекинга
]

# URL-конфигурация проекта
ROOT_URLCONF = 'config.urls'

# Настройки шаблонов
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates', # Шаблонизатор Django
        'DIRS': [],                                                  # Дополнительные директории шаблонов
        'APP_DIRS': True,                                            # Искать шаблоны в приложениях
        'OPTIONS': {
            'context_processors': [                                  # Процессоры контекста
                'django.template.context_processors.debug',           # Данные для отладки
                'django.template.context_processors.request',         # Данные запроса
                'django.contrib.auth.context_processors.auth',        # Данные аутентификации
                'django.contrib.messages.context_processors.messages', # Сообщения
            ],
        },
    },
]

# Приложение WSGI для развертывания
WSGI_APPLICATION = 'config.wsgi.application'

# URL и путь для медиафайлов
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Модель пользователя
AUTH_USER_MODEL = 'aichat.User'

# Валидаторы паролей
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'}, # Проверка сходства
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},           # Минимальная длина
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},          # Проверка на простоту
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},         # Проверка на цифры
]

# Язык и часовой пояс
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True  # Включить интернационализацию
USE_TZ = True    # Использовать часовой пояс

# Настройки статических файлов
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')] # Директория для статических файлов
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')   # Директория для собранных файлов

# Тип автоинкрементного поля по умолчанию
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Настройки crispy_forms для Bootstrap 5
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# API-ключи и токены (заглушки, если .env отсутствует)
try:
    SEARCHAPI_API_KEY = config('SEARCHAPI_API_KEY')
    TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN')
    # SEARCHAPI_API_KEY = config('SEARCHAPI_API_KEY', default='dummy-key')
    # TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN', default='dummy-token')
except Exception as e:
    print(f"Ошибка загрузки API-ключей: {e}")

# URL для аутентификации
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'

# Настройки логирования
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}', # Формат логов
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',  # Ротация логов
            'filename': os.path.join(BASE_DIR, 'debug.log'), # Путь к файлу логов
            'maxBytes': 1024 * 1024 * 5,                     # Максимальный размер файла
            'backupCount': 5,                                # Количество резервных копий
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',                # Вывод в консоль
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',                                # Уровень логирования
            'propagate': False,
        },
        'aichat': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}