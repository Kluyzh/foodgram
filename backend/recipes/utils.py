from django.http import HttpResponse
import io


def generate_shopping_list(ingredients):
    # Генерация текстового файла
    text_buffer = io.StringIO()
    text_buffer.write("Список покупок:\n\n")
    for item in ingredients:
        text_buffer.write(f"{item[0]} - {item[1]} {item[2]}\n")
    
    response = HttpResponse(
        text_buffer.getvalue(),
        content_type="text/plain"
    )
    response["Content-Disposition"] = (
        "attachment; filename=shopping_list.txt"
    )
    return response