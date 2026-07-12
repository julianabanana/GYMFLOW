# 009 · Configuración de tipos de membresía — Tareas

- [x] `membership/schemas.py`: `MembershipTypeCreate/Update` + `MembershipTypeAdminOut` (incluye `activo`) con validaciones (`visitas_totales ≥ 0`, `duracion_dias > 0`, `cupo_invitados ≥ 0`, `precio_base ≥ 0`).
- [x] `membership/repository.py`: CRUD `MembershipType` (`create/list_all/delete`) + `count_active_memberships_by_type` y `count_any_memberships_by_type`.
- [x] `membership/service.py`: `create_type/update_type/list_all_types/get_type` + `delete_type` (RN-05: desactivar bloqueado con activas; eliminar bloqueado con cualquier historial).
- [x] Confirmar snapshot de saldos en `create_membership` (RN-06) — verificado con `test_update_type_no_altera_membresia_activa_rn06`.
- [x] `membership/router.py`: CRUD bajo `/membresias/tipos` (`GET /tipos/admin`, `POST/PUT/DELETE`) protegido por `require_role(administrador)` (RF-09); se mantiene el `GET /membresias/tipos` de empleado (solo activos).
- [x] Frontend: `MembershipTypesPage.tsx` (tabla + formulario + activar/desactivar/eliminar) con motivo de bloqueo RN-05 visible; ruta en `App.tsx` y entrada `adminOnly` en `staffMenu.ts`; API en `api/members.ts`.
- [x] Tests: crear/editar/listar, bloqueo de borrado (historial) y de desactivación con membresía activa (RN-05), editar tipo no altera membresía activa (RN-06), RBAC solo Admin, validación 422. 20/20 nuevos; suite completa 137/137.
- [x] Validar contra los criterios de aceptación de `spec.md`.
- [x] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.
