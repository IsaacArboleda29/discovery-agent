#!/usr/bin/env python3
"""
readiness-gate.py — Hook PreToolUse genérico para el Discovery Agent.

QUÉ HACE
========
Custodia la PUERTA DE SALIDA del MVP de CUALQUIER discovery. Claude Code lo
ejecuta antes de cada Write/Edit. El script se auto-ubica: deriva la carpeta del
discovery desde la RUTA del archivo que se va a escribir, así que no depende de
un discovery en particular. Funciona igual para discoveries/citasalud que para
discoveries/latam-conciliacion o cualquier otro.

Solo actúa cuando la escritura apunta a <discovery>/outputs/mvp-canvas.md o
<discovery>/outputs/user-stories.md. Cualquier otra escritura pasa sin tocar.

CÓMO SE UBICA
=============
Dada la ruta  <algo>/<discovery>/outputs/mvp-canvas.md , deduce:
  outputs_dir   = <algo>/<discovery>/outputs
  discovery_dir = <algo>/<discovery>
  interviews    = <algo>/<discovery>/interviews
  evidence-map  = <algo>/<discovery>/outputs/evidence-map.json
y valida la evidencia de ESE discovery.

QUÉ VALIDA (independiente, no confía en el self-report del modelo)
==================================================================
1. Existe <discovery>/outputs/evidence-map.json (lo produce /discovery:analyze).
2. Hay al menos MIN_INTERVIEWS entrevistas en <discovery>/interviews/.
3. Cada persona PRIMARIA está respaldada por una entrevista en PRIMERA PERSONA
   que exista en disco (no basta con que la mencionen en la de otro).
4. Ningún DOLOR HUÉRFANO: cada dolor cita una fuente que existe en disco.

Si todo pasa -> exit 0 (permite). Si algo falla -> exit 2 (bloquea) + motivo.
Doc de hooks: https://docs.claude.com/en/docs/claude-code/hooks
"""

import json
import os
import sys
import glob
import re

MIN_INTERVIEWS = int(os.environ.get("DISCOVERY_MIN_INTERVIEWS", "2"))
GATED_FILES = {"mvp-canvas.md", "user-stories.md"}


def fail(reason_lines):
    border = "─" * 64
    print(f"\n{border}", file=sys.stderr)
    print("✗ HOOK readiness-gate: evidencia insuficiente para generar el MVP",
          file=sys.stderr)
    print(border, file=sys.stderr)
    for line in reason_lines:
        print(line, file=sys.stderr)
    print(border, file=sys.stderr)
    print("Acción: levanta más evidencia (agrega/entrevista) y reintenta.",
          file=sys.stderr)
    print(f"{border}\n", file=sys.stderr)
    sys.exit(2)


def allow():
    sys.exit(0)


def resolve_discovery(file_path, cwd):
    """
    Deriva (interviews_dir, outputs_dir) del discovery a partir de la ruta del
    archivo custodiado. Devuelve None si la ruta no tiene forma
    <discovery>/outputs/<archivo> (en cuyo caso no sabemos validar -> permitir).
    """
    if not os.path.isabs(file_path):
        file_path = os.path.join(cwd, file_path)
    file_path = os.path.normpath(file_path)
    outputs_dir = os.path.dirname(file_path)
    if os.path.basename(outputs_dir) != "outputs":
        return None
    discovery_dir = os.path.dirname(outputs_dir)
    interviews_dir = os.path.join(discovery_dir, "interviews")
    return interviews_dir, outputs_dir


def first_person_roles_on_disk(interviews_dir):
    roles = set()
    count = 0
    for path in glob.glob(os.path.join(interviews_dir, "*.md")):
        count += 1
        try:
            with open(path, encoding="utf-8") as fh:
                head = fh.read(800)
        except OSError:
            continue
        primera = re.search(r"primera_persona:\s*true", head)
        rolm = re.search(r"rol_entrevistado:\s*([A-Za-z_\-]+)", head)
        if primera and rolm:
            roles.add(rolm.group(1).strip().lower())
    return roles, count


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        allow()

    file_path = (payload.get("tool_input", {}) or {}).get("file_path", "") or ""
    target = os.path.basename(file_path)
    if target not in GATED_FILES:
        allow()

    cwd = payload.get("cwd") or os.getcwd()
    located = resolve_discovery(file_path, cwd)
    if located is None:
        allow()  # no podemos ubicar el discovery: no bloqueamos a ciegas
    interviews_dir, outputs_dir = located
    evidence_path = os.path.join(outputs_dir, "evidence-map.json")

    if not os.path.exists(evidence_path):
        fail([
            f"  Falta {os.path.relpath(evidence_path, cwd)}.",
            "  Corre primero  /discovery:analyze <discovery>  para generarlo.",
        ])

    try:
        with open(evidence_path, encoding="utf-8") as fh:
            evidence = json.load(fh)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        fail([f"  evidence-map.json no es JSON válido: {exc}"])

    personas = evidence.get("personas", [])
    pains = evidence.get("pains", [])
    problems = []

    fp_roles, interview_count = first_person_roles_on_disk(interviews_dir)
    if interview_count < MIN_INTERVIEWS:
        problems.append(
            f"  • Solo hay {interview_count} entrevista(s) en "
            f"{os.path.relpath(interviews_dir, cwd)}; se requieren al menos {MIN_INTERVIEWS}."
        )

    for p in personas:
        if not p.get("primary", True):
            continue
        name = p.get("name", "(sin nombre)")
        role = (p.get("role") or "").strip().lower()
        if role and role not in fp_roles:
            problems.append(
                f"  • Persona «{name}» (rol: {role}) no tiene una entrevista "
                f"en primera persona en disco. Está construida de oídas."
            )

    for d in pains:
        src = (d.get("source") or "").strip()
        pid = d.get("id", "(dolor sin id)")
        if not src:
            problems.append(f"  • Dolor «{pid}» no cita ninguna entrevista fuente.")
        elif not os.path.exists(os.path.join(interviews_dir, src)):
            problems.append(
                f"  • Dolor «{pid}» cita «{src}», que no existe en interviews/."
            )

    if problems:
        fail(problems)
    allow()


if __name__ == "__main__":
    main()