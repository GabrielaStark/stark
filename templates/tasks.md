<!--
TEMPLATE: tasks.md
Framework: stark (Spec-Driven Development)

Reglas absolutas:
- Cada tarea: checkbox + número + verbo concreto + sub-pasos + criterio de hecho + footer
- Una tarea = una sesión de agente (1-3 archivos, 50-200 líneas)
- Tests SIEMPRE como tareas independientes, NUNCA como sub-pasos
- Footer obligatorio: _Requirements: X.Y, ..._  (puede ser `-` para setup)
- Cada criterio EARS del requirements.md debe estar referenciado en al menos una tarea

Estrategia de entrega (delivery_strategy):
- DEFAULT = vertical (walking skeleton + rebanadas verticales). Ver cuerpo de abajo.
- Excepción = layered (orden clásico por capa). Solo si el design.md lo justifica
  explícitamente (infraestructura pura, migración o refactor sin UI). Ver el bloque
  comentado "ALTERNATIVA LAYERED" al final de este archivo.

Regla de slices (vertical):
- Cada slice CRUZA todas las capas de UNA feature: datos -> lógica -> API -> UI + tests,
  respetando ese orden de dependencia DENTRO del slice.
- Cada slice CIERRA con un criterio demostrable de punta a punta:
  "el sistema corre y la feature <X> es demostrable de punta a punta".
- La trazabilidad EARS NO cambia con el reordenamiento: solo cambia el AGRUPAMIENTO
  (de capas a slices), nunca la cobertura. Cada criterio EARS sigue cubierto por al
  menos una tarea, esté donde esté el slice.
- Los slices se ordenan por valor/riesgo de negocio (el más valioso/riesgoso primero).

Antes de cerrar este archivo, ejecutar el checklist de auto-validación
definido en .claude/skills/sdd-tasks/SKILL.md

Anatomía de tarea:
- [ ] N. [Verbo] [objeto concreto]
  - [Sub-paso 1: archivos a tocar / patrón a aplicar]
  - [Sub-paso 2]
  - Criterio de hecho: [cómo se sabe que terminó]
  - _Requirements: X.Y, X.Z_

Verbos permitidos: Implementar, Crear, Modificar, Agregar, Refactorizar,
                   Configurar, Validar, Documentar
-->

# Tasks: [Nombre del feature o sistema]

<!--
delivery_strategy: vertical
Estructura: ## 0. Walking Skeleton  ->  ## Slice 1: <feature>  ->  ## Slice 2: <feature> ...
-->

## 0. Walking Skeleton

<!--
Fundación mínima DESPLEGABLE: el sistema arranca, se despliega y atraviesa TODAS las
capas con un hilo pasante trivial (un end-to-end mínimo real). Incluye solo lo
imprescindible para que exista algo desplegable. NO mete features completas: es el
esqueleto que camina.
-->

- [ ] 1. Configurar scaffolding y estructura del proyecto
  - Crear estructura de carpetas: `src/{ui,api,services,repositories,db}`
  - Inicializar dependencias del package manager
  - Configurar linter, formatter, y tsconfig (si aplica)
  - Criterio de hecho: `npm install` corre limpio, linter pasa en proyecto vacío
  - _Requirements: -_

- [ ] 2. Configurar entorno de testing
  - Instalar framework de tests (vitest/jest/playwright según design §8)
  - Configurar coverage y CI mínimo
  - Criterio de hecho: `npm test` corre con un test trivial pasando
  - _Requirements: -_

- [ ] 3. Implementar hilo pasante trivial end-to-end
  - Crear un endpoint/handler de salud (`GET /health`) que devuelva 200
  - Crear una pantalla/cliente mínimo que consuma ese endpoint y muestre el estado
  - Atravesar todas las capas con un dato trivial (sin lógica de negocio real)
  - Criterio de hecho: la UI muestra el resultado del endpoint vivo; el hilo cruza UI->API->servicio
  - _Requirements: -_

- [ ] 4. Configurar pipeline de despliegue mínimo
  - Definir build y artefacto desplegable (Docker / plataforma según design §8)
  - Desplegar el hilo pasante a un entorno accesible
  - Criterio de hecho: el sistema arranca y responde `/health` en el entorno desplegado
  - _Requirements: -_

- [ ] 5. Tests del hilo pasante (smoke E2E)
  - Caso éxito: la petición a `/health` retorna 200 a través de todas las capas
  - Criterio de hecho: smoke test pasa en CI contra el esqueleto desplegado
  - _Requirements: -_

## Slice 1: [Nombre de la feature de mayor valor/riesgo]

<!--
Slice vertical: cruza datos -> lógica -> API -> UI + tests, en ese orden de dependencia.
Cierra con criterio demostrable de punta a punta. La cobertura EARS no cambia: cada
criterio que toque esta feature se referencia aquí.
-->

- [ ] 6. Crear schema y migración de tabla [nombre]
  - Definir entidad según design §3
  - Generar migración con índices declarados y aplicarla localmente
  - Criterio de hecho: tabla existe, índices verificables con `\d` o equivalente
  - _Requirements: [X.Y]_

- [ ] 7. Implementar repositorio [NombreRepository]
  - Crear archivo `src/repositories/[nombre]Repository.ts`
  - Implementar métodos según contratos del design §4; aislar queries (ningún SQL fuera)
  - Criterio de hecho: métodos compilan, types pasan
  - _Requirements: [X.Y, X.Z]_

- [ ] 8. Tests de integración para [NombreRepository]
  - Caso éxito: insert + read recupera el dato correctamente
  - Caso error: constraint violation retorna error tipado
  - Caso borde: query sobre tabla vacía
  - Criterio de hecho: todos los tests del archivo pasan
  - _Requirements: [X.Y, X.Z]_

- [ ] 9. Implementar servicio [NombreService]
  - Crear archivo `src/services/[nombre]Service.ts`
  - Implementar casos de uso según design §2 y §4; validar reglas antes de delegar al repo
  - Criterio de hecho: lógica pura, no toca BD directo
  - _Requirements: [X.Y]_

- [ ] 10. Tests unitarios para [NombreService]
  - Mockear repositorios
  - Cubrir camino feliz y casos error EARS del requirements
  - Criterio de hecho: coverage > 80% del archivo
  - _Requirements: [X.Y]_

- [ ] 11. Implementar endpoint/handler [nombre]
  - Crear archivo `src/api/[nombre].ts`
  - Validar payload con schema, invocar servicio, mapear errores a códigos tipados del design §4
  - Criterio de hecho: endpoint compila, contratos coinciden con design §4
  - _Requirements: [X.Y]_

- [ ] 12. Tests de integración para endpoint [nombre]
  - Caso éxito: payload válido → respuesta esperada
  - Caso error: cada tipo de error EARS retorna código correcto
  - Caso borde: payload mal formado / faltante
  - Criterio de hecho: todos los tests pasan
  - _Requirements: [X.Y, X.Z]_

- [ ] 13. Implementar pantalla/componente [nombre]
  - Crear componente según wireframes o descripción del requirements
  - Validar input en cliente (espejo de validación servidor), invocar API, manejar estados loading/success/error tipados
  - Criterio de hecho: componente renderiza e integra con la API real del slice
  - _Requirements: [X.Y]_

- [ ] 14. Tests E2E del flujo "[feature del Slice 1]"
  - Cubrir el flujo completo según design §6 (UI -> API -> servicio -> datos)
  - Camino feliz: usuario completa la operación de inicio a fin
  - Camino error: al menos un caso de error del requirements
  - Criterio de hecho: el sistema corre y la feature [del Slice 1] es demostrable de punta a punta.
  - _Requirements: [X.Y, X.Z, X.W]_

## Slice 2: [Siguiente feature por valor/riesgo]

<!--
Mismo patrón vertical: datos -> lógica -> API -> UI + tests, cerrando demostrable de
punta a punta. Reutiliza scaffolding y esqueleto del Walking Skeleton; aquí solo se
agrega lo propio de la feature. Repetir un bloque "## Slice N" por cada feature.
-->

- [ ] 15. Crear schema y migración de [entidad del Slice 2]
  - Definir entidad según design §3 y aplicar migración
  - Criterio de hecho: tabla/columnas existen y verificables
  - _Requirements: [X.Y]_

- [ ] 16. Implementar repositorio/servicio de [feature del Slice 2]
  - Crear repositorio + servicio según design §4; reglas de negocio en el servicio
  - Criterio de hecho: capa datos+lógica compila y types pasan
  - _Requirements: [X.Y, X.Z]_

- [ ] 17. Tests unitarios/integración de datos+lógica del Slice 2
  - Cubrir camino feliz y casos error EARS de esta feature
  - Criterio de hecho: tests del slice pasan
  - _Requirements: [X.Y, X.Z]_

- [ ] 18. Implementar endpoint + UI de [feature del Slice 2]
  - Endpoint según design §4 (validación + mapeo de errores tipados)
  - Componente que consume el endpoint y maneja estados loading/success/error
  - Criterio de hecho: API y UI integradas con datos reales del slice
  - _Requirements: [X.Y]_

- [ ] 19. Tests E2E del flujo "[feature del Slice 2]"
  - Cubrir el flujo completo según design §6; camino feliz + un caso de error
  - Criterio de hecho: el sistema corre y la feature [del Slice 2] es demostrable de punta a punta.
  - _Requirements: [X.Y, X.Z, X.W]_

<!-- Repetir "## Slice N: <feature>" por cada feature restante, ordenadas por valor/riesgo. -->

## Documentation

- [ ] N. Documentar uso de las features entregadas
  - Actualizar README con sección por slice/feature
  - Documentar endpoints públicos (si aplica) y agregar ejemplos de uso
  - Criterio de hecho: lector externo entiende qué hace cada feature y cómo usarla
  - _Requirements: -_

<!--
Patrones opcionales (aplican dentro de cualquier slice o del walking skeleton):

Spike (cuando hay incertidumbre técnica):
- [ ] N. Spike: investigar [pregunta concreta]
  - Pregunta a responder: [una línea]
  - Output esperado: mini-ADR agregado a design.md
  - Timebox: [horas máximo]
  - _Requirements: -_

Refactor preventivo:
- [ ] N. Refactor preventivo: limpiar [módulo X] antes de tarea N+M
  - Extraer [Y] a su propio módulo
  - Sin cambio de comportamiento (tests existentes siguen pasando)
  - _Requirements: -_

Validación intermedia:
- [ ] N. Validar integración tareas 1-N
  - Correr suite completa de tests hasta este punto
  - Verificar criterios EARS [X.Y, ...] manualmente con caso de uso real
  - _Requirements: [X.Y, X.Z]_

Tarea opcional (para MVP):
- [ ] N. (opcional) [Verbo] [acción]
  - ...
  - _Requirements: [no funcional]_

Tareas paralelizables (mismo número base, sufijo letra):
- [ ] 7a. Implementar [cosa A]
- [ ] 7b. Implementar [cosa B]
-->

<!--
=========================================================================
ALTERNATIVA LAYERED (delivery_strategy: layered)
=========================================================================
Usar SOLO cuando el design.md justifica explícitamente que la entrega vertical no
aplica: infraestructura pura, migración o refactor sin UI. En esos casos NO hay
feature demostrable de punta a punta, así que el agrupamiento por slices no aporta.

Orden clásico por capa (reemplaza al cuerpo vertical de arriba):

## Setup            -> scaffolding, deps, linter, testing
## Data Model       -> schema y migraciones por entidad (design §3)
## Data Access      -> repositorios + tests de integración (design §4)
## Business Logic   -> servicios + tests unitarios (design §2, §4)
## API / Interface  -> endpoints/handlers + tests de integración (design §4)
## UI / Client      -> pantallas/componentes (si aplica)
## Integration Tests (E2E) -> flujos críticos completos (design §6)
## Documentation    -> README, endpoints, ejemplos de uso

Reglas invariantes que NO cambian respecto a vertical:
- Cada tarea conserva sus 5 elementos (checkbox + número + verbo + sub-pasos + criterio).
- Cada tarea conserva su footer _Requirements: X.Y_ (o `-`).
- Tests SIEMPRE como tareas independientes.
- La cobertura EARS es la misma: solo cambia el agrupamiento (capas vs. slices).
-->
