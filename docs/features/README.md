# docs/features/

Carpeta destino del pipeline de **mantenimiento** de stark.

## Estructura

Una subcarpeta por feature, con slug en kebab-case:

```
docs/features/
├── README.md                      ← este archivo
├── exportar-reportes-pdf/         ← un feature
│   ├── intent.md                  ← input humano (descripción del feature)
│   ├── requirements.md            ← output: requirements del delta
│   ├── design.md                  ← output: design del delta
│   └── tasks.md                   ← output: tasks por riesgo
└── notificaciones-push/           ← otro feature
    └── ...
```

## Cómo empezar un feature de mantenimiento

1. Crea la carpeta `docs/features/<slug-del-feature>/`.
2. Copia el template: `cp templates/intent.md docs/features/<slug>/intent.md`.
3. Edita el `intent.md` describiendo el feature.
4. Invoca al primer agente del pipeline:
   ```
   Use the analista-feature-mantenimiento subagent to produce
   docs/features/<slug>/requirements.md
   ```
5. Pasa por los gates humanos (requirements → design → tasks) y ejecuta tarea por sesión.

## Sustrato recomendado (en `docs/` raíz, no aquí)

Antes de empezar el primer feature de mantenimiento sobre un sistema, conviene generar:

- `docs/CLAUDE.md` — guía del repo (skill `onboarding`)
- `docs/BIG_PICTURE.md` — radiografía arquitectónica (skill `onboarding`)
- `docs/REGLAS_DE_NEGOCIO.md` — reglas de negocio (skill `reglas-negocio`)

Estos archivos viven en `docs/` raíz (no dentro de `features/`) porque aplican al sistema completo, no a un feature específico. Los agentes del pipeline de mantenimiento los leen como sustrato si existen.

## Lectura recomendada

- [`docs/documentacion/DECISIONES.md`](../documentacion/DECISIONES.md) (Parte B) — decisiones de diseño del caso de uso mantenimiento.
- [`docs/documentacion/REFERENCIA.md`](../documentacion/REFERENCIA.md) — detalle por fase (variante mantenimiento).
