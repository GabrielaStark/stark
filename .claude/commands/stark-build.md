---
description: Fase 6 · Ejecuta una rebanada vertical / lote, con gate humano que valida software funcionando.
argument-hint: <slice o rango de tareas, ej. 'Slice 1' o '4-7'>
---

Lee `docs/documentacion/PRINCIPIOS.md` y aplica sus reglas como restricciones duras durante toda la ejecución.

Si existe `CONSTITUTION.md` en la raíz, léelo también UNA vez al inicio: sus estándares de código (§4), umbrales de calidad (§5), seguridad (§6), patrones (§2) y vetos (§3) son restricciones duras al escribir código. Antes de entregar el lote, verifica los umbrales de §5 con los comandos que declara. Si una tarea exige contradecir la constitución, DETENTE y repórtalo como alerta crítica — nunca la violes en silencio.

Vas a ejecutar UN lote. La unidad de ejecución es siempre un lote:
- Modo vertical: un lote = UNA rebanada vertical (un Slice completo, demostrable de punta a punta).
- Modo layered o mantenimiento por riesgo: un lote = un grupo contiguo de tareas de la misma capa/sección.

`$ARGUMENTS` indica el slice o rango de tareas a ejecutar. Si está vacío, identifica el siguiente lote no completado en `tasks.md` y confírmalo antes de proceder.

Pre-condición: `tasks.md` debe estar aprobado. Verifícalo: `python3 .claude/scripts/sello.py verificar-doc <ruta-del-tasks>`. En **ruta corta** de mantenimiento no hay `tasks.md`: las tasks viven dentro del documento único — verifica ese: `verificar-doc docs/features/<slug>/requirements.md`. Si falla, detente: se re-aprueba y re-sella antes de ejecutar. La primera vez en el repo, instala también el candado de push: `python3 .claude/scripts/sello.py instalar-hook`.

SEGURIDAD (dura, Principio 2): valida entradas en el servidor, parametriza queries/comandos (nunca concatenar input), autorización por rol en cada endpoint nuevo, secretos solo por env vars, datos sensibles fuera de logs y de mensajes de error, ningún `catch` vacío.

PRINCIPIO DE CORRECCIÓN (duro):
- Lee la spec COMPLETA del lote (requirements + design) UNA vez al inicio, con el contexto íntegro a la vista. No fragmentes la lectura.
- No infieras lo que no está escrito. Si falta información, detente y pregunta.
- No auto-marques `[x]`. El humano revisa y marca.

Aísla las tareas de validación: van solas, nunca loteadas. En mantenimiento, Regression Shield y No-Regression Validation también van solas.

GATE HUMANO por lote: valida SOFTWARE FUNCIONANDO. El sistema corre y la feature del lote es demostrable de punta a punta — no basta con código que compila. Entrega al humano cómo verificarlo y espera su revisión antes de cerrar el lote.

SELLO DEL LOTE (cadena de evidencia): cuando el humano aprueba el lote, deja el working tree limpio (todo commiteado, receipts incluidos) y sella el commit validado: `python3 .claude/scripts/sello.py sellar-lote <id> --por "<nombre>"` — usa `<n>` en construcción y `<feature>-<n>` en mantenimiento, para que los lotes de features distintas no colisionen (agrega `--invariantes` solo si la validación de invariantes pasó). El sello es un **annotated tag** `stark-lote-<id>` sobre el commit exacto: no modifica el árbol validado y cubre todos los commits del lote (el sellado y sus ancestros). El push se protege solo — el hook valida **cada commit de las refs que se empujan**: código sin sellar no pasa (ni empujando otra rama por nombre, ni escondido tras un revert), el árbol debe estar limpio, y **la evidencia viaja con el código**: el tag debe ir en el mismo push o ya existir en el remoto — `git push <remoto> <rama> refs/tags/stark-lote-<id>`. Marcar checkboxes `[x]` en tasks.md NO invalida su sello (canonicalización checkbox-v1); cualquier otro cambio al plan, sí. Si algo cambió después de la validación, se revalida — no se entrega.
