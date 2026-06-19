---
description: Transversal · Revisa el diff actual contra PRINCIPIOS.md (sobre-ingeniería + seguridad).
---

Lee `docs/documentacion/PRINCIPIOS.md` y aplica sus reglas como restricciones duras.

Toma el diff actual: ejecuta `git diff` (cambios sin commitear) y, si aplica, `git diff --staged`. Revisa SOLO lo que cambió.

Evalúa el diff contra los 4 principios, con foco especial en:

- **Escalera YAGNI** — ¿cada línea gana su lugar? Caza: flexibilidad especulativa, abstracción anticipada, parámetros/opciones sin uso real, código muerto, dependencias evitables. Si una línea no se justifica, recórtala.
- **Seguridad por diseño** — validación de entradas, manejo de errores, secretos fuera del código, riesgo de pérdida de datos.

Reporta hallazgos accionables priorizados (mayor a menor severidad): qué, dónde (archivo:línea) y la corrección sugerida. NO reescribas código sin permiso explícito.
