from .base import *

# Отладка: подтверждаем, что development.py загружен
print("Загружаем config/settings/development.py")

# Включение режима отладки для разработки
DEBUG = True

# Разрешенные хосты для локальной разработки
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Секретный ключ для разработки (в продакшене должен быть заменен)
SECRET_KEY = config('DJANGO_SECRET_KEY')

# Настройки базы данных для разработки
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql', # Движок PostgreSQL
        'NAME': 'aichat_db',                      # Имя базы данных
        'USER': 'aichat_user',                    # Пользователь
        'PASSWORD': 'PAC66rty110%',               # Пароль
        'HOST': 'localhost',                      # Хост
        'PORT': '5432',                           # Порт
    }
}

# Отладка: выводим настройки DATABASES из development.py
print(f"DATABASES в development.py: {DATABASES}")

# Путь для собранных статических файлов
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')