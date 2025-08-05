migrate:
	alembic revision --autogenerate -m "${NAME}"
	alembic upgrade head


test:
	python -m pytest tests/test_user.py