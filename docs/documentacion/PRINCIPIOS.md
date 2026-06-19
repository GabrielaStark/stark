# Principios de stark

stark es un framework de Gabriela Stark (@iamgabstark_). Implementa la
metodología MARK, una adaptación propia de Spec-Driven Development (Desarrollo
Guiado por Especificaciones).

Une dos mundos: especificación exhaustiva (specs primero, EARS, trazabilidad,
gates humanos) e implementación mínima (no escribir una línea que no gane su
lugar). El sello: especifica todo, construye lo mínimo.

Todo agente lee este archivo antes de actuar y respeta estos principios como
reglas duras.

## 1. No sobre-ingeniería (escalera YAGNI)

Antes de escribir código, recorre la escalera y detente en el primer escalón
que resuelva el requerimiento:
1. ¿Debe existir? — lo especulativo no se construye.
2. Eliminar — borra código muerto, flexibilidad no usada, abstracciones anticipadas.
3. Librería estándar — lo nativo del lenguaje antes que lógica propia.
4. Nativo de plataforma — lo integrado antes que dependencias externas.
5. Reducir — la misma lógica, con menos líneas.

Escalera adaptada de Ponytail (Dietrich Gebert, MIT). Crédito a la fuente.

## 2. Seguridad por diseño
Perezoso, no negligente. Nunca se sacrifican validación, manejo de errores,
protección de datos, secretos fuera del código, manejo de pérdida de datos.

## 3. Despliegue simple
Si desplegar exige un ritual, el diseño falló. Default al camino más simple que
funcione en producción. "¿Cómo se despliega esto?" es criterio de primera clase.

## 4. Documentación limpia
Cada documento gana su lugar. Sin redundancia, sin relleno, sin secciones "por
completitud".

## El principio que aplica a stark mismo
Un framework que predica contra la sobre-ingeniería no puede ser él mismo
sobre-ingeniado. Estos principios aplican al código que stark genera Y a stark
como producto.
