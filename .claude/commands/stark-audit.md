---
description: Transversal · Audita el repo completo contra los principios de stark.
---

Lee `docs/documentacion/PRINCIPIOS.md` y aplica sus reglas como restricciones duras.

Audita TODO el repositorio, no solo el diff. Evalúa el estado actual contra los 4 principios, cazando deuda sistémica:

- **Sobre-ingeniería sistémica** — abstracciones anticipadas, capas de indirección sin pago, flexibilidad especulativa, opciones/parámetros sin uso real.
- **Código muerto** — funciones, módulos, dependencias, flags y rutas inalcanzables o sin referencia.
- **Despliegue ritualizado** — pasos, scripts o configuraciones que se arrastran sin justificación vigente.
- **Documentación con relleno** — texto que no gana su lugar; redundancias con el código o entre documentos.
- **Divergencias con la metodología** — fases de stark omitidas, artefactos faltantes o inconsistentes con su fase.

Entrega un informe priorizado (mayor a menor severidad): para cada hallazgo indica severidad, ubicación (archivo:línea o módulo) y el recorte sugerido. NO modifiques nada sin aprobación explícita.
