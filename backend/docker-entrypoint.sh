#!/bin/sh
set -e

# Espera a que Postgres acepte conexiones antes de migrar.
# No usamos un healthcheck de compose para esto porque igual necesitamos
# reintentar aquí si el contenedor se reinicia solo (sin pasar por compose).
echo "Esperando a que la base de datos esté lista..."
until python -c "
import os, sys, time
import psycopg2
try:
    psycopg2.connect(os.environ['DATABASE_URL'])
except Exception as e:
    print(e)
    sys.exit(1)
"; do
  sleep 1
done

echo "Aplicando migraciones (alembic upgrade head)..."
alembic upgrade head

echo "Arrancando servidor..."
exec "$@"
