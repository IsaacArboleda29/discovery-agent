#!/usr/bin/env python3
"""
hypothesis-gate.py — Hook PreToolUse genérico para la fase de experimentación.

QUÉ HACE
========
Custodia la salida de experimentos de CUALQUIER discovery. Se auto-ubica desde
la ruta del archivo que se escribe (igual que readiness-gate). Solo actúa cuando
la escritura apunta a <discovery>/outputs/hypotheses.md o
<discovery>/outputs/experiment-board.json. El resto pasa sin tocar.

POR QUÉ EXISTE
==============
La diapositiva 15: el puente entre output y outcome es una hipótesis, y las
hipótesis SE COMPRUEBAN. Este gate impide generar experimentos sobre hipótesis
vagas: exige que cada una sea FALSABLE (señal medible, umbral concreto, regla de
decisión que contemple el fallo) y que su métrica no sea de vanidad (prueba
ácida, diapositiva 17).

QUÉ VALIDA (sobre <discovery>/outputs/experiment-board.json)
============================================================
1. Existe <discovery>/outputs/mvp-canvas.md (los supuestos salen del MVP).
2. Hay al menos una hipótesis.
3. Cada hipótesis tiene, no vacíos: assumption, hypothesis, metric, threshold,
   decision, experiment.
4. threshold es concreto (contiene número/porcentaje).
5. decision contempla el fallo (no solo el éxito).
6. metric no es de vanidad.

Si todo pasa -> exit 0. Si algo falla -> exit 2 (bloquea) + motivo.
Doc de hooks: https://docs.claude.com/en/docs/claude-code/hooks
"""

import json
import os
import re
import sys

GATED_FILES = {"hypotheses.md", "experiment-board.json"}
VANITY_PATTERNS = [
    "descarga", "paginas vistas", "page views", "lineas de codigo",
    "features lanzadas", "funcionalidades lanzadas", "story points",
    "numero de despliegues", "numero de features", "likes", "seguidores",
]
REQUIRED_FIELDS = {
    "assumption": "supuesto a probar",
    "hypothesis": "enunciado de la hipótesis",
    "metric": "señal medible",
    "threshold": "criterio de éxito",
    "decision": "regla de decisión",
    "experiment": "experimento",
}


def _strip_accents(text):
    return text.translate(str.maketrans("áéíóúÁÉÍÓÚ", "aeiouAEIOU"))


def fail(reason_lines):
    border = "─" * 64
    print(f"\n{border}", file=sys.stderr)
    print("✗ HOOK hypothesis-gate: hipótesis no comprobables", file=sys.stderr)
    print(border, file=sys.stderr)
    for line in reason_lines:
        print(line, file=sys.stderr)
    print(border, file=sys.stderr)
    print("Una hipótesis sin señal medible, umbral y decisión no es comprobable.",
          file=sys.stderr)
    print("Reescríbela en forma falsable y reintenta.", file=sys.stderr)
    print(f"{border}\n", file=sys.stderr)
    sys.exit(2)


def allow():
    sys.exit(0)


def resolve_outputs_dir(file_path, cwd):
    if not os.path.isabs(file_path):
        file_path = os.path.join(cwd, file_path)
    file_path = os.path.normpath(file_path)
    outputs_dir = os.path.dirname(file_path)
    if os.path.basename(outputs_dir) != "outputs":
        return None
    return outputs_dir


def has_concrete_threshold(text):
    return bool(re.search(r"\d", text or ""))


def is_vanity_metric(metric):
    flat = _strip_accents((metric or "").lower())
    return any(pat in flat for pat in VANITY_PATTERNS)


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
    outputs_dir = resolve_outputs_dir(file_path, cwd)
    if outputs_dir is None:
        allow()

    board_path = os.path.join(outputs_dir, "experiment-board.json")
    mvp_path = os.path.join(outputs_dir, "mvp-canvas.md")

    if not os.path.exists(mvp_path):
        fail([
            f"  Falta {os.path.relpath(mvp_path, cwd)}.",
            "  Corre primero  /discovery:generate-mvp <discovery>  para tener supuestos que probar.",
        ])

    if not os.path.exists(board_path):
        fail([
            f"  Falta {os.path.relpath(board_path, cwd)}.",
            "  /discovery:experiments debe escribir el tablero (board) antes que el .md.",
        ])

    try:
        with open(board_path, encoding="utf-8") as fh:
            board = json.load(fh)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        fail([f"  experiment-board.json no es JSON válido: {exc}"])

    hypotheses = board.get("hypotheses", [])
    if not hypotheses:
        fail(["  El tablero no contiene ninguna hipótesis."])

    problems = []
    for h in hypotheses:
        hid = h.get("id", "(sin id)")
        for field, label in REQUIRED_FIELDS.items():
            if not str(h.get(field, "")).strip():
                problems.append(f"  • {hid}: falta «{label}» ({field}).")

        threshold = str(h.get("threshold", "")).strip()
        if threshold and not has_concrete_threshold(threshold):
            problems.append(
                f"  • {hid}: el criterio de éxito «{threshold}» no es concreto "
                f"(necesita un número o porcentaje)."
            )

        decision = _strip_accents(str(h.get("decision", "")).lower())
        if decision and not any(w in decision for w in ("si falla", "si no", "fallo", "pivot", "descart", "mata")):
            problems.append(
                f"  • {hid}: la regla de decisión no dice qué hacer SI FALLA "
                f"(una hipótesis sin salida de fallo no es comprobable)."
            )

        metric = h.get("metric", "")
        if metric and is_vanity_metric(metric):
            problems.append(
                f"  • {hid}: «{metric}» es una métrica de vanidad. "
                f"Usa una métrica de negocio (prueba ácida: si sube, ¿qué decisión cambia?)."
            )

    if problems:
        fail(problems)
    allow()


if __name__ == "__main__":
    main()