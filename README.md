# Kittygram API

Kittygram - учебный REST API на Django REST Framework для управления котиками и их достижениями.

Проект поддерживает:
- регистрацию пользователей;
- JWT-аутентификацию;
- CRUD-операции для котов;
- справочник достижений (15 предзаполненных значений);
- запуск в Docker;
- CI/CD деплой на Ubuntu-сервер через GitHub Actions.

## Технологии

- Python 3.9+
- Django 3.2.3
- Django REST Framework 3.12.4
- Djoser 2.1.0
- SimpleJWT 4.8.0
- SQLite
- Gunicorn
- WhiteNoise
- Docker / Docker Compose
- GitHub Actions

## Локальный запуск (без Docker)

1. Клонируйте репозиторий и перейдите в директорию проекта:

```bash
git clone <url-вашего-репозитория>
cd kittygram-r3d
```

2. Создайте и активируйте виртуальное окружение:

```bash
python3 -m venv env
source env/bin/activate
```

3. Установите зависимости:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4. Выполните миграции:

```bash
python manage.py migrate
```

5. Запустите сервер:

```bash
python manage.py runserver
```

API доступно по адресу: http://127.0.0.1:8000/

## Основные эндпоинты

### Аутентификация

- `POST /auth/users/` - регистрация
- `POST /auth/jwt/create/` - получение access/refresh
- `POST /auth/jwt/refresh/` - обновление access
- `POST /auth/jwt/verify/` - проверка токена

### Пользователи

- `GET /users/`
- `GET /users/{id}/`

### Коты

- `GET /cats/`
- `POST /cats/`
- `GET /cats/{id}/`
- `PUT /cats/{id}/`
- `PATCH /cats/{id}/`
- `DELETE /cats/{id}/`

### Достижения (только чтение)

- `GET /achievements/`
- `GET /achievements/{id}/`

## Формат achievements в запросах

В текущей версии достижения передаются **числовыми ID**:

```json
{
  "name": "Барсик",
  "color": "White",
  "birth_year": 2020,
  "owner": 1,
  "achievements": [1, 3, 7]
}
```

Пример ответа:

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

docker run --rm -p 8000:8000 \
  -e DJANGO_SECRET_KEY='change-me' \
  -e DJANGO_ALLOWED_HOSTS='127.0.0.1,localhost' \
  kittygram:local
```

После запуска API будет доступно на http://127.0.0.1:8000/

## CI/CD через GitHub Actions

Workflow: `.github/workflows/deploy.yml`

Когда запускается:
- автоматически на `push` в `master`;
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
- `SERVER_APP_DIR` - папка приложения на сервере (например `/opt/kittygram`)
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
cd /opt/kittygram

docker compose -f docker-compose.server.yml --env-file .env ps
```

Приложение должно открываться по адресу:
- `http://<ваш-server-ip>:8000/`

## Полезно при отладке

- `401 Unauthorized` - проверьте Bearer-токен.
- `400 Bad Request` - проверьте JSON и типы полей (`achievements` должен быть массивом чисел).
- `404 Not Found` - проверьте URL и ID.
- Ошибки деплоя в Actions - смотрите лог jobs `build` и `deploy`.

## Автор

Студент: Кондратович А.В.
Группа: ПИ2У/246
Год: 2026
