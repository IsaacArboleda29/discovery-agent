---
description: Genera user stories y MVP Canvas de un discovery a partir de sus artefactos de descubrimiento. Sujeto al gate de readiness.
argument-hint: "<carpeta del discovery, p. ej. discoveries/citasalud>"
---

# Generar MVP de un discovery

Usa la skill `discovery` como estándar de formato.

**Discovery:** `$ARGUMENTS`
Si está vacío, pregunta cuál discovery antes de continuar.

Prerrequisito: deben existir `$ARGUMENTS/outputs/personas.md`,
`$ARGUMENTS/outputs/requisitos.md` y `$ARGUMENTS/outputs/evidence-map.json`. Si
falta alguno, corre antes `/discovery:analyze $ARGUMENTS`.

Pasos:

1. Lee `personas.md`, `requisitos.md` y `evidence-map.json` de
   `$ARGUMENTS/outputs/`.

2. Genera en `$ARGUMENTS/outputs/`, siguiendo la skill:
    - `user-stories.md` — historias INVEST con criterios de aceptación y fuente.
    - `mvp-canvas.md` — el MVP Canvas completo, con una métrica de éxito honesta
      (que pase la prueba ácida) y un bloque explícito de "fuera de alcance por ahora".

3. Prioriza: el MVP debe atacar el **núcleo de valor** primero (lo que más duele y
   más se repite entre personas), no la lista completa de deseos.

## El gate de readiness

Al escribir `user-stories.md` o `mvp-canvas.md`, el hook `readiness-gate.py`
valida la evidencia de ESTE discovery. Si bloquea, **no lo esquives** (no escribas
el artefacto con otro nombre ni en otra carpeta). Lee el motivo, explícaselo al
usuario en español y di qué evidencia falta levantar (típicamente una entrevista
de primera mano que falta, o muy pocas entrevistas).