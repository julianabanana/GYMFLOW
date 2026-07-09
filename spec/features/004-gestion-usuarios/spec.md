# 004 · Gestión de usuarios y membresías

**Estado:** propuesta

**Traza:** HU-07 · RN-07, RN-12 · RF-10, RF-09 · depende de `003-autenticacion-segura`

> **Fusión (decisión del equipo):** esta feature originalmente solo cubría el CRUD de `User`. Se le fusionó lo que iba a ser una feature aparte ("013 · Renovación de membresía") porque, técnicamente, **asignar la primera membresía a alguien** y **renovarle una nueva** son la misma operación de fondo (crear una fila `Membership`) — no tenía sentido separarlas en dos specs distintas. Queda todo aquí, distinguiendo los dos casos de uso donde sí difieren.
>
> **Sin HU de origen para la parte de renovación** — el equipo confirmó que nunca se pensó una historia de usuario para "quién cobra y renueva" ("no tenemos historias de usuario, no pensamos lo suficiente en eso"). Esta parte llena un hueco real: **RN-06** ("los cambios de un tipo de membresía... aplican al **siguiente ciclo**") asume que existe un mecanismo para crear ese siguiente ciclo, y antes de esta fusión ningún RF/HU lo definía.

## Qué hace

Da al **Staff** (Empleado/Administrador) un CRUD de usuarios, y dos formas de que un usuario tenga una `Membership`:

1. **Primera asignación** — un usuario (Prospecto recién afiliado, o Miembro nuevo) no tiene ninguna `Membership` previa; el Staff le crea la primera, vinculando un `MembershipType`.
2. **Renovación** — un socio con `Membership` anterior (vigente o vencida) paga en ventanilla; el Staff confirma el pago (fuera del sistema — GymFlow no procesa pagos, ver `mission.md`) y crea una **`Membership` nueva** (fila distinta, no se edita la anterior — ver decisión abajo), usando los valores del `MembershipType` **vigentes en el momento de renovar** (RN-06: pueden ser distintos a los del ciclo anterior, porque los tipos y precios cambian con el tiempo).

Incluye también el borrado de usuarios respetando la preservación del histórico de check-ins.

## Por qué

Sin altas manuales no hay miembros que validar en el kiosko; es la base operativa del Sprint 1 (HU-07) y prerrequisito real de los flujos de check-in. La renovación, además, es la operación más frecuente de un gimnasio real (cada socio la usa mensual/trimestral/anualmente) y sin ella RN-06 no tiene forma de dispararse nunca.

> **No confundir con el flujo de entrada diario:** la renovación es una transacción de pago, ocasional (una vez por ciclo). El check-in del día a día (`001`/`012`) sigue siendo 100% self-service — escanea QR (o cédula de respaldo), pasa los filtros, entra. El staff no interviene ahí; solo aparece en esta feature porque alguien tiene que recibir el pago.

## Decisiones ya confirmadas (por el equipo, en conversación)

- **Renovar crea una `Membership` nueva, no sobreescribe la existente.** La fila anterior queda intacta como histórico (`estado = Vencida` cuando corresponda). Razón: los tipos de membresía y sus precios cambian con el tiempo (RN-06) — sobreescribir perdería el registro de qué precio/plan tenía el socio en cada ciclo pasado. Consistente con RN-07 (preservar histórico) y con lo que `010` necesita para reportar por ciclo.
- **Pago en ventanilla.** El pago ocurre en un punto de atención física, fuera del sistema.

## Criterios de aceptación

### CRUD de usuarios
- [ ] Un Staff autenticado puede **crear** un usuario (`cédula`, `nombre`, `email`, `rol`, `estado`) y el perfil queda persistido (RF-10).
- [ ] Un Staff puede **leer, listar y editar** usuarios.
- [ ] Al **eliminar** un usuario, su información personal (`cédula`, `nombre`, `email`) se borra de forma irreversible, **pero** sus registros de `CheckIn` históricos se preservan (RN-07). *Comprobable: tras el borrado, los `CheckIn` del usuario siguen existiendo para estadística.*
- [ ] Si se crea un usuario Empleado/Administrador con credenciales, la contraseña se guarda **hasheada** (RN-12).
- [ ] Todos los endpoints exigen rol Empleado/Administrador (RBAC, RF-09); sin token válido → 401/403.

### Primera asignación de membresía
- [ ] Un Staff puede **asignar una membresía** a un usuario **sin `Membership` previa**, vinculando un `MembershipType` existente y creando su `Membership` con saldos iniciales (`visitas_restantes`, `cupo_invitados_restantes` = totales del tipo).

### Renovación de membresía
- [ ] Un Staff busca un socio existente (reutiliza `008`) y ve su membresía actual (vigente o vencida) y su historial de membresías anteriores.
- [ ] El Staff confirma la renovación indicando el `MembershipType` a aplicar (puede ser el mismo que tenía o uno distinto — ver duda abierta sobre upgrade/downgrade).
- [ ] Al confirmar, el sistema crea una **`Membership` nueva** (fila distinta): `fecha_inicio` = hoy, `fecha_vencimiento` = `fecha_inicio + duracion_dias`, `visitas_restantes` = `visitas_totales` del tipo, `cupo_invitados_restantes` = `cupo_invitados` del tipo, `estado` = Activa, tomando los valores del `MembershipType` **vigentes en el momento de renovar**.
- [ ] La `Membership` anterior **no se modifica** — queda como registro histórico, consultable en reportes (`010`) y en el historial del socio.
- [ ] Ambas operaciones (primera asignación y renovación) son **atómicas** (RN-10): si falla, no queda una `Membership` a medias.
- [ ] El historial de `CheckIn` del socio **no se altera** por ninguna de las dos operaciones.

## Fuera de alcance

- **Autenticación** (login, emisión de JWT, RBAC) → `003-autenticacion-segura`.
- **CRUD de tipos de membresía** (`MembershipType`) → `009-configuracion-tipos-membresia` (aquí se **usan**, no se definen).
- **Procesamiento de pagos** — no hay pasarela, no se factura (misión). El staff confirma el pago fuera del sistema.
- **Renovación automática** (cron/recurrente) — manual, iniciada por el staff.

## Duda abierta (a confirmar, no invento la respuesta)

- **RN-07 (borrado de usuario):** se implementa como **anonimización/tombstone** de la fila `User` (se vacía la PII y se conserva el `id`) para no romper la FK `CheckIn.usuario_id`. Alternativa (borrado físico con `usuario_id` nulo) descartada por trazabilidad. Confirmar con el equipo.
- **Granularidad del permiso de renovación:** ¿cualquier Empleado puede renovar, o es un permiso aparte dentro de RBAC (ej. solo quien atiende ventanilla/caja)? El RBAC actual (`003`) solo distingue Empleado/Administrador a nivel general. Confirmar si vale la pena para el alcance académico o si el rol genérico basta.
- **¿Se puede cambiar de `MembershipType` al renovar (upgrade/downgrade)?** No hay dato de origen. Si no se permite, simplificar a "renovar con el mismo tipo que ya tenía".
- **¿Puede el socio renovar antes de que venza (renovación anticipada)?** ¿La nueva `Membership` empieza el día que renueva, o el día siguiente al vencimiento de la anterior (para no perder días pagados)? No especificado — confirmar.
- **¿Registro de "pago recibido"?** ¿El staff deja alguna anotación/comprobante (aunque sea texto libre), o la renovación en sí ya implica que el pago se verificó fuera del sistema? Propuesta mínima: no agregar campo de pago — confirmar si el equipo quiere más trazabilidad que eso.
