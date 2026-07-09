"""
Tabla `checkin_device_locks` — dueño: checkin (spec/features/002-acceso-denegado,
RN-03). Contador de intentos fallidos por dispositivo en tabla (no en memoria),
para ser correcto con múltiples workers de uvicorn en Docker.
"""
from sqlalchemy import Column, Integer, String, DateTime

from core.database import Base


class CheckinDeviceLock(Base):
    __tablename__ = "checkin_device_locks"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(100), nullable=False, unique=True, index=True)
    intentos_fallidos = Column(Integer, nullable=False, default=0)
    # Inicio de la ventana deslizante de ≤5 min (RN-03); None si no hay fallos activos.
    ventana_inicio = Column(DateTime(timezone=True), nullable=True)
    # None si no está bloqueado; si tiene fecha futura, el kiosko rechaza check-ins.
    bloqueado_hasta = Column(DateTime(timezone=True), nullable=True)
