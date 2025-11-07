# Фудграм

### Описание проекта:
«Фудграм» — сайт, на котором можно публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Технологии
- Python 3.9
- Django==4.2.22
- djangorestframework==3.16.0
- nginx
- djoser==2.3.1
- Postgresql

## Что cделано:

- Настроен запуск проекта Foodgram в контейнерах и CI/CD с помощью GitHub Actions
- Пуш в ветку master запускает сборку и деплой Foodgram, а после успешного деплоя вам приходит сообщение в телеграм.
- настроено взаимодействие Python-приложения с внешними API-сервисами;
- создан собственный API-сервис на базе проекта Django;
- подключено SPA к бэкенду на Django через API;
- созданы образы и запущены контейнеры Docker;
- созданы, развёрнуты и запущены на сервере мультиконтейнерные приложения;
- закреплены на практике основы DevOps, включая CI&CD.
Инструменты и стек: #python #JSON #YAML #Django #React #Telegram #API #Docker #Nginx #PostgreSQL #Gunicorn #JWT #Postman

## Автор
Илья Клюжев https://github.com/kluyzh 

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone <https or SSH URL>
```

Создать файл .evn для хранения ключей в корне проекта:

```
SECRET_KEY='указать секретный ключ'
ALLOWED_HOSTS='указать имя,IP хоста,"backend"'
POSTGRES_DB: django_db
POSTGRES_USER: django_user
POSTGRES_PASSWORD: django_password
DB_HOST=db
DB_PORT=5432
DEBUG=False
```

Из основной директории
```
docker compose up -d
```

Наполнить проект ингредиентами
```
docker compose exec backend python manage.py load_ingredients ingredients.json
```
Создать суперпользователя
```
docker compose exec backend python manage.py createsuperuser
```
Войти в админ зону и создать свои теги для рецептов
```
http://127.0.0.1:80/admin/
```
