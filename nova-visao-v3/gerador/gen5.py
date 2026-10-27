import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen2 import COR, COR5, ORANGE, WHITE, CAFE
from gen4 import SHAPES

OUT = "/home/user/Claude/nova-visao-v3"
T = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gpt/prem_traced.json")))
NAMES = {"1": "Aro redondo clássico", "2": "Quadrado arredondado", "3": "Oval e leve", "4": "Gatinho sofisticado"}


def sym(i, color, cx, cy, width):
    t = T[str(i)]
    x0, y0, x1, y1 = t["bbox"]
    s = width / (x1 - x0)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    return f'<g transform="translate({cx} {cy}) scale({s:.4f}) translate({-mx} {-my})"><path d="{t["d"]}" fill="{color}" fill-rule="evenodd"/></g>'


def tile(i, shape, bg, fg, w=168):
    body, dy, k = SHAPES[shape]
    vb = "-30 0 300 240" if shape == "Lente (olho)" else "0 0 240 240"
    ww = w * (1.12 if shape == "Lente (olho)" else 1)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">{body.format(c=bg)}{sym(i, fg, 120, 120 + dy, ww)}</svg>'


def lock(i, shape, bg, fg, text):
    S = 100
    items, W = COR.shape("NOVA VISÃO", S, 0.14)
    cs = 200
    cw = cs * (1.25 if shape == "Lente (olho)" else 1)
    cont = tile(i, shape, bg, fg).replace('<svg xmlns="http://www.w3.org/2000/svg" ', f'<svg x="{W/2 - cw/2:.1f}" y="0" width="{cw:.1f}" height="{cs}" ')
    base = cs + 34 + COR.cap * S
    wm = f'<path d="{COR.path(items, S, 0, base)}" fill="{text}"/>'
    its, w5 = COR5.shape("ÓTICA", 27, 0.62)
    d5 = COR5.path(its, 27, W / 2 - w5 / 2, base + 74)
    lw = (W - w5) / 2 - 27
    ly = base + 74 - COR5.cap * 27 * 0.5
    rules = f'<path d="M0,{ly:.2f} H{lw:.2f} M{W-lw:.2f},{ly:.2f} H{W:.2f}" stroke="{text}" stroke-width="1.8"/>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-40 -30 {W+80:.1f} {base+130:.1f}">{cont}{wm}<path d="{d5}" fill="{text}"/>{rules}</svg>'


css = """*{box-sizing:border-box;margin:0}body{background:#FAF6F1;color:#2B1A12;font:16px/1.45 'Inter',system-ui,sans-serif;padding:48px;width:1700px}
h1{font-size:40px;letter-spacing:-.02em;margin-bottom:6px}.sub{color:#6B5B52;font-size:19px;margin-bottom:26px;max-width:1200px}
h2{font-size:22px;margin:30px 0 12px}.grid{display:grid;grid-template-columns:150px repeat(4,1fr);gap:14px;align-items:center}
.card{background:#fff;border:1px solid #E6DDD3;border-radius:16px;padding:10px}.card svg{width:100%;height:190px;display:block}
.hd{font-weight:700;text-align:center;color:#6B5B52;font-size:16px}.rl{font-weight:700;font-size:17px}
.lock{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}.lock .card svg{height:340px}.lock b{display:block;text-align:center;margin:6px 0}"""
cols = [("Arco (janela)", ORANGE, WHITE, "Arco · laranja"), ("Arco (janela)", CAFE, ORANGE, "Arco · café"),
        ("Círculo (selo)", CAFE, WHITE, "Selo · café"), ("Lente (olho)", ORANGE, WHITE, "Lente · laranja")]
rows = "<div></div>" + "".join(f'<div class="hd">{c[3]}</div>' for c in cols)
for i in range(1, 5):
    rows += f'<div class="rl">{i} · {NAMES[str(i)]}</div>'
    for (sh, bg, fg, _) in cols:
        rows += f'<div class="card">{tile(i, sh, bg, fg)}</div>'
locks = ""
for (i, sh, bg, fg, tx, lab) in [(1, "Arco (janela)", CAFE, ORANGE, CAFE, "Aro clássico · arco café"), (3, "Arco (janela)", ORANGE, WHITE, ORANGE, "Oval e leve · arco laranja"),
                                 (2, "Círculo (selo)", CAFE, WHITE, CAFE, "Quadrado · selo café"), (4, "Lente (olho)", ORANGE, WHITE, ORANGE, "Gatinho · lente laranja")]:
    locks += f'<div class="card">{lock(i, sh, bg, fg, tx)}<b>{lab}</b></div>'
html = (f'<!doctype html><meta charset="utf-8"><style>{css}</style><body><h1>Seus símbolos premium nos containers</h1>'
        f'<p class="sub">Os 4 símbolos que o ChatGPT gerou, vetorizados por mim e colocados nos formatos de container, em laranja e em café.</p>'
        f'<div class="grid">{rows}</div><h2>Logo completa</h2><div class="lock">{locks}</div></body>')
open(os.path.join(OUT, "container-simbolos-gpt.html"), "w").write(html)
print("ok")
