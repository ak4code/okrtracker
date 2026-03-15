# OKRTracker

<div align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Manrope&weight=600&size=24&duration=2600&pause=900&center=true&vCenter=true&width=840&lines=%D0%A1%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D0%B0+OKR+%D0%B4%D0%BB%D1%8F+%D0%BA%D0%BE%D0%BC%D0%B0%D0%BD%D0%B4;Django+6+%2B+Nuxt+4+%2B+DRF+%2B+PostgreSQL;REST+API+%D0%BF%D0%B0%D0%BD%D0%B5%D0%BB%D1%8C+%D0%B8+%D1%81%D0%BE%D0%B2%D1%80%D0%B5%D0%BC%D0%B5%D0%BD%D0%BD%D1%8B%D0%B9+frontend" alt="Typing SVG" />
</div>

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
![Django](https://img.shields.io/badge/Django-6.0-0C4B33?logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-API-A30000)
![Nuxt](https://img.shields.io/badge/Nuxt-4-00DC82?logo=nuxt&logoColor=white)
![Vue](https://img.shields.io/badge/Vue-3-4FC08D?logo=vuedotjs&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-4169E1?logo=postgresql&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker%20Compose-dev-2496ED?logo=docker&logoColor=white)
![Ruff](https://img.shields.io/badge/Ruff-lint%20%2B%20format-D7FF64?logo=ruff&logoColor=black)
![ty](https://img.shields.io/badge/ty-typecheck-111827)
![uv](https://img.shields.io/badge/uv-package%20manager-DE5FE9)

</div>

<p align="center">
  <b>OKRTracker</b> — система управления OKR для команд.
  <br/>
  Проект состоит из Django API, административной панели, Nuxt frontend и локального docker-compose окружения для разработки.
</p>

---

## Зачем Этот Проект

- Управление кварталами, командами, ролями и пользователями в одном месте.
- CRUD для OKR, key results, комментариев и check-ins через REST API.
- Отдельный frontend на Nuxt 4 для рабочего интерфейса.
- Django admin для служебного управления и отладки данных.
- Разделение логики на `api`, `selectors`, `services`.
- Подготовленное dev-окружение с PostgreSQL, backend, frontend и nginx.

## Возможности

- **OKR** — создание, редактирование, просмотр деталей и статусов.
- **Key Results** — числовые и процентные метрики с прогрессом и check-ins.
- **Комментарии** — обсуждение OKR внутри карточек целей.
- **Кварталы** — управление активными и будущими периодами.
- **Команды и роли** — отдельные справочники для оргструктуры.
- **Пользователи** — JWT login, `me` endpoint, админские CRUD-операции.
- **Demo seed** — наполнение базы абстрактными командами и демонстрационными OKR.

## Технологический Стек

| Layer | Tools |
|---|---|
| Backend | Django 6, Django REST Framework, SimpleJWT |
| Frontend | Nuxt 4, Vue 3, Tailwind CSS 4, lucide-vue-next |
| Data | PostgreSQL 17, Django ORM |
| Infra | Docker Compose, Nginx |
| Quality | Ruff, ty, pytest, pre-commit |
| Package Management | uv |

## Архитектура

Проект состоит из frontend на Nuxt 4 и backend на Django 6. Во время локальной разработки frontend и backend работают в отдельных контейнерах, а nginx отдаёт интерфейс и проксирует API-запросы.

На стороне Django код разделён на два основных приложения: `core` отвечает за пользователей, роли, команды и аутентификацию, а `okr` за кварталы, OKR, key results, комментарии и check-ins.

Внутри backend логика разнесена по слоям `api`, `selectors` и `services`: API обрабатывает HTTP-запросы, `selectors` отвечают за чтение данных, `services` за изменения и бизнес-операции. Это упрощает поддержку и не даёт бизнес-логике расползаться по view-слою.

## Быстрый Старт (Docker)

### 1) Подготовка

- Установи `Docker`, `Docker Compose` и `mkcert`.
- Создай `backend/.env` на основе `backend/.env.example`.
- Заполни переменные для суперпользователя:
  - `DJANGO_SUPERUSER_EMAIL`
  - `DJANGO_SUPERUSER_USERNAME`
  - `DJANGO_SUPERUSER_PASSWORD`

### 2) Запуск

```bash
make init
make up
make migrate
```

### 3) Наполнение демо-данными

После успешного запуска выполни:

```bash
make seed-demo
```

Локальные адреса:

- `https://localhost:8080` — nginx + frontend
- `http://localhost:8081` — nginx без TLS
- `http://127.0.0.1:8000` — backend внутри dev-потока
- `http://127.0.0.1:3000` — frontend dev server

Сервисы:

- `postgres` — PostgreSQL 17
- `backend` — Django app
- `frontend` — Nuxt dev server
- `nginx` — reverse proxy и локальный HTTPS

Список всех команд можно получить через `make help`.

## API

- Base paths: `/api/core/`, `/api/okr/`
- Auth: JWT (`/api/core/auth/jwt/login/`, `/api/core/auth/jwt/refresh/`)
- Current user: `/api/core/auth/me/`

| Prefix | Описание |
|---|---|
| `/api/core/roles/` | Роли |
| `/api/core/teams/` | Команды |
| `/api/core/users/` | Пользователи |
| `/api/okr/quarters/` | Кварталы |
| `/api/okr/okrs/` | OKR и вложенные данные |
| `/api/okr/key-results/` | Обновление key results |
| `/api/okr/check-ins/` | Обновление check-ins |

## Заметки По Разработке

- Python-зависимости ведутся через `uv` и [`backend/pyproject.toml`](/home/dev/projects/okrtracker/backend/pyproject.toml).
- Для качества кода используются `ruff`, `ty`, `pytest`, `pre-commit`.
- JWT-auth уже заведён в `core.api`.
- В backend есть demo seed команда: `seed_workspace_demo`.
- Для локального HTTPS используется `mkcert` и `make certs`.

---

<div align="center">
  <sub>Сделано на Django и Nuxt.</sub>
</div>
