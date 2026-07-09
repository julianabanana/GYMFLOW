# 007 · Resumen de membresía

**Estado:** propuesta

**Traza:** HU-06 · RF-04 · (integra el semáforo de `001`)

## Qué hace

Muestra al miembro el estado de su membresía: **tipo**, **fecha de vencimiento**, **estado**, **visitas restantes** y **cupos de invitado restantes**. Si al socio le quedan **≤10 días** para que venza su membresía, se muestra además un aviso con los días exactos restantes; si le quedan más de 10 días, **no se muestra ningún aviso** (no tiene sentido recordarle a alguien con 200 días restantes que su membresía va a vencer).

## Por qué

El usuario debe recibir feedback inmediato sobre su cuenta (problemática §1: falta de feedback), evitando las discusiones incómodas de la validación manual. Es puramente informativo. **Cambio respecto a la versión anterior:** se quitó el campo "próximo pago" — GymFlow no procesa pagos (misión), así que mostrar una fecha de "pago" era engañoso; lo que sí puede calcular con certeza es cuánto falta para que la membresía venza (`fecha_vencimiento - hoy`), que es un dato real del sistema.

## Criterios de aceptación

- [ ] Dado un miembro con membresía activa, cuando consulta su resumen (o completa un check-in exitoso), entonces se muestran: tipo de membresía, `fecha_vencimiento`, estado, `visitas_restantes` y `cupo_invitados_restantes` (RF-04).
- [ ] Se calcula `dias_restantes = fecha_vencimiento - hoy` (no se almacena, se calcula en cada consulta).
- [ ] Si `dias_restantes <= 10` (y `dias_restantes >= 0`, membresía aún activa) → se muestra un aviso, ej. *"Tu membresía vence en {dias_restantes} días ({fecha_vencimiento})"*.
- [ ] Si `dias_restantes > 10` → **no** se muestra ningún aviso de vencimiento.
- [ ] La consulta es de **solo lectura**: no descuenta visitas ni cupos ni registra ningún `CheckIn`.
- [ ] Un miembro sin membresía activa recibe un resumen coherente (estado Vencida / sin plan) sin error — en este caso no aplica "días restantes" (ya venció), ver `002` para el mensaje de membresía vencida.

## Fuera de alcance

- **Descuento** de visitas/cupos → `001`/`006`.
- **Reportes agregados** para administración → `010-reportes-asistencia`.
- Autogeneración de **QR** del miembro → relacionado con `008`; aquí no se emite QR.
