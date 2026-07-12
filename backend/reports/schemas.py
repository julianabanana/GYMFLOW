"""
Schemas Pydantic de reports (entrada/salida de API) — 010-reportes-asistencia.
Toda validación de entrada vive aquí, nunca a mano en el router (AGENTS.md).
"""
from datetime import date, datetime

from pydantic import BaseModel, model_validator


class ReportFilters(BaseModel):
    """Filtro de rango del reporte de asistencias (RF-12). Ambos extremos
    inclusive; `fecha_inicio` no puede ser posterior a `fecha_fin`."""

    fecha_inicio: date
    fecha_fin: date

    @model_validator(mode="after")
    def _rango_valido(self) -> "ReportFilters":
        if self.fecha_inicio > self.fecha_fin:
            raise ValueError("fecha_inicio no puede ser posterior a fecha_fin")
        return self


class AttendanceRow(BaseModel):
    """Una asistencia consolidada (RF-12): fecha/hora, usuario, resultado, tipo
    de plan y titular (este último solo se llena en check-in de invitado, 006)."""

    fecha_hora: datetime
    usuario_id: int
    usuario_nombre: str | None
    resultado: str
    tipo_membresia: str | None
    titular_nombre: str | None
