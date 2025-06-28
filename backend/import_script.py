import json
import os

import django

from recipes.models import Ingredient

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram_backend.settings')
django.setup()


with open('ingredients.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    Ingredient.objects.create(
        name=item['name'],
        measurement_unit=item['measurement_unit']
    )

print(f'Imported {len(data)} ingredients')
