NAME ?= auto_migration

migrate:
	bash ./scripts/migrate.sh "${NAME}"

start:
	python main.py

test:
# -s чтобы срабатывал логи print 	
	pytest -s