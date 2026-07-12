"""
Router de reports — 010-reportes-asistencia. Reporte histórico de asistencias
filtrable por rango, exportable a XLSX/CSV. Solo rol Administrador (RF-09).
"""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from pydantic import ValidationError
from sqlalchemy.orm import Session

import reports.service as reports_service
from auth.dependencies import require_role
from core.database import get_db
from models import RolUsuario
from reports.schemas import AttendanceRow, ReportFilters

router = APIRouter(prefix="/reportes", tags=["reports"])

_ADMIN = Depends(require_role(RolUsuario.administrador))


def _filtros(fecha_inicio: date, fecha_fin: date) -> ReportFilters:
    """Construye el filtro validando el rango; traduce el error de rango a 422
    (si no, la ValidationError de pydantic escaparía como 500)."""
    try:
        return ReportFilters(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
    except ValidationError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc))

_MEDIA_TYPES = {
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "csv": "text/csv; charset=utf-8",
}


@router.get("/attendance", response_model=list[AttendanceRow])
def get_attendance_report(
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    db: Session = Depends(get_db),
    _admin=_ADMIN,
) -> list[AttendanceRow]:
    """RF-12: tabla consolidada de asistencias del rango. Un rango sin
    registros devuelve `[]` (no error)."""
    return reports_service.generate(_filtros(fecha_inicio, fecha_fin), db)


@router.get("/attendance/export")
def export_attendance_report(
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    format: str = Query("xlsx", pattern="^(xlsx|csv)$"),
    db: Session = Depends(get_db),
    _admin=_ADMIN,
) -> Response:
    """RF-13: exporta el mismo reporte a XLSX o CSV."""
    filtros = _filtros(fecha_inicio, fecha_fin)
    contenido = reports_service.export(filtros, format, db)
    nombre = f"asistencias_{fecha_inicio}_{fecha_fin}.{format}"
    return Response(
        content=contenido,
        media_type=_MEDIA_TYPES[format],
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )
