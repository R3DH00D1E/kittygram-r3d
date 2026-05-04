# Kittygram API

REST API для управления котиками и их достижениями.

## Зависимости

```
Django==3.2.3
djangorestframework==3.12.4
djangorestframework-simplejwt==4.8.0
djoser==2.1.0
gunicorn==22.0.0
whitenoise==6.7.0
Pillow==11.3.0
PyJWT==2.1.0
```

## Переменные окружения

Создайте файл `.env` на основе `.env.example`:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

## Локальный запуск

### 1. Клонировать репозиторий:

```bash
git clone https://github.com/R3DH00D1E/kittygram-r3d.git
cd kittygram-r3d
```

### 2. Создать и активировать виртуальное окружение:

```bash
python3 -m venv env
source env/bin/activate
```

### 3. Установить зависимости:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Выполнить миграции:

```bash
python manage.py migrate
```

### 5. Создать суперпользователя:

```bash
python manage.py createsuperuser
```

### 6. Запустить проект:

```bash
python manage.py runserver
```

## Запуск через Docker

```bash
docker compose -f docker-compose.server.yml --env-file .env up -d
```

Миграции применяются автоматически при старте контейнера.

## API эндпоинты

### Аутентификация

| Метод | URL | Описание |
|-------|-----|---------|
| POST | `/auth/users/` | Регистрация |
| POST | `/auth/jwt/create/` | Получить токен |
| POST | `/auth/jwt/refresh/` | Обновить токен |

### Пользователи

| Метод | URL | Описание |
|-------|-----|---------|
| GET | `/users/` | Список пользователей (только чтение) |

### Коты

| Метод | URL | Описание | Права |
|-------|-----|---------|-------|
| GET, POST | `/cats/` | Список/создание котов | Все / Авторизованные |
| GET, PUT, DELETE | `/cats/{id}/` | Детали кота | Все / Владелец |

**Фильтры:** `color`, `owner`  
**Поиск:** `name`  
**Сортировка:** `name`, `birth_year`

### Достижения

| Метод | URL | Описание |
|-------|-----|---------|
| GET | `/achievements/` | Список достижений (только чтение) |

## Документация API

- **Swagger UI:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/
- **OpenAPI Schema:** http://localhost:8000/api/schema/

## Формат данных

### Пример создания кота с достижениями:

```json
{
  "name": "Барсик",
  "color": "White",
  "birth_year": 2020,
  "owner": 1,
  "achievements": [1, 3, 7]
}
```

### Пример ответа:

```json
{
  "id": 1,
  "name": "Барсик",
  "color": "White",
  "birth_year": 2020,
  "achievements": [1, 3, 7],
  "owner": 1,
  "age": 6
}
```

## Docker

В проекте используются файлы:

- `Dockerfile`
- `docker-entrypoint.sh`
- `docker-compose.server.yml`
- `.env.example`

### Локальная сборка и запуск контейнера

```bash
docker build -t kittygram:local .

docker run --rm -p 80:80 \
  -e DJANGO_SECRET_KEY='change-me' \
  -e DJANGO_ALLOWED_HOSTS='127.0.0.1,localhost' \
  kittygram:local
```

После запуска сайт будет доступен на http://127.0.0.1/

## CI/CD через GitHub Actions

Workflow: `.github/workflows/deploy.yml`

Когда запускается:

- автоматический `push` в `master`;
- вручную через `workflow_dispatch`.

Что делает pipeline:

1. Собирает Docker-образ.
2. Пушит образ в GHCR (`ghcr.io/<owner>/kittygram:latest`).
3. Подключается к серверу по SSH.
4. Копирует `docker-compose.server.yml` на сервер.
5. Создает/обновляет `.env` на сервере.
6. Выполняет `docker compose pull` и `docker compose up -d`.

## Что настроить в GitHub Secrets

В `Settings -> Secrets and variables -> Actions` добавьте:

- `SSH_HOST` - IP/домен сервера
- `SSH_PORT` - SSH порт (например `22`)
- `SSH_USER` - пользователь сервера
- `SSH_PRIVATE_KEY` - приватный SSH-ключ для деплоя
- `SERVER_APP_DIR` - папка приложения на сервере
- `DJANGO_SECRET_KEY` - продовый SECRET_KEY
- `DJANGO_ALLOWED_HOSTS` - хосты через запятую (например `example.com,1.2.3.4`)
- `GHCR_USERNAME` - GitHub username
- `GHCR_TOKEN` - GitHub PAT с правом `read:packages`

## Подготовка Ubuntu-сервера

Минимально на сервере должны быть:

- Docker;
- Docker Compose plugin (`docker compose`);
- пользователь с доступом к Docker;
- настроенный SSH-вход ключом для GitHub Actions.

Быстрая проверка:

```bash
docker --version
docker compose version
docker ps
```

## Как проверить деплой

После успешного workflow:

```bash
cd /директория/вашего/сайта/kittygram

docker compose -f docker-compose.server.yml --env-file .env ps
```

Приложение должно открываться по адресу:

- `http://<ваш-ip>/`

Если контейнер запущен через `docker compose` с `restart: unless-stopped`, то после перезагрузки сервера Docker поднимет его автоматически, когда сам сервис Docker стартует вместе с системой.

## Полезно при отладке

- `401 Unauthorized` - проверьте Bearer-токен.
- `400 Bad Request` - проверьте JSON и типы полей (`achievements` должен быть массивом чисел).
- `404 Not Found` - проверьте URL и ID.
- Ошибки деплоя в Actions - смотрите лог jobs `build` и `deploy`.

## Автор

Студент: Кондратович А.В.
Группа: ПИ2У/246
Год: 2026
