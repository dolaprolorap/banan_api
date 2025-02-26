## Развертывание и запуск
Для подтягивания зависимостей выполнить:
```
pip install -r requirenments.txt
```

Для запуска приложения выполнить:
```
flask --app main run
```

## Эндпоинты

### /create-session

Http-метод: POST

Описание: Создать новую сессию и вернуть её публичный идентификатор

Параметры: нет

Возвращает: json формата:
```
{
    "data": {
        "public_id": "27afe214-c0a5-4e97-8633-c23ddc836a88"
    },
    "success": true
}
```

При запросах, время между которыми меньше 10 миллисекунд, отправляется следующий ответ:
```
{
    "msg": "Too frequent create requests",
    "success": false
}
```

### /update-session

Http-метод: POST

Описание: Обновляет данные сессии

Параметры: json формата:
```
{
    "public_id": "b05ac770-846e-4870-950b-537cb961c602",
    "steps": 10,
    "is_finished": false
}
```

Возвращает: json формата:
```
{
    "data": {},
    "success": true
}
```
