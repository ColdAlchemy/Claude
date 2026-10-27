import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen2 import TA, ORANGE, WHITE
OUT = "/home/user/Claude/nova-visao-v3"
WM = TA["wordmark"]["d"]; DS = TA["descriptor"]["d"]


def logo(extra, bg=WHITE, col=ORANGE, W=1180, H=330, pad=40):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="{bg}"/>'
            f'<g transform="translate({pad},58)"><path d="{DS}" transform="translate(0,-6) scale(.62)" fill="{col}" fill-rule="evenodd"/>'
            f'<g transform="translate(0,52)"><path d="{WM}" fill="{col}" fill-rule="evenodd"/>{extra(col)}</g></g></svg>')


def st(d, col, w=26):
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'


def end_piece(c):
    return (f'<rect x="984" y="84" width="26" height="18" fill="{c}"/>'
            f'<rect x="1001" y="72" width="26" height="42" rx="12" fill="{c}"/>')


VARS = [
    ("A · Haste que volta por baixo",
     "O último “o” vira a lente, com a dobradiça ao lado. A haste desce, volta por baixo do nome inteiro e termina na ponta curvada da orelha. Peso igual ao das letras.",
     lambda c: end_piece(c) + st("M 1014,100 C 1014,172 1000,192 944,192 H 70 C 36,192 18,184 14,166", c)),
    ("B · Haste curta no último “o”",
     "Só o último “o” ganha dobradiça e uma haste curta, que termina curvando para baixo, como numa armação vista de lado.",
     lambda c: end_piece(c) + st("M 1014,93 H 1092 C 1122,93 1136,112 1136,142", c, 24)),
]
css = """*{box-sizing:border-box;margin:0}body{background:#FAF6F1;color:#2B1A12;font:16px/1.45 'Inter',system-ui,sans-serif;padding:48px;width:1700px}
h1{font-size:40px;letter-spacing:-.02em;margin-bottom:6px}.sub{color:#6B5B52;font-size:19px;margin-bottom:26px;max-width:1250px}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}.card{background:#fff;border:1px solid #E6DDD3;border-radius:18px;padding:18px}
.card svg{width:100%;display:block}.card h2{font-size:21px;margin:6px 0 2px}.card p{color:#6B5B52;font-size:15px;margin-bottom:8px}.on{border-radius:12px;overflow:hidden;margin-top:8px}.sm{display:flex;gap:18px;align-items:center;margin-top:10px}.sm svg{display:block}"""
cards = ""
os.makedirs(os.path.join(OUT, "svg-p3"), exist_ok=True)
for i, (n, d, ex) in enumerate(VARS, 1):
    a = logo(ex); b = logo(ex, bg=ORANGE, col=WHITE)
    open(os.path.join(OUT, "svg-p3", f"p3-{i}-laranja.svg"), "w").write(a)
    open(os.path.join(OUT, "svg-p3", f"p3-{i}-branco-sobre-laranja.svg"), "w").write(b)
    sm = "".join(f'<div style="width:{w}px">{a}</div>' for w in (300, 180, 110))
    cards += f'<div class="card"><h2>{n}</h2><p>{d}</p>{a}<div class="on">{b}</div><div class="sm">{sm}</div></div>'
open(os.path.join(OUT, "p3-propostas.html"), "w").write(f'<!doctype html><meta charset="utf-8"><style>{css}</style><body><h1>P3 · a haste do óculos no nome</h1><p class="sub">A sua tipografia de verdade, com uma haste do mesmo peso das letras e a dobradiça no último “o”.</p><div class="grid">{cards}</div></body>')
print("ok")
