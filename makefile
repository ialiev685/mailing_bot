NAME ?= auto_migration

create-migrate:
	bash ./scripts/create-migrate.sh "${NAME}"

migrate-prod:
	docker-compose -f docker-compose-prod.yml exec app alembic upgrade head

migrate-dev:
	docker-compose -p mailing_bot_stage exec app_dev alembic upgrade head

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
	docker-compose -f docker-compose-prod.yml --env-file .env.prod up -d --build

stop-dev:
	sudo docker-compose down

stop-stage:
	sudo docker-compose -f docker-compose-stage.yml -p mailing_bot_stage --env-file .env.dev down

stop-prod:
	docker-compose -f docker-compose-prod.yml --env-file .env.prod down