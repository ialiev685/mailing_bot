#!/bin/bash

set -e  # Выход при ошибке

MESSAGE="${1:-auto_migration}"

# Проверяем и создаем папку versions
if [ ! -d "alembic/versions" ]; then
    echo "📁 Creating alembic/versions directory..."
    mkdir -p alembic/versions
fi

if alembic check; then
    echo "✅ No migration"
    exit 0
else
    echo "🔄 Migration detected"
    alembic revision --autogenerate -m "$MESSAGE"
    alembic upgrade head
    echo "✅ Migrate created"
    exit 1
fi