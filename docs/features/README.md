# docs/features/

Carpeta destino del pipeline de **mantenimiento** de stark: una subcarpeta por
feature (slug en kebab-case, ej. `exportar-reportes-pdf`) con
`intent.md` (input humano) → `requirements.md` → `design.md` → `tasks.md`
(+ `prototype/` opcional si el feature trae UI).

Para empezar un feature: `/stark-init` (caso mantenimiento) crea
`docs/features/<slug>/intent.md` desde `templates/intent.md`; lo llenas en
lenguaje de negocio y sigues con `/stark-requirements <slug>`.

- Camino feliz completo: [`QUICKSTART.md`](../documentacion/QUICKSTART.md)
- Porqués del caso de uso: [`DECISIONES.md`](../documentacion/DECISIONES.md) (Parte B)
