"""
Repository de membership — único punto de acceso a `membresias` y
`tipos_membresia` (AGENTS.md). Métodos concretos se agregan al implementar
spec/features/001, 007, 009.
"""
from sqlalchemy.orm import Session

from models import Membership, MembershipType, EstadoMembresia


class MembershipRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active_by_user(self, user_id: int) -> Membership | None:
        return (
            self.db.query(Membership)
            .filter(Membership.miembro_id == user_id, Membership.estado == EstadoMembresia.activa)
            .first()
        )

    def get_for_update(self, membership_id: int) -> Membership:
        """SELECT ... FOR UPDATE — serializa descuentos concurrentes (plan.md de 001)."""
        return (
            self.db.query(Membership)
            .filter(Membership.id == membership_id)
            .with_for_update()
            .one()
        )


class MembershipTypeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, tipo_id: int) -> MembershipType | None:
        return self.db.query(MembershipType).filter(MembershipType.id == tipo_id).first()
