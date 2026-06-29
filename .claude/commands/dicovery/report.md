---
description: Genera un reporte HTML visual y a color de un discovery (personas, cadena de valor y tablero de experimentos) desde sus artefactos estructurados.
argument-hint: "<carpeta del discovery, p. ej. discoveries/citasalud>"
---

# Generar reporte visual de un discovery

**Discovery:** `$ARGUMENTS`
Si está vacío, pregunta cuál discovery antes de continuar.

Prerrequisito: deben existir al menos `$ARGUMENTS/outputs/evidence-map.json` (de
`/discovery:analyze`). Para el tablero de experimentos, también
`$ARGUMENTS/outputs/experiment-board.json` (de `/discovery:experiments`).

Pasos:

1. Ejecuta el generador determinista (no inventes el HTML tú mismo; el script lo
   produce de forma reproducible a partir de los JSON):

   ```bash
   python3 .claude/scripts/build-report.py $ARGUMENTS
   ```

2. Confirma al usuario la ruta del reporte (`$ARGUMENTS/outputs/report.html`) y
   resume qué contiene: personas con su respaldo (color verde/ámbar), el puente
   output→outcome→impact, y el tablero de experimentos con el riesgo codificado
   por color (alto=rojo, medio=ámbar, bajo=verde).

El reporte es autocontenido (un solo .html, sin dependencias externas): se abre
en cualquier navegador y sirve para presentar el discovery o imprimirlo.