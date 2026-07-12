# 010 · Reportes de asistencia — Tareas

- [x] `checkin/service.py`: `get_attendance(fecha_inicio, fecha_fin, db)` sobre la tabla propia `CheckIn` (RF-12).
- [x] Migración: índice por `fecha_hora` en `CheckIn` (`b4e1a7c0d9f2`).
- [x] `reports/schemas.py`: `AttendanceRow`, `ReportFilters`.
- [x] `reports/service.py`: `generate(...)` (orquesta checkin + enriquece con members/membership).
- [x] `reports/service.py`: `export(...)` a XLSX (openpyxl) y CSV (RF-13).
- [x] `reports/router.py`: `GET /reportes/attendance` y `.../export` con `require_role(administrador)` (RF-09).
- [x] Enriquecimiento en lote (`get_users_by_ids` / `get_type_names_by_user_ids`, evita N+1).
- [x] Frontend: selector de rango + tabla + exportación (`AttendanceReportPage.tsx`, `adminOnly`).
- [x] Discrepancia `reports/repository` vs. límite duro resuelta: `reports` no usa repository, orquesta vía services; `tech-stack.md` actualizado.
- [x] Tests: filtro por rango, rango vacío, export XLSX/CSV con mismos datos, RBAC solo Admin, inmutabilidad (no escribe). 11 tests, suite 148/148.
- [x] Validar contra los criterios de aceptación de `spec.md`.
- [x] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.

> **Nota de prefijo:** el plan mencionaba `/reports/attendance`, pero el router
> ya existía con prefijo `/reportes` (español, consistente con `/membresias`,
> `/usuarios`). Se implementó bajo `/reportes/attendance` para no romper esa
> convención.
>
> **Decisión de "tipo de membresía":** el reporte muestra el tipo del plan MÁS
> RECIENTE del socio (snapshot pragmático, batch sin N+1), no el vigente en la
> fecha exacta de cada asistencia. Si el equipo lo pide, es un ajuste de
> `membership.service.get_type_names_by_user_ids` sin cambio de modelo.
