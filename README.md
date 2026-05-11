# Kittygram - Приложение для учёта котов

Полнофункциональное веб-приложение для управления котиками, их достижениями и статусами владения. Включает REST API и веб-интерфейс.

## Возможности

- **Управление котами** - добавление, редактирование, удаление информации о котах
- **Система достижений** - присвоение достижений котам
- **Статусы владения** - отслеживание статуса каждого кота (владеет, в приюте, в поиске и т.д.)
- **Загрузка фото** - добавление изображений котов
- **Профили пользователей** - система авторизации и управления профилями
- **Согласия на обработку данных** - отслеживание согласий на использование данных и фотографий
- **Веб-интерфейс** - удобный фронтенд для управления котами
- **REST API** - полнофункциональный API для интеграции

## Технологии

- Python 3.9+
- Django 3.2.3
- Django REST Framework 3.12.4
- django-filter 23.5
- Djoser 2.1.0 (аутентификация)
- SimpleJWT 4.8.0 (JWT токены)
- Pillow 11.3.0 (обработка изображений)
- Gunicorn (WSGI сервер)
- Docker / Docker Compose
- WhiteNoise (раздача статики)

## Переменные окружения

Создайте файл `.env` на основе `.env.example`:

```
DJANGO_SECRET_KEY=strong-secret
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=example.com,127.0.0.1,localhost
```

## Локальный запуск

### 1. Клонировать репозиторий:

```bash
git clone https://github.com/R3DH00D1E/kittygram-r3d.git
cd kittygram-r3d
```

macOS / Linux:

```bash
python3 -m venv env
source env/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
./env/bin/python manage.py migrate
./env/bin/python manage.py createsuperuser
./env/bin/python manage.py runserver 127.0.0.1:8000
```

Windows (PS):

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
env\Scripts\python.exe manage.py migrate
env\Scripts\python.exe manage.py createsuperuser
env\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Запуск через Docker:

```bash
docker compose up --build -d
```

Миграции и сбор статики применяются автоматически при старте контейнера.

## Модели данных

### Cat (Кот)

- **name** - имя кота
- **color** - окрас (Gray, Black, White, Ginger, Mixed, Tabby, Calico, Cream, Blue, Fawn)
- **birth_year** - год рождения
- **image** - фото кота
- **owner** - владелец (ForeignKey на User)
- **ownership_status** - статус владения (ForeignKey на OwnershipStatus)
- **achievements** - достижения (ManyToMany через AchievementCat)
- **age** - вычисляется автоматически (текущий год - год рождения)

### Achievement (Достижение)

- **name** - название достижения

### OwnershipStatus (Статус владения)

- **name** - название статуса
- **description** - описание статуса

### UserProfile (Профиль пользователя)

- **user** - связь с User (OneToOneField)
- **consent_personal** - согласие на обработку персональных данных
- **consent_photo** - согласие на публикацию фотографий
- **consent_*_date** - дата согласия

Профиль создаётся автоматически при регистрации пользователя.

## REST API эндпоинты

## Postman

Для ручной проверки API используйте коллекцию:

- [postman/kittygram_api_checks.postman_collection.json](postman/kittygram_api_checks.postman_collection.json)

Коллекция рассчитана на запуск в Docker по адресу `http://127.0.0.1:80` и использует `root/root` для получения JWT. Если запускаете проект локально на `127.0.0.1:8000`, поменяйте `baseUrl`, `username` и `password` в переменных коллекции.

Внутри коллекции 10 запросов: публичные проверки статусов, фильтрации и пагинации, а также проверка JWT и прав администратора.

### Аутентификация

| Метод | URL                    | Описание                                             |
| ---------- | ---------------------- | ------------------------------------------------------------ |
| POST       | `/auth/users/`       | Регистрация нового пользователя |
| POST       | `/auth/jwt/create/`  | Получить access и refresh токены              |
| POST       | `/auth/jwt/refresh/` | Обновить access токен                           |
| POST       | `/auth/jwt/verify/`  | Проверить токен                                |

### Пользователи

| Метод | URL              | Описание                        | Права              |
| ---------- | ---------------- | --------------------------------------- | ----------------------- |
| GET        | `/users/`      | Список пользователей | Только админ |
| GET        | `/users/{id}/` | Детали пользователя   | Только админ |

### Коты

| Метод | URL             | Описание                                 | Права                    |
| ---------- | --------------- | ------------------------------------------------ | ----------------------------- |
| GET        | `/cats/`      | Список всех котов                 | Все                        |
| POST       | `/cats/`      | Создать нового кота             | Авторизованные  |
| GET        | `/cats/{id}/` | Детали кота                            | Все                        |
| PUT        | `/cats/{id}/` | Обновить кота полностью     | Владелец / Админ |
| PATCH      | `/cats/{id}/` | Частичное обновление кота | Владелец / Админ |
| DELETE     | `/cats/{id}/` | Удалить кота                          | Владелец / Админ |

**Параметры запроса:**

- `color` - фильтр по окрасу
- `owner` - фильтр по владельцу (по ID пользователя)
- `ownership_status` - фильтр по статусу владения
- Ответы списка пагинированы, доступен параметр `page`

### Достижения

| Метод | URL                     | Описание                           | Права |
| ---------- | ----------------------- | ------------------------------------------ | ---------- |
| GET        | `/achievements/`      | Список всех достижений | Все     |
| GET        | `/achievements/{id}/` | Детали достижения          | Все     |

### Статусы владения

| Метод | URL                           | Описание              | Права              |
| ---------- | ----------------------------- | ----------------------------- | ----------------------- |
| GET        | `/ownership-statuses/`      | Список статусов | Все                  |
| POST       | `/ownership-statuses/`      | Создать статус   | Только админ |
| GET        | `/ownership-statuses/{id}/` | Детали статуса   | Все                  |
| PUT        | `/ownership-statuses/{id}/` | Обновить статус | Только админ |
| DELETE     | `/ownership-statuses/{id}/` | Удалить статус   | Только админ |

## Веб-интерфейс

### Страницы для гостей

- `/` - главная страница
- `/login/` - вход в аккаунт
- `/register/` - регистрация
- `/privacy/` - политика конфиденциальности
- `/gallery/` - галерея всех котов

### Страницы для авторизованных пользователей

- `/cabinet/` - личный кабинет (список своих котов)
- `/cabinet/#add-cat` - добавление нового кота

### Админ-панель

- `/admin/` - стандартная Django админ-панель

## Примеры API запросов

### Регистрация

```bash
POST /auth/users/
Content-Type: application/json

{
  "username": "myuser",
  "password": "mysecurepassword",
  "email": "user@example.com"
}
```

### Получить токены

```bash
POST /auth/jwt/create/
Content-Type: application/json

{
  "username": "myuser",
  "password": "mysecurepassword"
}

# Ответ:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Создать кота

```bash
POST /cats/
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
  "name": "Барсик",
  "color": "White",
  "birth_year": 2020,
  "achievements": [1, 3, 5]
}
```

### Получить список котов с фильтром

```bash
GET /cats/?color=White&owner=1
```

### Обновить кота

```bash
PATCH /cats/1/
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
  "name": "Барсик II",
  "color": "Gray"
}
```

### Удалить кота

```bash
DELETE /cats/1/
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Примеры ответов

### Список котов

```json
[
  {
    "id": 1,
    "name": "Барсик",
    "color": "White",
    "birth_year": 2020,
    "achievements": [1, 3, 7],
    "owner": 1,
    "ownership_status": 1,
    "image": "http://127.0.0.1:80/media/cats/barsik.jpg",
    "age": 6
  }
]
```

### Детали кота

```json
{
  "id": 1,
  "name": "Барсик",
  "color": "White",
  "birth_year": 2020,
  "achievements": [1, 3, 7],
  "owner": 1,
  "ownership_status": 1,
  "image": "http://127.0.0.1:80/media/cats/barsik.jpg",
  "age": 6
}
```

### Список пользователей (только для админа)

```json
[
  {
    "id": 1,
    "username": "Alexander",
    "email": "alex@example.com",
    "cats": ["Барсик", "Мурзик"]
  }
]
```

### Список достижений

```json
[
  {
    "id": 1,
    "name": "Чемпион"
  },
  {
    "id": 2,
    "name": "Ловец мышей"
  }
]
```

## Система прав доступа

### IsOwnerOrAdmin

Кастомный класс для проверки прав. Позволяет редактировать/удалять коты только владельцу или администратору.

Применяется к: `CatViewSet` (PUT, PATCH, DELETE)

### IsAuthenticatedOrReadOnly

Авторизованные пользователи могут создавать и изменять коты. Гости только читают.

Применяется к: `CatViewSet`

### IsAdminUser

Только администраторы могут управлять пользователями, статусами владения и создавать достижения.

Применяется к: `UserViewSet`, `OwnershipStatusViewSet`

## Docker

В проекте используются файлы:

- `Dockerfile` - образ приложения
- `docker-entrypoint.sh` - скрипт инициализации контейнера
- `docker-compose.yml` - конфигурация для продакшена
- `.env.example` - пример переменных окружения

После запуска приложение будет доступно на http://127.0.0.1/

## CI/CD через GitHub Actions

Workflow находится по пути: `.github/workflows/deploy.yml`

### Когда запускается:

- Автоматический `push` в ветку `master`
- Вручную через `workflow_dispatch`

### Что делает pipeline:

1. Собирает Docker-образ
2. Пушит образ в GitHub Container Registry (GHCR)
3. Подключается к серверу по SSH
4. Копирует конфиг `docker-compose.yml` на сервер
5. Создает/обновляет `.env` на сервере
6. Выполняет `docker compose pull` и `docker compose up -d`

## Что настроить в GitHub Secrets

В `Settings -> Secrets and variables -> Actions` добавьте:

| Секрет             | Описание                                                                                                                     | Пример                                                           |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------- |
| `SSH_HOST`             | IP или домен сервера                                                                                                  | `123.45.67.89`                                                       |
| `SSH_PORT`             | SSH порт                                                                                                                         | `22`                                                                 |
| `SSH_USER`             | Пользователь на сервере                                                                                         | `ubuntu`                                                             |
| `SSH_PRIVATE_KEY`      | Приватный SSH-ключ                                                                                                      | `-----BEGIN RSA PRIVATE KEY-----...`                                 |
| `SERVER_APP_DIR`       | Директория приложения на сервере                                                                        | `/home/ubuntu/kittygram`                                             |
| `DJANGO_SECRET_KEY`    | Django SECRET_KEY для продакшена                                                                                        | Генерируется случайно                              |
| `DJANGO_ALLOWED_HOSTS` | Хосты через запятую                                                                                                 | `example.com,1.2.3.4`                                                |
| `WEB_PORT`             | Хостовый порт для публикации приложения при деплое. По умолчанию порт 80. | `8000`                                                               |
| `GHCR_USERNAME`        | GitHub username                                                                                                                      | `Юзернейм из ГитХаба`                               |
| `GHCR_TOKEN`           | GitHub Personal Access Token (PAT)                                                                                                   | Создается в Параметрах учетной записи |

### Как создать GitHub PAT:

1. Перейти в `Settings -> Developer settings -> Personal access tokens`
2. Нажать `Generate new token`
3. Выбрать scope `read:packages`
4. Скопировать токен и добавить в Secrets как `GHCR_TOKEN`

## Подготовка сервера под CI/CD

На сервере должны быть установлены:

- Docker
- Docker Compose plugin (`docker compose`)
- Пользователь с доступом к Docker
- SSH-доступ для GitHub Actions

### Быстрая проверка:

```bash
docker --version
docker compose version
docker ps
```

### Создание пользователя для Docker:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Полезные команды для Docker:

```bash
# Запустить контейнеры
docker compose -f docker-compose.yml up -d

# Посмотреть логи
docker compose -f docker-compose.yml logs -f

# Остановить контейнеры
docker compose -f docker-compose.yml down

# Применить миграции в контейнере
docker compose -f docker-compose.yml exec web python manage.py migrate
```
