# Tasks: [Nombre del feature]

> Feature de mantenimiento sobre `<nombre-sistema>`.
> Orden por **riesgo de regresión**, no por capa arquitectónica.
> Generado por `descompositor-riesgo-mantenimiento` siguiendo el skill `sdd-tasks-risk`.

## Regression Shield

> Tareas de blindaje. Tests sobre código existente que se va a tocar.
> Estas tareas se ejecutan ANTES de cualquier modificación al código de producción.

- [ ] 1. Verificar que la suite existente pasa contra los módulos afectados
  - Ejecutar `[comando de tests del repo, ej. mvn test, npm test, etc.]`
  - Si falla, detener y reportar al humano. El sistema está en estado roto independiente del feature.
  - Criterio de hecho: todos los tests existentes pasan en verde sin tocar nada
  - _Requirements: -_ | _Invariants: -_

- [ ] 2. Blindar I.1 — [descripción invariante]
  - Crear test en `[archivo_test]`
  - Cubrir comportamiento descrito en I.1 usando la fuente referenciada
  - Usar el comportamiento ACTUAL como ground truth (no inventar)
  - Criterio de hecho: test pasa contra el código sin modificaciones
  - _Requirements: -_ | _Invariants: I.1_

- [ ] 3. Blindar I.2 — [descripción invariante]
  - ...
  - _Requirements: -_ | _Invariants: I.2_

## Spike (opcional)

[Solo si el design.md indica incertidumbre técnica.]

## Data Model Delta

- [ ] N. Crear migración `[nombre]`
  - Archivo: `[ruta]`
  - ALTER TABLE ... compatible hacia atrás (DEFAULT explícito si NOT NULL)
  - Criterio de hecho: migración aplica limpiamente en BD de prueba + rollback funciona
  - _Requirements: X.Y_ | _Invariants: I.Z (compatibilidad hacia atrás)_

## Backend Delta

- [ ] N. Implementar `[servicio nuevo]`
  - Archivos: ...
  - Patrón: [patrón existente del sistema, citado del design]
  - Criterio de hecho: unit tests pasan
  - _Requirements: X.Y_ | _Invariants: -_

- [ ] N+1. Tests unit del `[servicio nuevo]`
  - Casos: feliz, error tipado, edge case
  - _Requirements: X.Y_ | _Invariants: -_

## API Delta

- [ ] N. Implementar endpoint `[nuevo]`
  - ...
  - _Requirements: X.Y_ | _Invariants: -_

- [ ] N+1. Modificar endpoint `[existente]` para extender con [delta]
  - **Preservar**: comportamiento sin el query param/header nuevo (invariante I.A)
  - Agregar rama para caso nuevo
  - Criterio de hecho: tests existentes pasan Y caso nuevo cubierto
  - _Requirements: X.Y_ | _Invariants: I.A_

- [ ] N+2. Tests de integración del endpoint extendido
  - Caso sin query param: response idéntica a hoy
  - Caso con query param: response extendida correcta
  - _Requirements: X.Y_ | _Invariants: I.A_

## Frontend Delta

[Si aplica.]

- [ ] N. Implementar `[componente UI]`
- [ ] N+1. Tests del componente
- [ ] N+2. Integrar `[componente]` en `[vista existente]` sin alterar resto
  - _Invariants: I.B (resto de la vista renderiza igual)_

## Integration

> Puntos de coexistencia con flujos existentes. Cada uno es una tarea aislada.

- [ ] N. Integrar [delta] con [flujo existente 1]
  - Punto de inserción: [archivo:línea o describir]
  - Garantía: el flujo existente sin la rama nueva se ejecuta idéntico
  - Criterio de hecho: tests del flujo existente pasan + caso nuevo cubierto
  - _Requirements: X.Y_ | _Invariants: I.C_

- [ ] N+1. Integrar [delta] con [flujo existente 2]
  - ...
  - _Invariants: I.D_

## Integration Tests (E2E del feature)

- [ ] N. Tests E2E del flujo completo "[nombre]"
  - Caso éxito: payload válido → 201
  - Caso error: payload inválido → 400 con error tipado
  - Caso coexistencia: flujo existente sin tocar el feature sigue funcionando
  - _Requirements: X.Y, X.Z, ..._ | _Invariants: I.A, I.C_

## No-Regression Validation

> Tarea final obligatoria antes de cerrar el feature.

- [ ] N. Verificar regresión: suite completa + invariantes
  - Ejecutar TODA la suite de tests del repo
  - Verificar manualmente cada invariante de `requirements.md`
  - Para cada invariante: ¿el test sigue pasando? ¿el comportamiento es idéntico?
  - Si alguna invariante está violada, **detener cierre** y reportar
  - Criterio de hecho: 100% de tests pasan + cada invariante verificada
  - _Requirements: -_ | _Invariants: I.1, I.2, ..., I.N (todas)_

## Documentation

- [ ] N. Actualizar `docs/BIG_PICTURE.md` si el delta cambió arquitectura visible
  - Si no aplica, marcar tarea como N/A y omitir
  - _Requirements: -_ | _Invariants: -_

- [ ] N+1. Actualizar `docs/REGLAS_DE_NEGOCIO.md` si el delta introdujo regla nueva
  - Agregar la regla con referencia al código nuevo
  - _Requirements: X.Y_ | _Invariants: -_

- [ ] N+2. Actualizar README del módulo afectado
  - _Requirements: -_ | _Invariants: -_
