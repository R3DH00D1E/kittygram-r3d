# Kittygram API

Kittygram - это учебный REST API на Django REST Framework для работы с котиками, пользователями и достижениями.

Сервис позволяет:

- регистрировать пользователей;
- получать JWT-токен;
- создавать и редактировать карточки котов;
- хранить список достижений кота.

## Технологии

- Python 3.9+
- Django 3.2.3
- Django REST Framework 3.12.4
- Djoser 2.1.0
- JWT (djangorestframework-simplejwt 4.8.0)
- SQLite (по умолчанию для локальной разработки)

## Быстрый старт (локально)

1. Клонируйте репозиторий и перейдите в папку проекта:

```bash
git clone https://github.com/yandex-praktikum/kittygram2.git
cd kittygram2
```

2. Создайте и активируйте виртуальное окружение:

macOS / Linux:

```bash
python3 -m venv env
source env/bin/activate
```

Windows:

```bash
python -m venv env
env\Scripts\activate
```

3. Установите зависимости:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4. Примените миграции:

```bash
python manage.py migrate
```

5. Запустите сервер:

```bash
python manage.py runserver
```

API будет доступно по адресу: http://127.0.0.1:8000/

## Основные эндпоинты

### Аутентификация (Djoser + JWT)

- `POST /auth/users/` - регистрация пользователя
- `POST /auth/jwt/create/` - получение access/refresh токенов
- `POST /auth/jwt/refresh/` - обновление access токена
- `POST /auth/jwt/verify/` - проверка токена

### Пользователи

- `GET /users/` - список пользователей
- `GET /users/{id}/` - пользователь по id

### Коты

- `GET /cats/` - список котов
- `POST /cats/` - создать кота
- `GET /cats/{id}/` - получить кота
- `PUT /cats/{id}/` - полностью обновить кота
- `PATCH /cats/{id}/` - частично обновить кота
- `DELETE /cats/{id}/` - удалить кота

### Достижения

- `GET /achievements/` - список достижений
- `POST /achievements/` - создать достижение
- `GET /achievements/{id}/` - получить достижение
- `PUT /achievements/{id}/` - обновить достижение
- `PATCH /achievements/{id}/` - частично обновить достижение
- `DELETE /achievements/{id}/` - удалить достижение

## Примеры JSON

Регистрация пользователя:

```json
{
	"username": "kotik_lover",
	"password": "securepass123"
}
```

Получение JWT:

```json
{
	"username": "kotik_lover",
	"password": "securepass123"
}
```

Создание кота:

```json
{
	"name": "Барсик",
	"color": "White",
	"birth_year": 2020,
	"owner": 1,
	"achievements": [
		{
			"achievement_name": "Лучший кот"
		}
	]
}
```

Пример ответа:

```json
{
	"id": 1,
	"name": "Барсик",
	"color": "White",
	"birth_year": 2020,
	"achievements": [
		{
			"id": 1,
			"achievement_name": "Лучший кот"
		}
	],
	"owner": 1,
	"age": 6
}
```

## Ограничения модели

- `color` принимает только одно из значений: `Gray`, `Black`, `White`, `Ginger`, `Mixed`.
- `owner` должен быть id существующего пользователя.
- `birth_year` - целое число (в текущей реализации без проверки на будущий год).

## Работа с API через Postman

Ниже практичный сценарий: от нуля до первого созданного кота.

1. Создайте окружение Postman:

- `baseUrl` = `http://127.0.0.1:8000`
- `accessToken` = пусто

2. Создайте пользователя:

- Метод: `POST`
- URL: `{{baseUrl}}/auth/users/`
- Body -> raw -> JSON:

```json
{
	"username": "kotik_lover",
	"password": "securepass123"
}
```

3. Получите JWT токен:

- Метод: `POST`
- URL: `{{baseUrl}}/auth/jwt/create/`
- Body:

```json
{
	"username": "kotik_lover",
	"password": "securepass123"
}
```

В ответе будет:

```json
{
	"refresh": "...",
	"access": "..."
}
```

Скопируйте `access` в переменную окружения `accessToken`.

4. Проверка авторизации:

- Метод: `GET`
- URL: `{{baseUrl}}/users/`
- Header: `Authorization: Bearer {{accessToken}}` (можно и без него для текущего проекта, но лучше сразу привыкать к правильной схеме)

5. Создайте кота:

- Метод: `POST`
- URL: `{{baseUrl}}/cats/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer {{accessToken}}`
- Body:

```json
{
	"name": "Снежок",
	"color": "White",
	"birth_year": 2021,
	"owner": 1,
	"achievements": [
		{
			"achievement_name": "Поймал лазер"
		}
	]
}
```

6. Проверьте список котов:

- Метод: `GET`
- URL: `{{baseUrl}}/cats/`

7. Обновите кота:

- Метод: `PATCH`
- URL: `{{baseUrl}}/cats/1/`
- Body:

```json
{
	"name": "Снежок PRO"
}
```

8. Удалите кота:

- Метод: `DELETE`
- URL: `{{baseUrl}}/cats/1/`

## Полезно при отладке

- Ошибка `400 Bad Request`: проверьте JSON и обязательные поля (`name`, `color`, `birth_year`, `owner`).
- Ошибка `401 Unauthorized`: проверьте заголовок `Authorization` и актуальность токена.
- Ошибка `404 Not Found`: проверьте URL и id ресурса.

## Документация в браузере

- Корневой список маршрутов: http://127.0.0.1:8000/
- Коты: http://127.0.0.1:8000/cats/
- Пользователи: http://127.0.0.1:8000/users/
- Аутентификация: http://127.0.0.1:8000/auth/

## Автор

Студент: Кондратович А.В.
Группа: ПИ2У/24б
Год: 2026
