Foodgram - Ваши рецепты и вам продуктовый помощник

Описание проекта
Foodgram - это онлайн-платформа для публикации кулинарных рецептов.

Пользователи могут:

Создавать и публиковать свои рецепты

Добавлять рецепты других пользователей в избранное

Подписываться на авторов рецептов

Формировать список покупок для выбранных рецептов

Скачивать итоговый список покупок в текстовом формате

Проект доступен по адресу: https://foodgraaam.sytes.net

Технологический стек

Backend
Python 3.9

Django 4.2.22

Django REST Framework 3.16.0

Djoser 2.3.1 (аутентификация)

PostgreSQL 13 (база данных)

Gunicorn 23.0.0 (веб-сервер)

Psycopg2 2.9.9 (драйвер PostgreSQL)

Pillow 11.2.1 (обработка изображений)

Django-filter 25.1 (фильтрация данных)

Nginx 1.19 (прокси-сервер)

Frontend
React

Инфраструктура
Docker

Docker Compose

GitHub Actions (CI/CD)

Ключевые особенности

Фильтрация рецептов по тегам

Система подписок на авторов

Формирование списка покупок с группировкой ингредиентов

Возможность скачивания списка покупок

Управление избранными рецептами

Локальное развертывание с Docker
1. Клонирование репозитория
bash
git clone git@github.com:Kluyzh/foodgram.git
cd infra
2. Настройка окружения
Создайте файл .env в директории infra:

# Настройки базы данных
DB_ENGINE=django.db.backends.postgresql
DB_NAME=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=secure_password
DB_HOST=db
DB_PORT=5432

# Настройки Django
SECRET_KEY=django-insecure-!@#your_secret_key_here$%^
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Настройки для фронтенда
API_URL=http://localhost/api/
3. Запуск контейнеров
docker-compose up -d --build
4. Применение миграций
docker-compose exec backend python manage.py migrate
5. Создание администратора
docker-compose exec backend python manage.py createsuperuser
6. Импорт данных
# Ингредиенты
docker-compose exec backend python manage.py load_ingredients ingredients.json

7. Сбор статических файлов
docker-compose exec backend python manage.py collectstatic
8. Доступ к проекту
После выполнения всех команд:

Frontend: http://localhost

Backend API: http://localhost/api

Админ-панель: http://localhost/admin

Примеры API-запросов
Регистрация пользователя
bash
curl -X POST http://localhost/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
        "email": "user@example.com",
        "username": "new_user",
        "first_name": "Иван",
        "last_name": "Иванов",
        "password": "strongpassword123"
      }'
Получение токена
bash
curl -X POST http://localhost/api/auth/token/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "strongpassword123"}'

# Ответ: {"auth_token": "ваш_токен"}
Создание рецепта
bash
curl -X POST http://localhost/api/recipes/ \
  -H "Authorization: Token ваш_токен" \
  -H "Content-Type: application/json" \
  -d '{
        "name": "Паста Карбонара",
        "ingredients": [
          {"id": 1, "amount": 200},
          {"id": 2, "amount": 100},
          {"id": 3, "amount": 2}
        ],
        "tags": [1, 2],
        "image": "data:image/png;base64,iVBORw0KGgo...",
        "text": "Пошаговый рецепт...",
        "cooking_time": 30
      }'
Получение списка рецептов
bash
curl http://localhost/api/recipes/

# Фильтрация по тегам
curl http://localhost/api/recipes/?tags=завтрак&tags=обед
Скачивание списка покупок
bash
curl http://localhost/api/recipes/download_shopping_cart/ \
  -H "Authorization: Token ваш_токен" \
  -o shopping_list.txt
Управление проектом
Основные команды
bash
# Запуск контейнеров
docker-compose up -d

# Остановка контейнеров
docker-compose down

# Просмотр логов
docker-compose logs -f backend

# Пересборка контейнеров
docker-compose build

# Выполнение команд в контейнере
docker-compose exec backend python manage.py shell
Администрирование
После создания суперпользователя доступны:

Админ-панель Django: /admin

Управление пользователями, рецептами, ингредиентами

Просмотр статистики (количество добавлений в избранное)