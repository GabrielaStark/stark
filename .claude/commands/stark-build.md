---
description: Fase 6 · Ejecuta una rebanada vertical / lote, con gate humano que valida software funcionando.
argument-hint: <slice o rango de tareas, ej. 'Slice 1' o '4-7'>
---

Lee `docs/documentacion/PRINCIPIOS.md` y aplica sus reglas como restricciones duras durante toda la ejecución.

Vas a ejecutar UN lote. La unidad de ejecución es siempre un lote:
- Modo vertical: un lote = UNA rebanada vertical (un Slice completo, demostrable de punta a punta).
- Modo layered o mantenimiento por riesgo: un lote = un grupo contiguo de tareas de la misma capa/sección.

`$ARGUMENTS` indica el slice o rango de tareas a ejecutar. Si está vacío, identifica el siguiente lote no completado en `tasks.md` y confírmalo antes de proceder.

PRINCIPIO DE CORRECCIÓN (duro):
- Lee la spec COMPLETA del lote (requirements + design) UNA vez al inicio, con el contexto íntegro a la vista. No fragmentes la lectura.
- No infieras lo que no está escrito. Si falta información, detente y pregunta.
- No auto-marques `[x]`. El humano revisa y marca.

Aísla las tareas de validación: van solas, nunca loteadas. En mantenimiento, Regression Shield y No-Regression Validation también van solas.

GATE HUMANO por lote: valida SOFTWARE FUNCIONANDO. El sistema corre y la feature del lote es demostrable de punta a punta — no basta con código que compila. Entrega al humano cómo verificarlo y espera su revisión antes de cerrar el lote.
