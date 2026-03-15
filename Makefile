COMPOSE := docker compose -f docker-compose.dev.yml
CERT_DIR := certs/local
CERT_FILE := $(CERT_DIR)/localhost.crt
KEY_FILE := $(CERT_DIR)/localhost.key
BACKEND_ENV_FILE := backend/.env
BACKEND_ENV_EXAMPLE := backend/.env.example

.PHONY: help init certs build up down restart logs ps config backend-shell frontend-shell migrate seed-demo

help:
	@echo "Доступные команды:"
	@echo "  make init            - создать backend/.env из backend/.env.example, если файла ещё нет"
	@echo "  make certs           - выпустить доверенный локальный TLS сертификат через mkcert"
	@echo "  make build           - собрать все контейнеры"
	@echo "  make up              - запустить проект в фоне"
	@echo "  make down            - остановить проект"
	@echo "  make restart         - перезапустить проект"
	@echo "  make logs            - показать логи"
	@echo "  make ps              - показать состояние сервисов"
	@echo "  make config          - проверить docker compose config"
	@echo "  make backend-shell   - shell в backend контейнере"
	@echo "  make frontend-shell  - shell в frontend контейнере"
	@echo "  make migrate         - применить миграции в backend"
	@echo "  make seed-demo       - заполнить базу демонстрационными OKR"

init:
	@if [ -f $(BACKEND_ENV_FILE) ]; then \
		echo "$(BACKEND_ENV_FILE) уже существует"; \
	else \
		cp $(BACKEND_ENV_EXAMPLE) $(BACKEND_ENV_FILE); \
		echo "Создан $(BACKEND_ENV_FILE) из $(BACKEND_ENV_EXAMPLE)"; \
	fi

certs:
	@mkdir -p $(CERT_DIR)
	@docker run --rm -v "$(CURDIR)/$(CERT_DIR):/certs" alpine sh -c "chown -R $$(id -u):$$(id -g) /certs || true"
	@mkcert -install
	@mkcert -cert-file $(CERT_FILE) -key-file $(KEY_FILE) localhost 127.0.0.1 ::1

build:
	$(COMPOSE) build

up: init certs
	$(COMPOSE) up --build -d

down:
	$(COMPOSE) down

restart: init certs
	$(COMPOSE) down
	$(COMPOSE) up --build -d

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

config:
	$(COMPOSE) config

backend-shell:
	$(COMPOSE) exec backend sh

frontend-shell:
	$(COMPOSE) exec frontend sh

migrate:
	$(COMPOSE) exec backend uv run python manage.py migrate

seed-demo:
	$(COMPOSE) exec backend uv run python manage.py seed_workspace_demo
