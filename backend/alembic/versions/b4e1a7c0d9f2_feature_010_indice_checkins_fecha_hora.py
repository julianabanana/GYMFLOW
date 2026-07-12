"""feature 010: índice en checkins.fecha_hora

Revision ID: b4e1a7c0d9f2
Revises: c98ffd6f38d1
Create Date: 2026-07-12 14:20:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'b4e1a7c0d9f2'
down_revision = 'c98ffd6f38d1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 010 (RF-12): el reporte de asistencias filtra por rango de fecha_hora.
    # Índice para que el filtro por rango no haga seq scan cuando el histórico
    # de check-ins crezca.
    op.create_index(
        op.f('ix_checkins_fecha_hora'), 'checkins', ['fecha_hora'], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_checkins_fecha_hora'), table_name='checkins')
