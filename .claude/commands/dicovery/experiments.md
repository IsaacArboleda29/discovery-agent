---
description: Convierte los supuestos riesgosos del MVP de un discovery en hipótesis falsables y diseña el experimento más barato para cada una. Sujeto al gate de hipótesis.
argument-hint: "<carpeta del discovery, p. ej. discoveries/citasalud>"
---

# Generar hipótesis y experimentos de un discovery

Usa la skill `discovery` (sección "Hipótesis y experimentos").

**Discovery:** `$ARGUMENTS`
Si está vacío, pregunta cuál discovery antes de continuar.

Prerrequisito: deben existir `$ARGUMENTS/outputs/mvp-canvas.md` y
`$ARGUMENTS/outputs/evidence-map.json`. Si faltan, corre antes los comandos previos.

Idea rectora (diapositiva 15): el puente entre output e impact es una **hipótesis**,
y las hipótesis se comprueban. Idea rectora (diapositiva 32): cada experimento es
**comprar información barata** sobre el riesgo más grande antes de construir.

Pasos:

1. Lee `mvp-canvas.md` (sobre todo "Riesgos / supuestos" y la métrica de éxito),
   `requisitos.md` y `evidence-map.json` de `$ARGUMENTS/outputs/`.

2. Identifica los **supuestos más riesgosos** (saltos de fe de los que depende el
   MVP y que aún no están validados). Prioriza por riesgo (impacto de equivocarse
   × incertidumbre), del más peligroso al menos.

3. Para cada supuesto prioritario escribe una **hipótesis falsable** y su
   **experimento**, siguiendo la skill. Cada una debe tener: el supuesto, el
   enunciado "Creemos que… si… porque…", una **señal medible** (de negocio, no de
   vanidad), un **criterio de éxito concreto** (con número/porcentaje), el
   **experimento más barato** que responda (con caja de tiempo) y una **regla de
   decisión** que diga qué hacer si pasa **y si falla**.

4. Escribe en `$ARGUMENTS/outputs/` (siguiendo la skill):
    - `experiment-board.json` — el tablero machine-readable que audita el gate.
    - `hypotheses.md` — las test cards legibles, ordenadas de mayor a menor riesgo.
      Escribe primero el JSON y luego el .md.

5. Cierra con un resumen: cuántas hipótesis, cuál es la #1 por riesgo y qué
   experimento la ataca primero.

## El gate de hipótesis

Al escribir estos artefactos, el hook `hypothesis-gate.py` exige que cada
hipótesis sea comprobable (señal medible, umbral concreto, regla de decisión que
contemple el fallo, métrica no de vanidad). Si bloquea, **no lo esquives**:
reescribe la hipótesis en forma falsable. Una hipótesis que no se puede refutar no
es una hipótesis, es un deseo.