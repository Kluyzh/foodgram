# Фудграм

### Описание проекта:
«Фудграм» — сайт, на котором можно публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Технологии
- Python 3.9
- Django==3.2.16
- djangorestframework==3.12.4
- nginx
- djoser==2.1.0
- Postgres

## Что cделано:

- Настроен запуск проекта Foodgram в контейнерах и CI/CD с помощью GitHub Actions
- Пуш в ветку master запускает тестирование и деплой Foodgram, а после успешного деплоя вам приходит сообщение в телеграм.
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

Перейти в директорию backend
```
cd /foodgram-project-react/backend/
```

Создать и активировать вирутальное окружение(для Windows):
```
python -m venv venv
```
```
source venv/Scripts/activate
```

Установоить зависимости:
```
pip install -r requirements.txt
```

Создать файл .evn для хранения ключей в корне проекта:

```
SECRET_KEY='указать секретный ключ'
ALLOWED_HOSTS='указать имя или IP хоста'
POSTGRES_DB: django_db
POSTGRES_USER: django_user
POSTGRES_PASSWORD: django_password
DB_NAME=kittygram
DB_HOST=db
DB_PORT=5432
SECRET_KEY=<50ти символьный ключ>
DEBUG=False
```

Запустить docker-compose.production:
```
docker compose -f docker-compose.production.yml up
```

Выполнить миграции, сбор статики:
```
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /static/static/
```

Наполнить базу данных ингредиентами:
```
docker compose exec backend python manage.py load_ingredients_from_csv
```

Создать суперпользователя, ввести почту, логин, пароль:

```
docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```
