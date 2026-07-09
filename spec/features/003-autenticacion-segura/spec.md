# 003 · Autenticación segura

**Estado:** propuesta

**Traza:** HU-10 · RN-11, RN-12 · RF-09 · RNF seguridad (HTTPS/TLS), límite duro "JWT propio, sin OAuth server"

## Qué hace

Permite a **Empleado** y **Administrador** iniciar sesión con credenciales y obtener un **JWT propio** que autoriza el acceso al backoffice y a los endpoints de API según su **rol** (RBAC). Las sesiones expiran por inactividad y las contraseñas se guardan siempre con hash.

El flujo de **Miembro/Invitado en el kiosko no requiere login** (así lo fija la misión): el check-in por cédula/nombre es público a nivel de usuario y se protege por dispositivo (RN-03), no por JWT. Esto sigue siendo cierto para el kiosko. El Miembro sí puede loguearse por fuera del kiosko, en el **portal web** (`011-portal-miembro-autenticacion`), con su propio esquema de sesión (access + refresh token, distinto al de Staff/Administrador porque su propósito es otro: consulta de cuenta y habilitar check-in por QR, no acceso al backoffice). El Invitado nunca tiene login, en ningún canal.

## Por qué

Las funciones administrativas (CRUD de usuarios, configuración, reportes) deben quedar restringidas por rol (RF-09). Es prerrequisito de las features `004`, `009` y `010`.

## Criterios de aceptación

- [ ] Un Empleado/Administrador con credenciales válidas recibe un **JWT firmado** que incluye su `rol` y una expiración (`exp`).
- [ ] Credenciales inválidas → **401** sin revelar si el usuario existe.
- [ ] Un endpoint de backoffice sin token válido → **401**; con token válido pero **rol insuficiente** → **403** (RBAC, RF-09).
- [ ] La sesión expira tras **30 min de inactividad** (RN-11).
- [ ] Las contraseñas se almacenan **hasheadas** (bcrypt/argon2), nunca en texto plano (RN-12). *Comprobable: inspección de la tabla no muestra la contraseña en claro.*
- [ ] Los endpoints del **kiosko** (check-in, cortesía, invitado, resumen) funcionan **sin** JWT de usuario (misión).

## Fuera de alcance

- **CRUD** de usuarios/altas de staff → `004-gestion-usuarios` (esta feature solo autentica y autoriza).
- **OAuth2 / Authorization Server / login federado / multi-SecurityFilterChain** → prohibido por la constitución.
- Recuperación de contraseña / MFA → no está en `docs/`; no se implementa.
- **Duda abierta:** "30 min de inactividad" se implementa como **expiración deslizante** de 30 min (se renueva con cada request autenticada). Confirmar si el equipo prefiere refresh token explícito.
