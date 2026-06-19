---
description: Fase 1 · Arranca un proyecto stark - detecta el caso de uso y enruta el flujo. Genera el sustrato en reingeniería y mantenimiento.
argument-hint: [nuevo|reingenieria|mantenimiento|prototipo]
---

Lee `docs/documentacion/PRINCIPIOS.md` y aplica sus reglas como restricciones duras durante toda la fase.

Este comando arranca un proyecto stark (fase 1: init). NO produce specs: orquesta el setup y deja claro el siguiente paso. Un único comando cubre los 4 casos de uso — no hay comandos duplicados por pipeline.

## 1. Determina el caso de uso

Tómalo de `$ARGUMENTS`. Si viene vacío o ambiguo, pregunta al humano cuál aplica:

- **nuevo** — proyecto desde cero, sin código previo.
- **reingenieria** — existe código vivo que se va a reescribir.
- **mantenimiento** — código en producción al que se le agrega una feature sin romperlo.
- **prototipo** — mockup interactivo rápido para validar, sin construir el sistema completo.

## 2. Explica la secuencia del caso elegido

Muestra la secuencia stark del caso ([ ] = opcional) y cuál comando sigue:

| Caso | Secuencia |
|------|-----------|
| nuevo | init → requirements → [prototype] → design → tasks → build |
| reingeniería | init (+sustrato) → requirements → [prototype] → design → tasks → build |
| mantenimiento | init (+sustrato) → requirements (delta) → [prototype] → design (delta) → tasks (riesgo) → build |
| prototipo | init → requirements (ligero) → prototype (paras ahí o sigues) |

## 3. Ejecuta el setup del caso

- **NUEVO** → asegura que exista `docs/inputs/` para el material de levantamiento (transcripciones, notas, entrevistas). Siguiente: `/stark-requirements`.

- **REINGENIERÍA** → genera el sustrato sobre el código vivo: corre la skill `onboarding` (produce `docs/CLAUDE.md` y `docs/BIG_PICTURE.md`) y la skill `reglas-negocio` (produce `docs/REGLAS_DE_NEGOCIO.md`). Siguiente: `/stark-requirements`.

- **MANTENIMIENTO** → genera el sustrato (skills `onboarding` + `reglas-negocio`) y crea `docs/features/$ARGUMENTS/intent.md` desde `templates/intent.md` para capturar la intención de la feature. Siguiente: `/stark-requirements`.

- **PROTOTIPO** → mantén requirements en modo ligero y salta directo a `/stark-prototype`.

## 4. Cierra

Confirma qué se generó y enuncia explícitamente el siguiente comando a invocar.
