"""
Servicio de membership.

Regla de módulos (no negociable, AGENTS.md): este service es el ÚNICO punto de
entrada que otros módulos pueden llamar para leer/mutar datos de membership.
Ningún otro módulo debe importar membership/repository.py directamente.
"""
from datetime import date

from sqlalchemy.orm import Session

from core.config import now as _now
from membership.repository import MembershipRepository, MembershipTypeRepository
from membership.schemas import MembershipSummary
from models import Membership


def hoy() -> date:
    return _now().date()


def get_membership_for_user(user_id: int, db: Session) -> Membership | None:
    """Fila `estado=activa` sin validar fecha/visitas — para que quien llame
    (ej. checkin.service, RN-01 inversa de 002) determine la razón exacta de
    por qué RN-01 no se cumple."""
    return MembershipRepository(db).get_active_by_user(user_id)


def get_active_membership(user_id: int, db: Session) -> Membership | None:
    """RN-01: membresía con estado activa, no vencida (hoy <= fecha_vencimiento)
    y con visitas_restantes > 0. No confía solo en `estado`, revalida la fecha."""
    membership = MembershipRepository(db).get_active_by_user(user_id)
    if membership is None:
        return None
    if membership.fecha_vencimiento < hoy():
        return None
    if membership.visitas_restantes <= 0:
        return None
    return membership


def consume_visit(membership_id: int, db: Session) -> Membership:
    """RN-08: descuenta exactamente 1 visita. `SELECT ... FOR UPDATE` serializa
    descuentos concurrentes (RNF ≥10 concurrencia, plan.md de 001). No hace
    commit — el orquestador (checkin.service) confirma la transacción completa."""
    membership = MembershipRepository(db).get_for_update(membership_id)
    membership.visitas_restantes -= 1
    return membership


def get_membership_summary(user_id: int, db: Session) -> MembershipSummary | None:
    """Mínimo del semáforo reutilizado por checkin (001) y resumen (007)."""
    membership = MembershipRepository(db).get_active_by_user(user_id)
    if membership is None:
        return None
    tipo = MembershipTypeRepository(db).get_by_id(membership.tipo_id)
    return MembershipSummary(
        tipo=tipo.nombre if tipo else "",
        visitas_restantes=membership.visitas_restantes,
        fecha_vencimiento=membership.fecha_vencimiento,
    )
