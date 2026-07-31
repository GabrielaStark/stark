# stark

> Especificación exhaustiva, implementación mínima. Especifica todo, construye lo mínimo.
> 
> Por [@iamgabstark_](https://iamgabstark.com/)
> 
>  · [MARK — la metodología](https://iamgabstark.com/mark.html) · [stark — el framework](https://iamgabstark.com/stark.html) · [Principios](docs/documentacion/PRINCIPIOS.md)


**MARK integra SDD para especificar, YAGNI para limitar y RDD para demostrar que lo validado es exactamente lo entregado. stark convierte ese método en un workflow ejecutable para agentes.**

En la práctica: stark convierte Claude Code en un equipo de ingeniería que trabaja con specs, no con vibras. Subagentes especializados levantan requirements formales (EARS), diseñan, descomponen en tareas y construyen por lotes — con un gate humano entre cada fase, trazabilidad de cada línea de código hasta su requirement, y sellos de aprobación (quién, cuándo, qué commit) en cada artefacto. Cubre cuatro situaciones: proyecto nuevo, reingeniería de un legacy, feature sobre un sistema en producción sin romperlo, y prototipos para validar con el cliente.

Clonas, corres `/stark-init`, y el framework te lleva fase por fase: [empieza aquí →](docs/documentacion/QUICKSTART.md)

---

## Propiedad: SDD, MARK, stark

Tres cosas distintas. No se confunden:

- **SDD** (Spec-Driven Development — Desarrollo Guiado por Especificaciones): la metodología de la industria. Tomada y adaptada.
- **MARK**: la metodología propia de la autora — su adaptación de SDD. El **método**.
- **stark**: este framework. La herramienta que implementa MARK. El **con qué**.

> **MARK es el método, stark es la herramienta. stark es un framework Spec-Driven.**

### ¿Qué es SDD?

**Spec-Driven Development** es una práctica (un género) donde escribes especificaciones formales primero y el agente IA genera código a partir de ellas. Las specs son el artefacto primario versionado; el código es consecuencia.

Resuelve el problema del vibe-coding: prototipos rápidos pero código frágil. SDD recupera disciplina de ingeniería sin perder velocidad.

Está en fase "Assess" del Tech Radar de Thoughtworks (2025-2026). Práctica emergente bien fundamentada que probablemente sea estándar en 2027. MARK es la adaptación de la autora dentro de ese género; stark la implementa.

> stark te da el **formato** (la gramática de requirements/design/tasks) y el **workflow**. Lo que hace que entregue código que funciona — no solo documentación preciosa — son los **gates humanos** y el rigor de tu revisión. Esos los pones tú.

### ¿Qué es RDD?

**Receipt-Driven Development** (desarrollo guiado por comprobantes): ninguna validación sin evidencia verificable. No basta con que el agente diga "ya quedó" — cada aprobación deja huella escrita en el repo.

En stark son **dos sellos**:

1. **Sello de documento** — al aprobar requirements, design o tasks en su gate, el header queda estampado: `> Aprobado por [nombre] — YYYY-MM-DD`.
2. **Sello de lote** — al cerrar cada lote de build con tests en verde: `> Lote validado: commit <hash> — Tests: PASS — aprobado por [nombre] el YYYY-MM-DD`. Antes del push se recompara el hash: si difiere, el código cambió después de la validación — se revalida, no se entrega.

Con eso, cualquiera que abra un proyecto hecho con stark puede verificar **quién aprobó qué, cuándo, y que lo validado es exactamente lo entregado** — sin acceso al chat donde ocurrió.

Honestidad de posicionamiento: RDD es una disciplina emergente de la era de agentes de IA, sin autor canónico ni estándar consagrado (a diferencia de SDD). stark no la presume: la implementa.

---

## Quick Start

stark cubre tres casos de uso de construcción/cambio, más el prototipo como modo transversal:

| Tu situación | Caso de uso | Cómo "instalar" stark |
|---|---|---|
| Construir desde cero (entrevistas, formularios, imágenes) | **Nuevo** (greenfield) | Clonar como repo nuevo |
| Reescribir/modernizar un legacy (código + arqueología previa) | **Reingeniería** (brownfield-rewrite) | Clonar como repo nuevo |
| Sistema en producción + agregar feature sin romper nada | **Mantenimiento** | Copiar `.claude/`, `templates/`, `docs/features/` y `docs/documentacion/` **al repo existente** |
| Mockup interactivo desplegable a partir de requirements | **Prototipo** (transversal/standalone) | Sobre cualquiera de los anteriores |

### La regla de oro: la herramienta no se commitea, las specs sí

stark tiene dos partes que no se confunden:

| | Qué es | ¿Va al git de tu proyecto? |
|---|---|---|
| **Herramienta** | `.claude/` (agentes, skills, comandos) y `templates/` | ❌ NO — va en `.gitignore`; vive en tu disco |
| **Producto** | Tu código + `docs/` (specs, sustrato, manual) + `CONSTITUTION.md` | ✅ SÍ — es tu proyecto y su evidencia SDD |

- Gitignorear **no borra nada**: los archivos siguen en tu disco y los agentes funcionan igual. Git simplemente no los sube.
- **Actualizar stark** en cualquier proyecto = recopiar `.claude/` y `templates/` encima. Como están ignoradas, git ni se entera.
- **Entregar o vender el proyecto** = el repo ya está limpio: se va con sus specs, sin tu herramienta.
- **¿Proyecto viejo con stark commiteado adentro?** Desde su raíz: `printf '.claude/\ntemplates/\n' >> .gitignore && git rm -r --cached .claude templates && git commit -am "stark: herramienta fuera del repo"` — salen del repo, siguen en tu disco.

### Instalar (nuevo / reingeniería)

```bash
git clone https://github.com/GabrielaStark/stark.git mi-proyecto
cd mi-proyecto && rm -rf .git && git init
printf '.claude/\ntemplates/\nscripts/verificar.py\n.github/workflows/verificar.yml\n' >> .gitignore
```

El README y el LICENSE de stark los reemplazas por los de tu proyecto cuando arranque el código.

Carga inputs:
- **Nuevo**: material de levantamiento en `docs/inputs/` (transcripciones, imágenes, formularios).
- **Reingeniería**: análisis arqueológico previo en `docs/analysis/` + código legacy accesible.

### Instalar (mantenimiento, sobre repo existente)

Desde la raíz de tu repo en producción, copia-pega:

```bash
git clone --depth 1 https://github.com/GabrielaStark/stark.git /tmp/stark && \
cp -r /tmp/stark/.claude /tmp/stark/templates . && \
mkdir -p docs/documentacion docs/features && \
cp /tmp/stark/docs/documentacion/*.md docs/documentacion/ && \
cp /tmp/stark/docs/features/README.md docs/features/ && \
printf '.claude/\ntemplates/\n' >> .gitignore && \
rm -rf /tmp/stark
```

Agrega la herramienta (`.claude/`, `templates/` — gitignoreadas: no ensucian el git del cliente) y la documentación (`docs/documentacion/`, `docs/features/` — estas sí se commitean: son parte del proyecto). No toca nada más.

**Antes del primer feature** (una vez por repo): genera el sustrato corriendo las skills `onboarding` y `reglas-negocio` desde Claude Code. Producen `docs/CLAUDE.md`, `docs/BIG_PICTURE.md` y `docs/REGLAS_DE_NEGOCIO.md`.

**Por cada feature nuevo**:

```bash
mkdir -p docs/features/<slug-del-feature>
cp templates/intent.md docs/features/<slug-del-feature>/intent.md
# edita docs/features/<slug-del-feature>/intent.md
```

### Ejecutar las fases

Vía principal: los comandos slash `/stark-*`. Las fases están numeradas; el prototipo (Fase 3) es ciudadano de primera.

```
1  /stark-init           ← arranca: detecta caso de uso (nuevo / reingeniería / mantenimiento)
2  /stark-requirements   ← material/legacy/intent → requirements.md (EARS)
3  /stark-prototype      ← (transversal) requirements → mockup desplegable + loop con cliente
4  /stark-design         ← requirements → design.md
5  /stark-tasks          ← design → tasks.md
6  /stark-build          ← ejecuta un lote (Slice) por sesión

   /stark-review   ← transversal: revisa el diff actual contra los Principios (sobre-ingeniería + seguridad)
   /stark-audit    ← transversal: audita el repo completo contra los Principios
```

Cada fase termina en un **gate humano**: revisión y aprobación explícita antes de pasar a la siguiente.

#### Alternativa manual: invocar subagentes directamente

Los comandos `/stark-*` orquestan subagentes (con `/agents` deberías ver 8). Si prefieres control fino, cada fase se puede invocar subagente por subagente — las invocaciones exactas están en [`REFERENCIA.md`](docs/documentacion/REFERENCIA.md), en la sección de cada fase.

### Documentación completa

- 📖 [`docs/documentacion/PRINCIPIOS.md`](docs/documentacion/PRINCIPIOS.md) — filosofía: el sello especifica todo, construye lo mínimo
- 🚀 [`docs/documentacion/QUICKSTART.md`](docs/documentacion/QUICKSTART.md) — **empieza aquí**: el camino feliz, una pista lineal por caso de uso
- 📋 [`docs/documentacion/REFERENCIA.md`](docs/documentacion/REFERENCIA.md) — referencia detallada por fase (anatomía completa de cada artefacto y agente)
- 🛟 [`docs/documentacion/TROUBLESHOOTING.md`](docs/documentacion/TROUBLESHOOTING.md) — problemas comunes y soluciones
- 🧭 [`docs/documentacion/DECISIONES.md`](docs/documentacion/DECISIONES.md) — decisiones de diseño del framework: modo prototipo y caso de uso mantenimiento

---

## Arquitectura del framework

```
stark/
├── .claude/
│   ├── commands/                                     ← 8 comandos slash /stark-*
│   │   ├── stark-init.md                             ← Fase 1: detecta caso de uso
│   │   ├── stark-requirements.md                     ← Fase 2
│   │   ├── stark-prototype.md                        ← Fase 3 (transversal)
│   │   ├── stark-design.md                           ← Fase 4
│   │   ├── stark-tasks.md                            ← Fase 5
│   │   ├── stark-build.md                            ← Fase 6
│   │   ├── stark-review.md                           ← transversal
│   │   └── stark-audit.md                            ← transversal
│   ├── agents/                                       ← 8 subagentes especializados
│   │   ├── analista-entrevistas.md                  ← nuevo: material → requirements
│   │   ├── arqueologo-codigo.md                      ← reingeniería: legacy → requirements
│   │   ├── prototipador-visual.md                    ← (transversal) requirements → mockup desplegado
│   │   ├── disenador-arquitecto.md                   ← construcción: requirements → design
│   │   ├── descompositor-tareas.md                   ← construcción: design → tasks
│   │   ├── analista-feature-mantenimiento.md         ← mantenimiento: intent + código prod → requirements (delta)
│   │   ├── disenador-delta-mantenimiento.md          ← mantenimiento: requirements (delta) → design (delta)
│   │   └── descompositor-riesgo-mantenimiento.md     ← mantenimiento: design (delta) → tasks (por riesgo)
│   └── skills/                                       ← 9 skills (7 constituciones SDD + 2 auxiliares)
│       ├── sdd-requirements/SKILL.md                 ← construcción
│       ├── sdd-prototype/SKILL.md                    ← transversal
│       ├── sdd-design/SKILL.md                       ← construcción
│       ├── sdd-tasks/SKILL.md                        ← construcción
│       ├── sdd-requirements-mantenimiento/SKILL.md   ← mantenimiento
│       ├── sdd-design-delta/SKILL.md                 ← mantenimiento
│       ├── sdd-tasks-risk/SKILL.md                   ← mantenimiento
│       ├── onboarding/SKILL.md                       ← auxiliar: genera CLAUDE.md + BIG_PICTURE.md
│       └── reglas-negocio/SKILL.md                   ← auxiliar: genera REGLAS_DE_NEGOCIO.md
├── docs/
│   ├── inputs/                                       ← material crudo (nuevo)
│   ├── analysis/                                     ← análisis previo (reingeniería)
│   ├── features/                                     ← caso de uso mantenimiento
│   │   └── <slug>/{intent,requirements,design,tasks}.md
│   ├── requirements.md                               ← OUTPUT construcción
│   ├── prototype/                                    ← OUTPUT prototipo
│   ├── design.md                                     ← OUTPUT construcción
│   ├── tasks.md                                      ← OUTPUT construcción
│   └── documentacion/
│       ├── PRINCIPIOS.md                             ← filosofía (sello stark)
│       ├── QUICKSTART.md                             ← empieza aquí (camino feliz)
│       ├── REFERENCIA.md                             ← referencia detallada por fase
│       ├── TROUBLESHOOTING.md                        ← problemas comunes
│       └── DECISIONES.md                             ← decisiones de diseño (prototipo + mantenimiento)
├── scripts/
│   └── verificar.py                                  ← auto-verificación del framework (CI la
│                                                       corre en cada push)
└── templates/
    ├── intent.md                                     ← se copia y llena (input de mantenimiento)
    ├── CONSTITUTION.md                               ← se copia a la raíz y llena (decisiones
    │                                                   inmutables del proyecto)
    └── (resto)                                       ← esqueletos de referencia de los artefactos;
                                                        la fuente única de estructura son los skills
```

Este árbol es el repo de **stark**. En **tu proyecto**, solo se commitea `docs/` (y tu código): `.claude/`, `templates/`, `scripts/` y el workflow de CI son herramienta — gitignoreados, viven solo en tu disco (ver la regla de oro del Quick Start).

---

## Los casos de uso en una imagen

```
NUEVO                     REINGENIERÍA                MANTENIMIENTO
(desde cero)              (reescribir legacy)         (feature a sistema en prod)
    │                          │                              │
    ▼                          ▼                              ▼
docs/inputs/              docs/analysis/                docs/features/<X>/
    │                          │                              │
    ▼                          ▼                              ▼
analista-                 arqueologo-                  analista-feature-
entrevistas               codigo                       mantenimiento
    │                          │                              │
    └──────────┬───────────────┘                              │
               ▼                                              ▼
   docs/requirements.md                            docs/features/<X>/requirements.md
   (sistema completo)                              (DELTA + Surface of Contact
               │                                    + Invariantes Preservadas)
       [gate humano]                                          │
               │                                       [gate humano]
               ▼                                              │
   (prototipo transversal a los tres casos) ──────────────────┤
               │                                              │
       [gate cliente]                                         │
               ▼                                              ▼
   disenador-arquitecto                            disenador-delta-mantenimiento
               │                                              │
               ▼                                              ▼
   docs/design.md                                  docs/features/<X>/design.md
   (arquitectura completa)                         (delta sobre arq. heredada)
       [gate humano]                                  [gate humano]
               ▼                                              ▼
   descompositor-tareas                            descompositor-riesgo-
                                                    mantenimiento
               │                                              │
               ▼                                              ▼
   docs/tasks.md                                   docs/features/<X>/tasks.md
   (walking skeleton +                             (orden por RIESGO de regresión)
    rebanadas verticales)
       [gate humano]                                  [gate humano]
               │                                              │
               └────────────────────┬─────────────────────────┘
                                    ▼
                        lote por sesión + revisión humana → código + tests
```

**Los gates humanos no son opcionales.** Saltarse uno propaga errores 10x a la siguiente fase.

**Construcción (nuevo / reingeniería)**: las tasks se ordenan como **walking skeleton + rebanadas verticales** — primero un esqueleto end-to-end que camina, luego rebanadas verticales que atraviesan todas las capas, no capa por capa.

**Mantenimiento**: la arquitectura/stack son **heredados e inmutables**, los artefactos describen solo el **delta**, las tasks van ordenadas por **riesgo de regresión** (Regression Shield primero, No-Regression Validation al final), y se documentan explícitamente las **Invariantes Preservadas** del sistema existente. Los cambios internos de bajo riesgo pueden ir por **ruta corta** (un solo documento, un solo gate; Shield y No-Regression intactos) — el criterio es la superficie tocada, no el tamaño: ver `DECISIONES.md` B-D13.

---

## Reglas no negociables

1. **La unidad de ejecución es el lote** (un Slice vertical, o un grupo contiguo de la misma capa/sección), con revisión humana al cerrar cada lote. Nunca "ejecuta todo tasks.md". Las tareas de validación — y en mantenimiento el Regression Shield y la No-Regression Validation — van solas.
2. **Cada fase requiere aprobación humana explícita** antes de pasar a la siguiente (en la ruta corta de mantenimiento los gates se fusionan en uno; la aprobación humana se conserva — ver `DECISIONES.md` B-D13).
3. **Los SKILLs son absolutos.** Si una regla no encaja en un caso, el caso no es para stark — no inventes excepciones.
4. **Trazabilidad bidireccional.** Cada línea de código se justifica en una tarea → decisión de design → criterio EARS → historia de usuario.
5. **Nada gana su lugar por defecto.** Lo especulativo no se construye; lo que no aporta se recorta (escalera YAGNI, ver Principios).
6. **(Mantenimiento)** El Regression Shield va primero, la No-Regression Validation va última. Ambas son obligatorias. El Shield blinda solo invariantes `confirmada` e `inferida`; lo `en-duda` exige decisión explícita, nunca blindaje silencioso.

### Líneas que stark no cruza

- **No spec-as-source puro.** stark versiona las specs como artefacto primario, pero el código sigue siendo código mantenible — no la spec como única fuente de verdad sin código. Eso último es experimental, no producción.
- **No "es lo que hacen los grandes".** SDD está en "Assess", no en "Adopt". Es práctica emergente bien fundamentada, no estándar consolidado.

---

## Preguntas que casi siempre salen

**¿Y si el feature es enorme?** Lo partes. Una feature = un trío `requirements/design/tasks`. Si el `design.md` pasa de ~800 líneas o el `tasks.md` de ~50 tareas, partir. El anti-patrón confirmado por Thoughtworks es la spec gigante upfront + big-bang release. Partir divide el papeleo, no el riesgo: los pedazos de una misma feature se evalúan juntos para decidir ruta corta o completa. Partir para calificar a la ruta corta es el anti-patrón, no el atajo.

**¿Por qué EARS en inglés si trabajamos en español?** Porque los LLMs procesan EARS mucho mejor en inglés — así fueron entrenados. La User Story va en español (preserva el contexto humano de negocio); los criterios EARS van en inglés (preservan precisión técnica). Es el patrón más común en repos reales.

**¿Mantenimiento o reingeniería en un sistema podrido?** La pregunta única es: ¿respetas la arquitectura existente o la cambias? Caso límite: cliente quiere un feature pero la deuda técnica es enorme. Si el feature es chico y la deuda no bloquea → **mantenimiento** + tareas opcionales de refactor preventivo. Si la deuda hace imposible meter el feature sin romper → **reingeniería** del módulo afectado primero, después el feature.

(Más preguntas resueltas en [`TROUBLESHOOTING.md`](docs/documentacion/TROUBLESHOOTING.md) y [`DECISIONES.md`](docs/documentacion/DECISIONES.md).)

---

## Stack y requisitos

- **Claude Code** instalado
- Acceso a modelo Claude Opus (recomendado para los 8 subagentes)
- Material según el caso de uso:
  - Nuevo: entrevistas, transcripciones, formularios
  - Reingeniería: código legacy + arqueología previa
  - Mantenimiento: código en producción + descripción del feature
- (Mantenimiento recomendado) Skills auxiliares `onboarding` y `reglas-negocio` (ya incluidas en `.claude/skills/`) para generar el sustrato (`CLAUDE.md`, `BIG_PICTURE.md`, `REGLAS_DE_NEGOCIO.md`)

El repo se auto-verifica: `python3 scripts/verificar.py` valida frontmatters, fences, links y nombres citados; el CI lo corre en cada push.

---

## Licencia y autoría

stark — framework creado por [iamgabstark_](https://github.com/GabrielaStark). Licencia **MIT**.

Implementa la metodología **MARK**, adaptación propia de la autora de prácticas SDD documentadas por **GitHub Spec Kit**, **AWS Kiro** y **JetBrains Junie**, llevadas al flujo de trabajo de Claude Code con subagentes y skills.

La escalera YAGNI (Principio 1) está adaptada de **Ponytail** (Dietrich Gebert, MIT).
