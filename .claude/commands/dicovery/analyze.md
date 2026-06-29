---
description: Analiza las entrevistas crudas de un discovery y extrae personas, stakeholders, dolores y requisitos, escribiendo el mapa de evidencia.
argument-hint: "<carpeta del discovery, p. ej. discoveries/citasalud>"
---

# Analizar evidencia de un discovery

Usa la skill `discovery` como estándar de formato.

**Discovery a analizar:** `$ARGUMENTS`
Si está vacío, pregunta al usuario qué discovery analizar (una carpeta dentro de
`discoveries/`) en lugar de asumir uno.

Las entrevistas están en `$ARGUMENTS/interviews/` y los artefactos se escriben en
`$ARGUMENTS/outputs/`. Nunca escribas fuera de la carpeta `outputs/` de ese discovery.

Pasos:

1. Lee **todas** las entrevistas de `$ARGUMENTS/interviews/`. Revisa el
   frontmatter de cada una (`rol_entrevistado`, `primera_persona`) y su contenido.

2. Extrae, citando siempre el archivo fuente:
    - **Personas** (tipos de usuario/actor). Marca el respaldo: `primera mano` si
      existe entrevista propia de ese rol; `referenciada` si solo la mencionan
      otros. Si una persona aparece mencionada pero no entrevistada, **inclúyela
      igual** y márcala `referenciada` — no la ocultes para "pasar" el gate.
    - **Stakeholders** (actores con interés, aunque no sean usuarios directos).
    - **Dolores** concretos, cada uno con un `id` corto en kebab-case.
    - **Requisitos candidatos** (funcionales y no funcionales), numerados R-NN.

3. Escribe en `$ARGUMENTS/outputs/` (en español, siguiendo la skill):
    - `personas.md` — personas y stakeholders.
    - `requisitos.md` — requisitos candidatos.
    - `evidence-map.json` — el mapa de evidencia con el esquema exacto de la skill
      (personas con `name`/`role`/`primary`, pains con `id`/`source`). Obligatorio:
      lo audita el gate de readiness.

4. Cierra con un resumen: cuántas personas, stakeholders, dolores y requisitos, y
   **advierte explícitamente** si alguna persona quedó solo `referenciada` (sin
   entrevista de primera mano), porque eso impedirá generar el MVP.

Regla de cero invención: si la evidencia no respalda algo, no lo escribas como hecho.