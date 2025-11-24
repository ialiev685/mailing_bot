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
	sudo docker-compose --env-file .env.dev up -d --build

build-stage:
	docker-compose -f docker-compose-stage.yml -p mailing_bot_stage --env-file .env.dev up -d --build

build-prod:
	docker-compose -f docker-compose-prod.yml -p mailing_bot_prod --env-file .env.prod up -d --build

stop-dev:
	sudo docker-compose down

stop-stage:
	sudo docker-compose -f docker-compose-stage.yml -p mailing_bot_stage --env-file .env.dev down

stop-prod:
	docker-compose -f docker-compose-prod.yml -p mailing_bot_prod --env-file .env.prod down