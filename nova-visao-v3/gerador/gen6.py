import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
from trace import trace
from gen2 import TA, WM_W, WM_H, WM_BASE, ORANGE, WHITE

OUT = "/home/user/Claude/nova-visao-v3"
SVGD = os.path.join(OUT, "svg-popular-gpt"); os.makedirs(SVGD, exist_ok=True)
im = Image.open('/root/.claude/uploads/e19f6b0b-622f-5ee1-a4a5-f14c5bc9806b/38d71c23-image.png').convert('RGB')
G = [(77, 501, 534), (576, 1001, 533), (1071, 1496, 546), (1571, 1996, 553)]
SYM = []
for (x0, x1, y1) in G:
    box = (x0 - 4, 154, x1 + 5, y1 + 5)
    d, w, h = trace(im, box, up=3, thr=195, alpha=1.15)
    SYM.append(dict(d=d, w=w, h=h))
json.dump(SYM, open('gpt/popular_traced.json', 'w'))


def sym_svg(i, fill, bg=None, pad=0):
    s = SYM[i]
    r = f'<rect x="{-pad}" y="{-pad}" width="{s["w"]+2*pad}" height="{s["h"]+2*pad}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {s["w"]+2*pad} {s["h"]+2*pad}">{r}'
            f'<path d="{s["d"]}" fill="{fill}" fill-rule="evenodd"/></svg>')


def lockup(i, color, bg, pad=40):
    s = SYM[i]
    ws = 0.5
    ch = WM_BASE * ws * 1.35
    k = ch / s["h"]
    cw = s["w"] * k
    wx = cw + 30
    wy = ch - WM_BASE * ws
    ds = 0.5
    sym = f'<path d="{s["d"]}" transform="scale({k:.4f})" fill="{color}" fill-rule="evenodd"/>'
    wm = f'<path d="{TA["wordmark"]["d"]}" transform="translate({wx:.2f},{wy:.2f}) scale({ws})" fill="{color}" fill-rule="evenodd"/>'
    W = wx + WM_W * ws
    H = ch + 4
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {W+2*pad:.1f} {H+2*pad:.1f}">'
            f'<rect x="{-pad}" y="{-pad}" width="{W+2*pad:.1f}" height="{H+2*pad:.1f}" fill="{bg}"/>{sym}{wm}</svg>')


for i in range(4):
    n = i + 1
    open(os.path.join(SVGD, f"var{n}-simbolo-laranja.svg"), "w").write(sym_svg(i, ORANGE, pad=20))
    open(os.path.join(SVGD, f"var{n}-simbolo-branco-sobre-laranja.svg"), "w").write(sym_svg(i, WHITE, ORANGE, pad=20))
    open(os.path.join(SVGD, f"var{n}-horizontal-laranja.svg"), "w").write(lockup(i, ORANGE, WHITE))
    open(os.path.join(SVGD, f"var{n}-horizontal-branco-sobre-laranja.svg"), "w").write(lockup(i, WHITE, ORANGE))

css = """*{box-sizing:border-box;margin:0}body{background:#FAF6F1;color:#2B1A12;font:16px/1.45 'Inter',system-ui,sans-serif;padding:48px;width:1700px}
h1{font-size:40px;letter-spacing:-.02em;margin-bottom:6px}.sub{color:#6B5B52;font-size:19px;margin-bottom:26px;max-width:1200px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}.card{background:#fff;border:1px solid #E6DDD3;border-radius:18px;padding:18px}
.card h2{font-size:21px;margin:10px 0 8px}.big svg{width:100%;display:block}.row{margin-top:10px;border-top:1px solid #EFE7DE;padding-top:10px}.row svg{width:100%;display:block}
.on{border-radius:12px;overflow:hidden;margin-top:10px}.on svg{width:100%;display:block}.sm{display:flex;gap:16px;align-items:flex-end;margin-top:12px}.sm svg{display:block}"""
cards = ""
for i in range(4):
    sm = "".join(f'<div style="width:{p}px">{sym_svg(i, ORANGE)}</div>' for p in (96, 48, 32, 16))
    cards += (f'<div class="card"><div class="big">{sym_svg(i, ORANGE, pad=10)}</div><h2>Variação {i+1}</h2>'
              f'<div class="row">{lockup(i, ORANGE, WHITE, 18)}</div><div class="on">{lockup(i, WHITE, ORANGE, 18)}</div><div class="sm">{sm}</div></div>')
html = (f'<!doctype html><meta charset="utf-8"><style>{css}</style><body><h1>As 4 do ChatGPT, vetorizadas</h1>'
        f'<p class="sub">Símbolos refeitos em vetor limpo e juntos com a sua tipografia laranja. Cada um aparece grande, na logo horizontal, em branco sobre laranja e em tamanhos pequenos.</p><div class="grid">{cards}</div></body>')
open(os.path.join(OUT, "popular-gpt-vetor.html"), "w").write(html)
print("ok")
