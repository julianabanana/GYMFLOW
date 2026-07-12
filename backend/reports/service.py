"""
Servicio de reports — 010-reportes-asistencia.

`reports` no posee tablas propias (no tiene repository con queries): orquesta.
Pide las asistencias a `checkin.service` (dueño de `checkins`) y las enriquece
con `members.service` (nombres) y `membership.service` (tipo de plan), sin
cruzar ninguna tabla ajena (regla de módulos, AGENTS.md). Solo lectura: nunca
escribe sobre la fuente inmutable `CheckIn` (RF-05).

Regla de módulos (no negociable, AGENTS.md): este service es el ÚNICO punto de
entrada que otros módulos pueden llamar para leer/mutar datos de reports.
"""
import csv
import io

import checkin.service as checkin_service
import members.service as members_service
import membership.service as membership_service
from reports.schemas import AttendanceRow, ReportFilters

_COLUMNAS = ("Fecha y hora", "Usuario", "Resultado", "Tipo de membresía", "Titular")


def generate(filtros: ReportFilters, db) -> list[AttendanceRow]:
    """Tabla consolidada de asistencias del rango (RF-12). Un rango sin
    registros devuelve una lista vacía (no error)."""
    asistencias = checkin_service.get_attendance(filtros.fecha_inicio, filtros.fecha_fin, db)
    if not asistencias:
        return []

    user_ids = {c.usuario_id for c in asistencias}
    titular_ids = {c.titular_id for c in asistencias if c.titular_id is not None}

    usuarios = members_service.get_users_by_ids(list(user_ids | titular_ids), db)
    tipos = membership_service.get_type_names_by_user_ids(list(user_ids), db)

    filas: list[AttendanceRow] = []
    for c in asistencias:
        usuario = usuarios.get(c.usuario_id)
        titular = usuarios.get(c.titular_id) if c.titular_id is not None else None
        filas.append(
            AttendanceRow(
                fecha_hora=c.fecha_hora,
                usuario_id=c.usuario_id,
                usuario_nombre=usuario.nombre if usuario else None,
                resultado=c.resultado.value,
                tipo_membresia=tipos.get(c.usuario_id),
                titular_nombre=titular.nombre if titular else None,
            )
        )
    return filas


def _fila_valores(row: AttendanceRow) -> list[str]:
    return [
        row.fecha_hora.isoformat(),
        row.usuario_nombre or "",
        row.resultado,
        row.tipo_membresia or "",
        row.titular_nombre or "",
    ]


def export(filtros: ReportFilters, formato: str, db) -> bytes:
    """Exporta el MISMO dataset de `generate` a XLSX u CSV (RF-13). `formato`
    ya viene validado por el router (`xlsx`|`csv`)."""
    filas = generate(filtros, db)
    if formato == "csv":
        return _to_csv(filas)
    return _to_xlsx(filas)


def _to_csv(filas: list[AttendanceRow]) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(_COLUMNAS)
    for row in filas:
        writer.writerow(_fila_valores(row))
    # BOM utf-8 para que Excel abra bien los acentos al hacer doble clic.
    return buffer.getvalue().encode("utf-8-sig")


def _to_xlsx(filas: list[AttendanceRow]) -> bytes:
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "Asistencias"
    ws.append(list(_COLUMNAS))
    for row in filas:
        ws.append(_fila_valores(row))
    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()
