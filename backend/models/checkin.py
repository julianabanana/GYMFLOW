"""
Tabla `checkins` — dueño: checkin (ver tech-stack.md). Registro inmutable.
"""
import enum

from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Boolean, func

from core.database import Base


class ResultadoCheckin(str, enum.Enum):
    exitoso = "exitoso"
    denegado = "denegado"


class CheckIn(Base):
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    fecha_hora = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    resultado = Column(Enum(ResultadoCheckin), nullable=False)
    # Distingue al menos: MEMBRESIA_VENCIDA, SIN_VISITAS, YA_INGRESO_HOY,
    # DISPOSITIVO_BLOQUEADO (ver 002-acceso-denegado).
    razon_denegacion = Column(String(50), nullable=True)
    # Solo se llena en check-in de invitado (ver 006-checkin-invitado).
    titular_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    # true = acceso ya concedido para el día calendario de fecha_hora (001):
    # un reingreso exitoso el mismo día no crea otro is_active=true ni
    # descuenta visita. La query siempre filtra también por fecha (ver
    # checkin/repository.py) — un is_active=true de un día anterior no cuenta.
    is_active = Column(Boolean, nullable=False, default=False)

    # Índice único parcial (usuario_id, DATE(fecha_hora)) WHERE is_active=true
    # se agrega en la migración de Alembic de la feature 001 (anti doble
    # check-in concurrente, RN-02).
