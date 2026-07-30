---
description: Transversal · Revisa el diff actual contra PRINCIPIOS.md (sobre-ingeniería + seguridad).
---

Lee `docs/documentacion/PRINCIPIOS.md` y aplica sus reglas como restricciones duras.

Toma el diff actual: ejecuta `git diff` (cambios sin commitear) y, si aplica, `git diff --staged`. Revisa SOLO lo que cambió.

Evalúa el diff contra los 4 principios, con foco especial en:

- **Escalera YAGNI** — ¿cada línea gana su lugar? Caza: flexibilidad especulativa, abstracción anticipada, parámetros/opciones sin uso real, código muerto, dependencias evitables. Si una línea no se justifica, recórtala.
- **Seguridad por diseño** — caza en el diff:
  - Entradas sin validar del lado servidor (la validación de cliente no basta; el servidor es la verdad).
  - Queries o comandos construidos concatenando input (inyección SQL/shell/path) — siempre parametrizar.
  - Autorización ausente o solo en UI: cada endpoint/acción nueva verifica rol/permiso en servidor.
  - Secretos o credenciales en código, config versionada, fixtures o logs.
  - Datos sensibles del dominio en logs o mensajes de error; errores que exponen stack/detalles internos al usuario.
  - `catch` vacíos o manejo de errores que deja datos a medio escribir (pérdida de datos).

Si existe `CONSTITUTION.md` en la raíz, revisa el diff también contra ella: librerías vetadas (§3), patrones obligatorios (§2), estándares de código (§4) y seguridad (§6). Toda violación de la constitución es hallazgo de severidad ALTA.

Reporta hallazgos accionables priorizados (mayor a menor severidad): qué, dónde (archivo:línea) y la corrección sugerida. NO reescribas código sin permiso explícito.
