# Discovery Agent

Agente de Claude Code que convierte **conocimiento de negocio crudo** en
**artefactos de producto** (personas, stakeholders, requisitos, user stories,
MVP Canvas) e **hipótesis con experimentos** para validarlos. Es el producto de
la Unidad 1 de *Ingeniería de Software* (Maestría en Software, UPS).

El agente es **genérico**: no está atado a ningún caso. Cada caso de negocio es
un **discovery** independiente bajo `discoveries/`. El objetivo no es escribir
código de la aplicación, sino entender el problema antes de construir.

## Estructura

- `discoveries/<nombre>/` — un caso de descubrimiento. Contiene:
    - `interviews/` — evidencia cruda: entrevistas y notas en Markdown, en español,
      cada una con frontmatter (`rol_entrevistado`, `primera_persona`, `anonimizada`).
      Es la **única fuente de verdad** sobre el negocio de ese discovery.
    - `outputs/` — TODO artefacto generado de ese discovery, en español.
- `discoveries/citasalud/` — discovery de **ejemplo**, completo (sirve de
  referencia y de plan B para la demo). No lo uses como fuente de otro discovery.
- `discoveries/_template/` — discovery en blanco para copiar al empezar uno nuevo.
- `.claude/` — el agente en sí (genérico): skill `discovery`, comandos y los hooks.

## Reglas de trabajo (no negociables)

1. **Cero invención.** Nunca afirmes un dolor, persona o requisito que no esté
   respaldado por una entrevista real del discovery. Si la evidencia no alcanza,
   **dilo** en lugar de rellenar con suposiciones.
2. **Trazabilidad.** Cada persona, dolor y requisito cita el archivo de entrevista
   del que proviene (por nombre, p. ej. `recepcionista.md`).
3. **Personas de primera mano.** Una persona solo está respaldada si existe una
   entrevista *en primera persona* de ese rol. Que la mencionen otros no basta.
4. **Aislamiento entre discoveries.** Trabaja solo dentro del discovery indicado;
   nunca mezcles evidencia o artefactos de un discovery con otro.
5. **Idioma.** Español, salvo términos técnicos (user story, MVP, stakeholder).
6. **Formato.** Sigue siempre la skill `discovery`. No improvises estructuras.

## Flujo de trabajo (recibe la carpeta del discovery como argumento)

1. `/discovery:analyze <discovery>` — lee la evidencia y produce `personas.md`,
   `requisitos.md` y `evidence-map.json` en `<discovery>/outputs/`.
2. `/discovery:generate-mvp <discovery>` — genera `user-stories.md` y
   `mvp-canvas.md`.
3. `/discovery:experiments <discovery>` — convierte los supuestos riesgosos del
   MVP en hipótesis falsables y genera `experiment-board.json` y `hypotheses.md`.

Ejemplo: `/discovery:analyze discoveries/citasalud`.

## Los gates (reglas duras, por discovery)

Ambos hooks se auto-ubican: deducen a qué discovery pertenece la escritura desde
la ruta del archivo, así que funcionan para cualquier discovery.

### Gate de readiness
Antes de escribir `mvp-canvas.md` o `user-stories.md` de un discovery, valida que
su evidencia sea suficiente: existe el mapa de evidencia, hay un mínimo de
entrevistas, cada persona primaria tiene respaldo de primera mano y no hay dolores
huérfanos. Si no, **bloquea** la escritura y explica qué falta. No lo sortees: la
respuesta correcta es conseguir más evidencia.

### Gate de hipótesis
Antes de escribir `hypotheses.md` o `experiment-board.json`, valida que cada
hipótesis sea **comprobable**: señal medible, criterio de éxito concreto (con
número), regla de decisión que contemple el fallo, y métrica que no sea de vanidad
(prueba ácida). Una hipótesis que no se puede refutar no es una hipótesis. Si
bloquea, reescríbela en forma falsable; no la disfraces para pasar.