import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen2 import COR, COR5, b_glasses, ORANGE, WHITE, CAFE, f2

OUT = "/home/user/Claude/nova-visao-v3"

SHAPES = {
    "Quadrado arredondado": ('<rect width="240" height="240" rx="58" fill="{c}"/>', 0, 1.0),
    "Círculo (selo)": ('<circle cx="120" cy="120" r="120" fill="{c}"/>', 0, 0.92),
    "Arco (janela)": ('<path d="M0,120 A120,120 0 0 1 240,120 V222 Q240,240 222,240 H18 Q0,240 0,222 Z" fill="{c}"/>', 22, 0.92),
    "Lente (olho)": ('<path d="M-30,120 Q120,-28 270,120 Q120,268 -30,120 Z" fill="{c}"/>', 0, 0.95),
}


def tile(name, bg, glass, wide=False):
    shape, dy, k = SHAPES[name]
    vb = "-30 0 300 240" if name == "Lente (olho)" else "0 0 240 240"
    g = b_glasses(glass, sw=7.2, detail=False, temples=False)
    s = 0.88 * k
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">{shape.format(c=bg)}'
            f'<g transform="translate(120 {120+dy}) scale({s}) translate(-150 -78)">{g}</g></svg>')


def lockup_stack(name, bg, glass, text):
    S = 100
    items, W = COR.shape("NOVA VISÃO", S, 0.14)
    shape, dy, k = SHAPES[name]
    cs = 200
    cont = tile(name, bg, glass).replace('<svg xmlns="http://www.w3.org/2000/svg" ', f'<svg x="{W/2 - cs/2 * (1.25 if name == "Lente (olho)" else 1):.1f}" y="0" width="{cs * (1.25 if name == "Lente (olho)" else 1):.1f}" height="{cs}" ')
    base = cs + 34 + COR.cap * S
    wm = f'<path d="{COR.path(items, S, 0, base)}" fill="{text}"/>'
    its, w5 = COR5.shape("ÓTICA", 27, 0.62)
    d5 = COR5.path(its, 27, W / 2 - w5 / 2, base + 74)
    gap = 27
    lw = (W - w5) / 2 - gap
    ly = base + 74 - COR5.cap * 27 * 0.5
    rules = f'<path d="M0,{ly:.2f} H{lw:.2f} M{W-lw:.2f},{ly:.2f} H{W:.2f}" stroke="{text}" stroke-width="1.8"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-40 -30 {W+80:.1f} {base+130:.1f}">{cont}{wm}<path d="{d5}" fill="{text}"/>{rules}</svg>')


css = """
*{box-sizing:border-box;margin:0}
body{background:#FAF6F1;color:#2B1A12;font:16px/1.45 'Inter',system-ui,sans-serif;padding:48px;width:1700px}
h1{font-size:40px;letter-spacing:-.02em;margin-bottom:6px}
.sub{color:#6B5B52;font-size:19px;margin-bottom:28px;max-width:1200px}
h2{font-size:22px;margin:30px 0 12px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}
.card{background:#fff;border:1px solid #E6DDD3;border-radius:18px;padding:18px;text-align:center}
.card svg{width:100%;height:210px;display:block}
.card b{display:block;margin-top:10px;font-size:17px}
.card span{color:#6B5B52;font-size:14px}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:6px}
.pair svg{height:150px}
.lock{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}
.lock .card svg{height:340px}
"""
names = list(SHAPES)
notes = {
    "Quadrado arredondado": "É o mesmo do popular. Fica pesado e comum para premium.",
    "Círculo (selo)": "Lembra carimbo e lacre. Elegante, mas muito visto.",
    "Arco (janela)": "Janela da vitrine, e “visão” é olhar por uma janela. É o que mais combina com premium.",
    "Lente (olho)": "Container em forma de olho, ao estilo da Zeiss. Conceitual e diferente.",
}
cards = ""
for n in names:
    cards += (f'<div class="card"><div class="pair">{tile(n, ORANGE, WHITE)}{tile(n, CAFE, ORANGE)}</div>'
              f'<b>{n}</b><span>{notes[n]}</span></div>')
locks = ""
for n, bg, glass, text, lab in [("Arco (janela)", ORANGE, WHITE, ORANGE, "Arco em laranja"),
                                ("Arco (janela)", CAFE, ORANGE, CAFE, "Arco em café com laranja"),
                                ("Círculo (selo)", CAFE, WHITE, CAFE, "Selo em café"),
                                ("Lente (olho)", ORANGE, WHITE, ORANGE, "Lente em laranja")]:
    locks += f'<div class="card">{lockup_stack(n, bg, glass, text)}<b>{lab}</b></div>'
html = (f'<!doctype html><meta charset="utf-8"><style>{css}</style><body><h1>Premium com container: funciona?</h1>'
        f'<p class="sub">Sim, funciona. Mas o container não deve ser o mesmo quadrado arredondado do popular. Veja 4 formatos, cada um em laranja com óculos branco e em café com óculos laranja.</p>'
        f'<div class="grid">{cards}</div><h2>Como ficaria na logo completa</h2><div class="lock">{locks}</div></body>')
open(os.path.join(OUT, "container-premium.html"), "w").write(html)
print("ok")
