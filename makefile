NAME ?= auto_migration

migrate:
	bash ./scripts/migrate.sh "${NAME}"

dev:
	STAND=DEV python main.py

start:
	STAND=PROD python main.py

test:
# -s чтобы срабатывал логи print 	
	pytest -s

build-dev:
	docker-compose -f docker-compose.dev.yml --env-file .env.dev up -d --build

build-prod:
	docker-compose -f docker-compose.prod.yml up -d --build