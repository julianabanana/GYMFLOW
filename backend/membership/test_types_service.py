"""
Tests de membership/service.py para el CRUD de tipos de membresía
(spec/features/009-configuracion-tipos-membresia). Cubre RN-05 (bloqueo de
desactivación/eliminación) y RN-06 (editar el tipo no altera contratos vigentes).
"""
from decimal import Decimal

import pytest

from membership.service import (
    MembershipTypeConHistorialError,
    MembershipTypeConMembresiaActivaError,
    MembershipTypeNoEncontradoError,
    create_membership,
    create_type,
    delete_type,
    get_type,
    list_all_types,
    update_type,
)
from models import EstadoMembresia, EstadoUsuario, MembershipType, RolUsuario, User


def _crear_tipo(db, **overrides) -> MembershipType:
    defaults = dict(
        nombre="Mensual", precio_base=Decimal("50000"), visitas_totales=30,
        cupo_invitados=1, duracion_dias=30, activo=True,
    )
    defaults.update(overrides)
    tipo = create_type(
        defaults["nombre"], defaults["precio_base"], defaults["visitas_totales"],
        defaults["cupo_invitados"], defaults["duracion_dias"], defaults["activo"], db,
    )
    db.commit()
    return tipo


def _crear_socio(db) -> User:
    user = User(
        cedula="1000000001", nombre="Ana Pérez", rol=RolUsuario.miembro,
        estado=EstadoUsuario.activo,
    )
    db.add(user)
    db.flush()
    return user


def test_create_type_guarda_todos_los_campos(db):
    tipo = _crear_tipo(db, nombre="Anual", precio_base=Decimal("500000"),
                       visitas_totales=365, cupo_invitados=4, duracion_dias=365)

    assert tipo.id is not None
    assert tipo.nombre == "Anual"
    assert tipo.visitas_totales == 365
    assert tipo.cupo_invitados == 4
    assert tipo.duracion_dias == 365
    assert tipo.activo is True


def test_list_all_types_incluye_inactivos(db):
    _crear_tipo(db, nombre="Activo")
    _crear_tipo(db, nombre="Inactivo", activo=False)

    nombres = [t.nombre for t in list_all_types(db)]

    assert nombres == ["Activo", "Inactivo"]


def test_update_type_edita_campos(db):
    tipo = _crear_tipo(db)

    actualizado = update_type(tipo.id, db, nombre="Mensual Plus", precio_base=Decimal("60000"))
    db.commit()

    assert actualizado.nombre == "Mensual Plus"
    assert actualizado.precio_base == Decimal("60000")


def test_update_type_no_altera_membresia_activa_rn06(db):
    tipo = _crear_tipo(db, visitas_totales=30)
    socio = _crear_socio(db)
    membership = create_membership(socio.id, tipo.id, Decimal("50000"), None, db)
    db.commit()
    saldo_original = membership.visitas_restantes

    update_type(tipo.id, db, visitas_totales=5)
    db.commit()
    db.refresh(membership)

    assert saldo_original == 30
    assert membership.visitas_restantes == 30  # snapshot intacto


def test_update_type_desactivar_con_membresia_activa_falla_rn05(db):
    tipo = _crear_tipo(db)
    socio = _crear_socio(db)
    create_membership(socio.id, tipo.id, Decimal("50000"), None, db)
    db.commit()

    with pytest.raises(MembershipTypeConMembresiaActivaError):
        update_type(tipo.id, db, activo=False)


def test_update_type_desactivar_sin_membresia_activa_permitido(db):
    tipo = _crear_tipo(db)
    socio = _crear_socio(db)
    membership = create_membership(socio.id, tipo.id, Decimal("50000"), None, db)
    membership.estado = EstadoMembresia.vencida  # ya no es activa
    db.commit()

    actualizado = update_type(tipo.id, db, activo=False)
    db.commit()

    assert actualizado.activo is False


def test_update_type_editar_campos_con_membresia_activa_permitido(db):
    """RN-05 solo bloquea la desactivación, no la edición de parámetros."""
    tipo = _crear_tipo(db)
    socio = _crear_socio(db)
    create_membership(socio.id, tipo.id, Decimal("50000"), None, db)
    db.commit()

    actualizado = update_type(tipo.id, db, precio_base=Decimal("70000"))
    db.commit()

    assert actualizado.precio_base == Decimal("70000")


def test_update_type_inexistente_falla(db):
    with pytest.raises(MembershipTypeNoEncontradoError):
        update_type(9999, db, nombre="X")


def test_delete_type_sin_uso_permitido(db):
    tipo = _crear_tipo(db)

    delete_type(tipo.id, db)
    db.commit()

    with pytest.raises(MembershipTypeNoEncontradoError):
        get_type(tipo.id, db)


def test_delete_type_con_historial_falla(db):
    tipo = _crear_tipo(db)
    socio = _crear_socio(db)
    membership = create_membership(socio.id, tipo.id, Decimal("50000"), None, db)
    membership.estado = EstadoMembresia.vencida  # histórica, ya no activa
    db.commit()

    # count_active = 0 (se podría desactivar), pero count_any > 0 → no se borra.
    with pytest.raises(MembershipTypeConHistorialError):
        delete_type(tipo.id, db)


def test_delete_type_inexistente_falla(db):
    with pytest.raises(MembershipTypeNoEncontradoError):
        delete_type(9999, db)
