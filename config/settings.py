import os
from pathlib import Path
import sys

# Отладка: начало выполнения
print("Начало выполнения config/settings.py")

# Проверяем текущий PYTHONPATH
print(f"PYTHONPATH: {sys.path}")

# Определяем базовую директорию проекта
BASE_DIR = Path(__file__).resolve().parent.parent
print(f"BASE_DIR: {BASE_DIR}")

# Проверяем переменную окружения DJANGO_SETTINGS_MODULE
print(f"DJANGO_SETTINGS_MODULE: {os.getenv('DJANGO_SETTINGS_MODULE', 'не установлена')}")

# Проверяем переменную окружения DJANGO_ENV
ENVIRONMENT = os.getenv('DJANGO_ENV', 'development')
print(f"Используемая среда: {ENVIRONMENT}")

# Проверяем .env
print(f"DJANGO_ENV из os.environ: {os.environ.get('DJANGO_ENV', 'DJANGO_ENV не найдена')}")

# Секретный ключ Django
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
print("SECRET_KEY загружен")

# Режим отладки
DEBUG = True
print(f"DEBUG установлен: {DEBUG}")

# Разрешенные хосты
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
print(f"ALLOWED_HOSTS установлен: {ALLOWED_HOSTS}")

# Список установленных приложений Django
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'aichat.apps.AichatConfig',
    'crispy_forms',
    'crispy_bootstrap5',
]
print("INSTALLED_APPS установлен")

# Список middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
print("MIDDLEWARE установлен")

# URL-конфигурация проекта
ROOT_URLCONF = 'config.urls'
print("ROOT_URLCONF установлен")

# Настройки шаблонов
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
print("TEMPLATES установлен")

# Приложение WSGI
WSGI_APPLICATION = 'config.wsgi.application'
print("WSGI_APPLICATION установлен")

# Настройки базы данных
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}
print(f"DATABASES установлен: {DATABASES}")

# URL и путь для медиафайлов
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
print("MEDIA_URL и MEDIA_ROOT установлены")

# Модель пользователя
AUTH_USER_MODEL = 'aichat.User'
print("AUTH_USER_MODEL установлен")

# Валидаторы паролей
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
print("AUTH_PASSWORD_VALIDATORS установлен")

# Язык и часовой пояс
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True
print("Язык и часовой пояс установлены")

# Настройки статических файлов
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
print("STATIC_URL, STATICFILES_DIRS, STATIC_ROOT установлены")

# Тип автоинкрементного поля
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
print("DEFAULT_AUTO_FIELD установлен")

# Настройки crispy_forms
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'
print("CRISPY настройки установлены")

# API-ключи и токены
SEARCHAPI_API_KEY = os.getenv('SEARCHAPI_API_KEY', 'dummy-key')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'dummy-token')
print("API-ключи загружены")

# URL для аутентификации
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'
print("URL аутентификации установлены")

# Настройки логирования
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'aichat': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
print("LOGGING установлен")

# Отладка: проверяем django.conf.settings
from django.conf import settings
print(f"settings.DATABASES: {settings.DATABASES}")
print(f"settings.DEBUG: {settings.DEBUG}")
print(f"settings.ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")

# Отладка: конец выполнения
print("Конец выполнения config/settings.py")