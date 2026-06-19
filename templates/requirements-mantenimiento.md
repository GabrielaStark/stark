# Requirements: [Nombre del feature]

> Feature de mantenimiento sobre el sistema `<nombre-sistema>`.
> Este documento describe **el delta** (lo que se añade), no el sistema completo.
> Generado por `analista-feature-mantenimiento` siguiendo el skill `sdd-requirements-mantenimiento`.

## Contexto

[Párrafo descriptivo, 7-10 líneas:
- Qué feature se va a agregar
- Por qué (problema que resuelve / decisión de negocio que lo motiva)
- Quién lo pidió
- En qué módulo/área del sistema vive
Cero implementación. Cero arquitectura nueva.]

## Surface of Contact

[Tabla obligatoria. TODOS los módulos, archivos, endpoints, tablas, servicios
que el feature toca, lee, o explícitamente NO toca.]

| Elemento del sistema | Tipo | Qué se hace | Riesgo |
|---|---|---|---|
| `src/...` | Servicio existente | Modificar | medio |
| `tabla_x` | Schema existente | Agregar columna | medio |
| `POST /api/...` | Endpoint nuevo | Crear | bajo |
| `src/...` | Módulo nuevo | Crear | bajo |
| `src/...` | Módulo existente | **NO se toca** | — |

Niveles:
- **alto**: punto de coexistencia con flujo crítico, alta probabilidad de regresión
- **medio**: modificación localizada con tests existentes
- **bajo**: lectura o creación aislada
- **—**: explícitamente NO se toca

## Invariantes Preservadas

[Lista numerada de comportamientos del sistema que NO deben cambiar.
Cada invariante con referencia al código que la implementa hoy.]

1. **I.1** — [Descripción de la invariante en lenguaje testeable].
   <!-- source: src/...:líneas; tests: ...Test.testNombre -->
2. **I.2** — ...
   <!-- source: ... -->

## Requirements (del delta)

### Requirement 1

**User Story:** Como [rol], quiero [acción/capacidad nueva], para [objetivo de negocio].

#### Acceptance Criteria

1. WHEN [trigger] THE SYSTEM SHALL [response]
2. IF [unwanted condition] THEN THE SYSTEM SHALL [response]
3. THE SYSTEM SHALL [invariant — performance, security, etc.]

### Requirement 2

**User Story:** Como [rol], quiero [...], para [...].

#### Acceptance Criteria

1. ...

## Non-Functional Requirements (del delta)

[Solo si el feature introduce restricciones nuevas. EARS estándar.]

## Tests Existentes a Preservar

[Lista de tests que ya cubren los módulos tocados. Si un módulo de riesgo
medio/alto NO tiene tests, documentar como gap.]

| Test existente | Cubre | ¿Existe? |
|---|---|---|
| `...Test.testNombre` | Invariante I.1 | Sí |
| (sin test) | Invariante I.2 | **NO — gap a cubrir** |

## Out of Scope (del feature)

[Lista explícita de lo que el feature NO va a hacer. Evita scope creep.]

## Open Questions

[Cosas no resueltas al cierre. Vacío idealmente.]

## Glossary

[Términos no obvios del dominio, si aplica.]
