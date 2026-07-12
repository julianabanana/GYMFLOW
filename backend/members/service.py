"""
Servicio de members.

Regla de módulos (no negociable, AGENTS.md): este service es el ÚNICO punto de
entrada que otros módulos pueden llamar para leer/mutar datos de members.
Ningún otro módulo debe importar members/repository.py directamente.
"""
from decimal import Decimal

from sqlalchemy.orm import Session

import membership.service as membership_service
from core.security import hash_password
from members.repository import MembersRepository
from models import EstadoUsuario, Membership, RolUsuario, User


class UsuarioNoEncontradoError(Exception):
    """El `user_id` pedido no existe (004)."""


class CedulaYaRegistradaError(Exception):
    """Ya existe un usuario con esa cédula (004) — se valida antes del
    INSERT/UPDATE para no dejar reventar un IntegrityError sin capturar."""


class EmailYaRegistradoError(Exception):
    """Ya existe un usuario con ese email (004), misma razón que arriba."""


class RolNoPermitidoError(Exception):
    """El actor no puede crear/ascender un usuario al rol pedido (004): ver
    `puede_asignar_rol`."""


PERMISO_ASIGNAR_ROL_EMPLEADO = "members.asignar_rol_empleado"


def puede_asignar_rol(actor_rol: RolUsuario, actor_permisos: set[str], rol_objetivo: RolUsuario) -> bool:
    """Quién puede crear un usuario con `rol_objetivo`, o ascender uno
    existente a ese rol (decisión del equipo, 004):
    - `administrador`: reservado exclusivamente al rol administrador, ningún
      permiso individual lo habilita.
    - `empleado`: administrador, o un empleado con el permiso individual
      `members.asignar_rol_empleado`.
    - `miembro`/`invitado`: cualquier staff autenticado (sin restricción extra)."""
    if rol_objetivo == RolUsuario.administrador:
        return actor_rol == RolUsuario.administrador
    if rol_objetivo == RolUsuario.empleado:
        return actor_rol == RolUsuario.administrador or PERMISO_ASIGNAR_ROL_EMPLEADO in actor_permisos
    return True


def get_user_by_cedula(cedula: str, db: Session) -> User | None:
    return MembersRepository(db).get_by_cedula(cedula)


def get_user_by_email(email: str, db: Session) -> User | None:
    return MembersRepository(db).get_by_email(email)


def get_user(user_id: int, db: Session) -> User:
    user = MembersRepository(db).get_by_id(user_id)
    if user is None:
        raise UsuarioNoEncontradoError()
    return user


def list_users(db: Session) -> list[User]:
    return MembersRepository(db).list_all()


def get_users_by_ids(user_ids: list[int], db: Session) -> dict[int, User]:
    """010: resuelve nombres de usuarios en lote (evita N+1 al enriquecer el
    reporte de asistencias). Punto de entrada del módulo dueño de `usuarios`
    para que `reports` no consulte esa tabla directamente (regla de módulos)."""
    return {u.id: u for u in MembersRepository(db).list_by_ids(user_ids)}


def _validar_unicidad(
    db: Session, cedula: str, email: str | None, excluir_id: int | None = None
) -> None:
    repo = MembersRepository(db)
    existente_cedula = repo.get_by_cedula(cedula)
    if existente_cedula is not None and existente_cedula.id != excluir_id:
        raise CedulaYaRegistradaError()
    if email is not None:
        existente_email = repo.get_by_email(email)
        if existente_email is not None and existente_email.id != excluir_id:
            raise EmailYaRegistradoError()


def create_user(
    cedula: str,
    nombre: str,
    email: str | None,
    rol: RolUsuario,
    estado: EstadoUsuario,
    password: str | None,
    db: Session,
) -> User:
    _validar_unicidad(db, cedula, email)
    user = User(
        cedula=cedula,
        nombre=nombre,
        email=email,
        rol=rol,
        estado=estado,
        password_hash=hash_password(password) if password else None,
    )
    user = MembersRepository(db).create(user)
    db.commit()
    return user


def update_user(user_id: int, db: Session, **fields) -> User:
    user = get_user(user_id, db)
    cedula = fields.get("cedula", user.cedula)
    email = fields.get("email", user.email)
    _validar_unicidad(db, cedula, email, excluir_id=user_id)

    password = fields.pop("password", None)
    if password:
        fields["password_hash"] = hash_password(password)

    user = MembersRepository(db).update(user, **fields)
    db.commit()
    return user


def anonymize_user(user_id: int, db: Session) -> User:
    """RN-07: borra PII de forma irreversible pero conserva la fila (y su
    `id`) para no romper la FK de `CheckIn.usuario_id` — el histórico de
    check-ins del usuario se preserva. `estado=inactivo` ya bloquea el login;
    limpiar `password_hash` también es higiene extra de credenciales."""
    user = get_user(user_id, db)
    user = MembersRepository(db).update(
        user,
        cedula=None,
        nombre=None,
        email=None,
        password_hash=None,
        estado=EstadoUsuario.inactivo,
    )
    db.commit()
    return user


def assign_membership(
    user_id: int, tipo_id: int, monto: Decimal, nota: str | None, db: Session
) -> Membership:
    get_user(user_id, db)  # 404 limpio si el usuario no existe
    membership = membership_service.create_membership(user_id, tipo_id, monto, nota, db)
    db.commit()
    return membership


def renew_membership(
    user_id: int, tipo_id: int, monto: Decimal, nota: str | None, db: Session
) -> Membership:
    get_user(user_id, db)
    membership = membership_service.renew_membership(user_id, tipo_id, monto, nota, db)
    db.commit()
    return membership


def get_membership_history(user_id: int, db: Session) -> list[Membership]:
    get_user(user_id, db)
    return membership_service.list_membership_history(user_id, db)
