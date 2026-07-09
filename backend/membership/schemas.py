"""
Schemas Pydantic de membership (entrada/salida de API). Se agregan al implementar
spec/features/001, 007, 009/. Toda validación de entrada vive aquí, nunca a
mano en el router (AGENTS.md).
"""
from datetime import date

from pydantic import BaseModel


class MembershipSummary(BaseModel):
    """Mínimo del semáforo (001); el detalle completo lo amplía 007."""

    tipo: str
    visitas_restantes: int
    fecha_vencimiento: date
