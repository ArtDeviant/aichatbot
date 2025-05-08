from .base import *
from decouple import config
import traceback

# Отладка: подтверждаем, что production.py загружен
print("Загружаем config/settings/production.py")

try:
    # Отключение режима отладки для продакшена
    DEBUG = False

    # Разрешенные хосты для продакшена
    ALLOWED_HOSTS = ['example.com', 'www.example.com', 'ip_host']

    # Секретный ключ из переменной окружения
    SECRET_KEY = config('DJANGO_SECRET_KEY')

    # Настройки базы данных для продакшена
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql', # Движок PostgreSQL
            'NAME': config('DB_NAME'),                 # Имя базы данных
            'USER': config('DB_USER'),                 # Пользователь
            'PASSWORD': config('DB_PASSWORD'),         # Пароль
            'HOST': config('DB_HOST'),                 # Хост
            'PORT': config('DB_PORT', default='5432'), # Порт
        }
    }

    # Отладка: выводим настройки DATABASES из production.py
    print(f"DATABASES в production.py: {DATABASES}")

    # Путь для собранных статических файлов
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

    # Настройки безопасности для продакшена
    SECURE_SSL_REDIRECT = True              # Перенаправление на HTTPS
    SESSION_COOKIE_SECURE = True            # Куки только через HTTPS
    CSRF_COOKIE_SECURE = True               # CSRF-токены только через HTTPS
    SECURE_BROWSER_XSS_FILTER = True        # Защита от XSS
    SECURE_HSTS_SECONDS = 31536000          # HSTS на год
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True   # HSTS для поддоменов
    SECURE_HSTS_PRELOAD = True              # Предварительная загрузка HSTS

except Exception as e:
    # Вывод ошибки, если что-то пошло не так (например, отсутствует переменная окружения)
    print(f"Ошибка в production.py: {e}")
    traceback.print_exc()
    raise