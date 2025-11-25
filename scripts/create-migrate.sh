#!/bin/bash

set -e  # Выход при ошибке

MESSAGE="${1:-auto_migration}"

# Проверяем и создаем папку versions
mkdir -p alembic/versions

if alembic check; then
    echo "✅ No migration"
else
    echo "🔄 Migration detected"
    alembic revision --autogenerate -m "$MESSAGE"
    alembic upgrade head
    echo "✅ Migrate created"
fi