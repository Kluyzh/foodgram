import json
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загружает ингредиенты из JSON-файла в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='Путь к JSON-файлу с ингредиентами'
        )

    def handle(self, *args, **options):
        file_path = options['json_file']

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                ingredients_data = json.load(file)

                created_count = 0
                for item in ingredients_data:
                    obj, created = Ingredient.objects.get_or_create(
                        name=item['name'],
                        defaults={'measurement_unit': item['measurement_unit']}
                    )
                    if created:
                        created_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Успешно загружено {created_count}/{len(ingredients_data)} ингредиентов'
                    )
                )

        except FileNotFoundError:
            self.stderr.write(f'Ошибка: Файл {file_path} не найден')
        except json.JSONDecodeError:
            self.stderr.write('Ошибка: Некорректный JSON-формат')
        except KeyError as e:
            self.stderr.write(f'Ошибка: Отсутствует обязательное поле {e}')
