# QUICKSTART de stark

El camino feliz, de principio a fin. Elige tu caso de uso **una vez** y sigue su pista lineal — sin filtrar mentalmente los otros casos en cada paso.

¿Quieres el porqué de cada decisión? → [`PRINCIPIOS.md`](PRINCIPIOS.md). ¿El detalle exhaustivo (checklists completos, las 9 secciones del design, Surface of Contact)? → [`REFERENCIA.md`](REFERENCIA.md) (la referencia). ¿Algo se trabó? → [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).

---

## Arranca

Un solo riel: los comandos `/stark-*`. No hay prompt que copiar ni nada que memorizar.

```
/stark-init
```

Te pregunta tu caso, prepara el terreno y te dice **textualmente** cuál es el siguiente comando. De ahí avanzas comando por comando, aprobando cada gate humano. Eso es todo.

---

## 1. Elige tu caso de uso

| Tu situación | Caso | Empiezas con |
|---|---|---|
| Construir desde cero (tienes entrevistas, formularios, imágenes) | **Nuevo** | material en `docs/inputs/` |
| Reescribir/modernizar un legacy (tienes código + arqueología) | **Reingeniería** | análisis en `docs/analysis/` + código legacy |
| Sistema en producción + agregar un feature sin romper nada | **Mantenimiento** | `docs/features/<slug>/intent.md` |
| Solo un mockup desplegable para validar una idea con el cliente | **Prototipo** | un requirements ligero |

`/stark-init` te hace esta misma pregunta y prepara el terreno. El árbol de decisión completo (casos mixtos, legacy + feature nuevo) está en la referencia → [elegir caso](REFERENCIA.md#1-fase-1-init--elegir-caso-de-uso).

---

## 2. Tu pista lineal

Cada caso es una sola secuencia de comandos, de arriba a abajo. `[ ]` = opcional.

### Nuevo

1. `/stark-init` — confirma caso, deja `docs/inputs/` listo.
2. **Pon tu material** (entrevistas, notas, imágenes, PDFs) en `docs/inputs/`. Sin esto, requirements no tiene de dónde partir.
3. `/stark-requirements` — material → `docs/requirements.md` (EARS). ✋
4. `[ ]` `/stark-prototype` — si hay UI: mockup desplegable + loop con cliente. ✋ cliente.
5. `/stark-design` — requirements → `docs/design.md` (9 secciones). ✋
6. `/stark-tasks` — design → `docs/tasks.md` (**walking skeleton + rebanadas verticales**). ✋
7. `/stark-build` — ejecuta **un Slice por sesión**; tú revisas y apruebas. ✋ por lote.

### Reingeniería

Igual que **Nuevo**, con dos diferencias:
- En el paso 1, `/stark-init` genera el **sustrato** (`CLAUDE.md`, `BIG_PICTURE.md`, `REGLAS_DE_NEGOCIO.md`) corriendo `onboarding` y `reglas-negocio`.
- En el paso 2, `/stark-requirements` levanta los requirements **desde el código legacy** (`docs/analysis/` + el código).

Secuencia: `init (+sustrato)` → `requirements` → `[prototype]` → `design` → `tasks` → `build`. Misma entrega vertical.

### Mantenimiento

Agregar un feature a producción sin romper lo que funciona. Trabajas sobre el repo del sistema, no un repo nuevo.

1. `/stark-init` — genera el **sustrato** y crea `docs/features/<slug>/intent.md` (descríbelo en lenguaje de negocio).
2. `/stark-requirements <slug>` — intent + código → `docs/features/<slug>/requirements.md`: el **delta**, con Surface of Contact e Invariantes Preservadas. ✋
3. `[ ]` `/stark-prototype <slug>` — si el feature trae UI nueva. ✋ cliente.
4. `/stark-design <slug>` — delta sobre la arquitectura **heredada e inmutable** → `docs/features/<slug>/design.md`. ✋
5. `/stark-tasks <slug>` — **orden por riesgo**: Regression Shield primero, No-Regression Validation al final. ✋
6. `/stark-build <slug>` — un lote por sesión; las tareas de blindaje y la validación final van **solas**. ✋ por lote.

> Mantenimiento no cierra sin la **No-Regression Validation** final. Es no negociable.

### Prototipo

1. `/stark-init` — caso prototipo.
2. `/stark-requirements` — requirements ligero (lo mínimo para inferir pantallas).
3. `/stark-prototype` — mockup desplegable + loop con cliente vía `validation-log`.

Paras ahí (el prototipo era el encargo) o sigues con `design → tasks → build` si decides construir.

---

## 3. Cheat sheet de comandos

| Fase | Comando |
|---|---|
| 1. Init / elegir caso | `/stark-init` |
| 2. Requirements | `/stark-requirements` |
| 3. Prototipo | `/stark-prototype` |
| 4. Design | `/stark-design` |
| 5. Tasks | `/stark-tasks` |
| 6. Build (una rebanada) | `/stark-build` |
| Revisar diff vs. principios | `/stark-review` |
| Auditar repo | `/stark-audit` |

Las fases 1–6 son la columna vertebral; `/stark-review` y `/stark-audit` son transversales (úsalos cuando quieras). El prototipo (fase 3) es opcional pero ciudadano de primera.

---

## 4. Los gates humanos (la regla que sostiene todo)

✋ **Una fase a la vez. Tú apruebas entre cada una.** Saltarte un gate propaga el error 10× a la fase siguiente.

- Después de **requirements**, **design** y **tasks**: revísalos y di explícitamente "aprobado, sigue".
- En **prototipo**: aprueba el **cliente**, no tú.
- En **build**: revisas **cada lote** — corres los tests, verificas el criterio de hecho, y **solo tú** marcas `[x]`. El agente nunca se auto-aprueba.
- El gate de build valida **software funcionando** (el sistema corre y el Slice es demostrable de punta a punta), no solo código que compila.

Los checklists de validación de cada fase (qué revisar antes de aprobar) están completos en la referencia: [requirements](REFERENCIA.md#2-fase-2-requirements-levantamiento) · [prototipo](REFERENCIA.md#3-fase-3-prototipo-visual-opcional) · [design](REFERENCIA.md#4-fase-4-design-diseño-técnico) · [tasks](REFERENCIA.md#5-fase-5-tasks-descomposición) · [build](REFERENCIA.md#6-fase-6-build--ejecución-del-código).

---

Si esto se te quedó corto en algún paso, el detalle está en [`REFERENCIA.md`](REFERENCIA.md). Si algo no salió como debía, [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md). Una fase a la vez, una rebanada por sesión, tú apruebas.
