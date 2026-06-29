#!/usr/bin/env python3
"""
build-report.py — Genera un reporte HTML visual y a color de un discovery.

Lee los artefactos ESTRUCTURADOS del discovery (evidence-map.json y
experiment-board.json) y produce un dashboard autocontenido en
<discovery>/outputs/report.html, con la paleta de las diapositivas del curso.

Es DETERMINISTA y sin dependencias (solo stdlib): el mismo input produce el mismo
output, sin depender del modelo. Misma filosofía que los hooks: lógica en código.

USO
===
    python3 .claude/scripts/build-report.py <carpeta-del-discovery>
    # p. ej.
    python3 .claude/scripts/build-report.py discoveries/citasalud

Codificación de color (leyenda en el propio reporte):
- Respaldo de persona:  primera mano = verde · referenciada = ámbar
- Riesgo de hipótesis:  alto = rojo · medio = ámbar · bajo = verde
- Cadena de valor:      output (azul) → outcome (azul medio) → impact (ámbar)
"""

import json
import os
import sys
import glob
import re
import html
from datetime import date

# ---- paleta (coincide con las diapositivas) ----
PAPER = "#F3F4F1"; INK = "#0E1A26"; BLUE = "#1A4E8A"; BLUE2 = "#3E6FA6"
AMBER = "#E89B0C"; AMBER_INK = "#9A6605"
GREEN = "#2E7D52"; GREEN_BG = "#E3F1E8"
RED = "#B3402F"; RED_BG = "#F6E2DD"
AMBER_BG = "#F6E3BC"; BLUE_BG = "#E2EAF3"

RISK_COLORS = {
    "alto":  (RED, RED_BG),
    "medio": (AMBER_INK, AMBER_BG),
    "bajo":  (GREEN, GREEN_BG),
}


def esc(x):
    return html.escape(str(x), quote=True)


def load_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError, ValueError):
        return None


def first_person_roles(interviews_dir):
    roles = {}
    for path in glob.glob(os.path.join(interviews_dir, "*.md")):
        try:
            head = open(path, encoding="utf-8").read(800)
        except OSError:
            continue
        rolm = re.search(r"rol_entrevistado:\s*([A-Za-z_\-]+)", head)
        fp = re.search(r"primera_persona:\s*true", head)
        if rolm and fp:
            roles[rolm.group(1).strip().lower()] = os.path.basename(path)
    return roles


def chip(text, fg, bg):
    return (f'<span style="display:inline-block;padding:2px 10px;border-radius:999px;'
            f'font:600 12px/1.6 ui-monospace,Menlo,monospace;color:{fg};'
            f'background:{bg};white-space:nowrap">{esc(text)}</span>')


def build(discovery_dir):
    name = os.path.basename(os.path.normpath(discovery_dir))
    out_dir = os.path.join(discovery_dir, "outputs")
    interviews_dir = os.path.join(discovery_dir, "interviews")
    evidence = load_json(os.path.join(out_dir, "evidence-map.json")) or {}
    board = load_json(os.path.join(out_dir, "experiment-board.json")) or {}

    personas = evidence.get("personas", [])
    pains = evidence.get("pains", [])
    hyps = board.get("hypotheses", [])
    fp_roles = first_person_roles(interviews_dir)
    n_interviews = len(glob.glob(os.path.join(interviews_dir, "*.md")))

    # agrupar dolores por persona
    pains_by_persona = {}
    for d in pains:
        pains_by_persona.setdefault(d.get("persona", "(sin persona)"), []).append(d)

    parts = []
    A = parts.append

    # ---------- HEAD ----------
    A(f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Discovery — {esc(name)}</title>
<style>
  :root{{--paper:{PAPER};--ink:{INK};--blue:{BLUE};--blue2:{BLUE2};--amber:{AMBER};--amber-ink:{AMBER_INK}}}
  *{{box-sizing:border-box}}
  body{{margin:0;background:var(--paper);color:var(--ink);
    font-family:'IBM Plex Sans',-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;line-height:1.5}}
  .wrap{{max-width:1000px;margin:0 auto;padding:32px 24px 80px}}
  .eyebrow{{font:600 12px/1.6 ui-monospace,Menlo,monospace;letter-spacing:.12em;
    text-transform:uppercase;color:var(--blue)}}
  h1{{font-size:34px;margin:.1em 0 .1em;letter-spacing:-.01em}}
  h2{{font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:var(--blue);
    border-bottom:2px solid var(--blue);padding-bottom:6px;margin:40px 0 18px;
    font-family:ui-monospace,Menlo,monospace}}
  h3{{font-size:17px;margin:0 0 6px}}
  .sub{{color:#3C4A57}}
  .counts{{display:flex;flex-wrap:wrap;gap:10px;margin-top:14px}}
  .stat{{background:#fff;border:1px solid #D7DCE2;border-radius:12px;padding:10px 16px;min-width:96px}}
  .stat b{{display:block;font-size:24px;line-height:1.1}}
  .stat span{{font-size:12px;color:#3C4A57}}
  .legend{{display:flex;flex-wrap:wrap;gap:18px;background:#fff;border:1px solid #D7DCE2;
    border-radius:12px;padding:14px 18px;margin-top:18px;font-size:13px}}
  .legend div{{display:flex;align-items:center;gap:7px}}
  .dot{{width:12px;height:12px;border-radius:3px;display:inline-block}}
  .grid{{display:grid;gap:16px}}
  .cards3{{grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}}
  .card{{background:#fff;border:1px solid #D7DCE2;border-radius:14px;padding:18px}}
  .card.persona{{border-top:5px solid var(--blue)}}
  ul.clean{{margin:8px 0 0;padding-left:18px}}
  ul.clean li{{margin:3px 0}}
  .flow{{display:flex;align-items:stretch;gap:0;flex-wrap:wrap;margin-top:8px}}
  .flow .node{{flex:1;min-width:150px;border-radius:12px;padding:14px 16px;color:#fff}}
  .flow .arrow{{display:flex;align-items:center;justify-content:center;padding:0 10px;
    font-size:24px;color:var(--blue)}}
  .flow .node small{{display:block;opacity:.85;font-weight:400;margin-top:4px;font-size:12.5px}}
  .hyp{{background:#fff;border:1px solid #D7DCE2;border-left:7px solid #999;border-radius:14px;
    padding:18px 20px;margin-bottom:14px}}
  .hyp .head{{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}}
  .hyp dl{{display:grid;grid-template-columns:140px 1fr;gap:6px 14px;margin:12px 0 0;font-size:14px}}
  .hyp dt{{font:600 12px/1.7 ui-monospace,Menlo,monospace;letter-spacing:.06em;
    text-transform:uppercase;color:#3C4A57}}
  .hyp dd{{margin:0}}
  table{{border-collapse:collapse;width:100%;background:#fff;border:1px solid #D7DCE2;
    border-radius:12px;overflow:hidden;font-size:14px}}
  th,td{{text-align:left;padding:10px 14px;border-bottom:1px solid #E7EAEE;vertical-align:top}}
  th{{background:var(--blue-bg,#E2EAF3);font:600 12px/1.6 ui-monospace,Menlo,monospace;
    letter-spacing:.06em;text-transform:uppercase;color:#123A68}}
  tr:last-child td{{border-bottom:none}}
  .foot{{margin-top:48px;font-size:12px;color:#6A7682}}
  .mono{{font-family:ui-monospace,Menlo,monospace}}
</style></head><body><div class="wrap">""")

    # ---------- HEADER ----------
    A(f'<div class="eyebrow">Discovery Agent · reporte visual</div>')
    A(f'<h1>{esc(name)}</h1>')
    A(f'<div class="sub">Síntesis del descubrimiento — generado {date.today().isoformat()}.</div>')
    A('<div class="counts">')
    for val, lab in [(n_interviews, "entrevistas"), (len(personas), "personas"),
                     (len(pains), "dolores"), (len(hyps), "hipótesis")]:
        A(f'<div class="stat"><b>{val}</b><span>{lab}</span></div>')
    A('</div>')

    # ---------- LEYENDA ----------
    A('<div class="legend">')
    A(f'<div><span class="dot" style="background:{GREEN}"></span>respaldo: primera mano</div>')
    A(f'<div><span class="dot" style="background:{AMBER}"></span>respaldo: referenciada</div>')
    A(f'<div><span class="dot" style="background:{RED}"></span>riesgo alto</div>')
    A(f'<div><span class="dot" style="background:{AMBER}"></span>riesgo medio</div>')
    A(f'<div><span class="dot" style="background:{GREEN}"></span>riesgo bajo</div>')
    A('</div>')

    # ---------- PERSONAS ----------
    A('<h2>Personas y sus dolores</h2>')
    A('<div class="grid cards3">')
    for p in personas:
        pname = p.get("name", "(sin nombre)")
        role = (p.get("role") or "").strip().lower()
        backed = role in fp_roles
        fg, bg = (GREEN, GREEN_BG) if backed else (AMBER_INK, AMBER_BG)
        badge = chip("primera mano" if backed else "referenciada", fg, bg)
        src = fp_roles.get(role)
        src_line = f'<div class="sub mono" style="font-size:12px;margin-top:4px">fuente: {esc(src)}</div>' if src else \
                   '<div class="sub mono" style="font-size:12px;margin-top:4px">sin entrevista propia</div>'
        A(f'<div class="card persona"><div style="display:flex;justify-content:space-between;align-items:start;gap:8px">'
          f'<h3>{esc(pname)}</h3>{badge}</div>'
          f'<div class="sub">{esc(role)}</div>{src_line}')
        plist = pains_by_persona.get(pname, [])
        if plist:
            A('<ul class="clean">')
            for d in plist:
                A(f'<li>{esc(d.get("id",""))} '
                  f'<span class="sub mono" style="font-size:11px">({esc(d.get("source",""))})</span></li>')
            A('</ul>')
        A('</div>')
    A('</div>')

    # ---------- CADENA DE VALOR (genérica, didáctica) ----------
    A('<h2>El puente: output → outcome → impact</h2>')
    A('<div class="sub" style="margin-bottom:8px">Lo que entregamos solo vale si cambia un comportamiento y mueve un número. Cada flecha es una hipótesis a comprobar.</div>')
    A('<div class="flow">')
    A(f'<div class="node" style="background:{BLUE}">OUTPUT<small>Las funcionalidades del MVP (ver mvp-canvas.md)</small></div>')
    A('<div class="arrow">→</div>')
    A(f'<div class="node" style="background:{BLUE2}">OUTCOME<small>El cambio de comportamiento esperado en las personas</small></div>')
    A('<div class="arrow">→</div>')
    A(f'<div class="node" style="background:{AMBER}">IMPACT<small>El número de negocio que se mueve</small></div>')
    A('</div>')

    # ---------- TABLERO DE EXPERIMENTOS ----------
    A('<h2>Tablero de experimentos (hipótesis a comprobar)</h2>')
    if not hyps:
        A('<div class="sub">Aún no hay experimentos. Corre <span class="mono">/discovery:experiments</span>.</div>')
    for h in hyps:
        risk = (h.get("risk") or "medio").strip().lower()
        fg, bg = RISK_COLORS.get(risk, RISK_COLORS["medio"])
        A(f'<div class="hyp" style="border-left-color:{fg}">')
        A(f'<div class="head"><h3>{esc(h.get("id",""))} · {esc(h.get("assumption",""))}</h3>'
          f'{chip("riesgo " + risk, fg, bg)}</div>')
        A('<dl>')
        for key, lab in [("hypothesis","Hipótesis"),("metric","Señal medible"),
                         ("threshold","Criterio de éxito"),("experiment","Experimento"),
                         ("decision","Regla de decisión")]:
            if h.get(key):
                A(f'<dt>{lab}</dt><dd>{esc(h.get(key))}</dd>')
        A('</dl></div>')

    # ---------- FOOT ----------
    A(f'<div class="foot">Generado por <span class="mono">build-report.py</span> desde '
      f'<span class="mono">evidence-map.json</span> y <span class="mono">experiment-board.json</span>. '
      f'El detalle en prosa (requisitos, user stories, MVP Canvas completo) está en los .md de '
      f'<span class="mono">{esc(name)}/outputs/</span>.</div>')
    A('</div></body></html>')

    report_path = os.path.join(out_dir, "report.html")
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write("".join(parts))
    return report_path


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 build-report.py <carpeta-del-discovery>", file=sys.stderr)
        sys.exit(1)
    discovery_dir = sys.argv[1]
    out_dir = os.path.join(discovery_dir, "outputs")
    if not os.path.isdir(out_dir):
        print(f"No existe {out_dir}. ¿Corriste analyze/generate-mvp primero?", file=sys.stderr)
        sys.exit(1)
    path = build(discovery_dir)
    print(f"✓ Reporte generado: {path}")


if __name__ == "__main__":
    main()