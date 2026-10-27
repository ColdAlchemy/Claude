import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen2 import TA, WM_W, WM_H, ORANGE, WHITE
OUT = "/home/user/Claude/nova-visao-v3"
SD = os.path.join(OUT, "sistema"); os.makedirs(SD, exist_ok=True)
SYM = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gpt/popular_traced.json")))


def symbol(i, col, bg=None, pad=14):
    s = SYM[i]
    r = f'<rect x="{-pad}" y="{-pad}" width="{s["w"]+2*pad}" height="{s["h"]+2*pad}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {s["w"]+2*pad} {s["h"]+2*pad}">{r}<path d="{s["d"]}" fill="{col}" fill-rule="evenodd"/></svg>'


def horiz(i, col, bg, pad=40):
    s = SYM[i]
    ws = 0.5; ch = 158 * ws * 1.3; k = ch / s["h"]; cw = s["w"] * k
    wy = ch / 2 - 105 * ws; wx = cw + 30; Wt = wx + WM_W * ws
    top = min(0, wy); bot = max(ch, wy + WM_H * ws); H = bot - top
    body = (f'<g transform="translate(0,{-top:.2f})"><g transform="scale({k:.4f})"><path d="{s["d"]}" fill="{col}" fill-rule="evenodd"/></g>'
            f'<path d="{TA["wordmark"]["d"]}" transform="translate({wx:.2f},{wy:.2f}) scale({ws})" fill="{col}" fill-rule="evenodd"/></g>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {Wt+2*pad:.1f} {H+2*pad:.1f}"><rect x="{-pad}" y="{-pad}" width="{Wt+2*pad:.1f}" height="{H+2*pad:.1f}" fill="{bg}"/>{body}</svg>'


css = """*{box-sizing:border-box;margin:0}body{background:#FAF6F1;color:#2B1A12;font:16px/1.45 'Inter',system-ui,sans-serif;padding:48px;width:1700px}
h1{font-size:40px;letter-spacing:-.02em;margin-bottom:6px}.sub{color:#6B5B52;font-size:19px;margin-bottom:22px;max-width:1300px}
.grid{display:grid;gap:16px;grid-template-columns:1fr 1fr}.card{background:#fff;border:1px solid #E6DDD3;border-radius:16px;padding:16px}
.top{display:grid;grid-template-columns:200px 1fr;gap:16px;align-items:center}.top svg{width:100%;display:block}.card h2{font-size:21px;margin-bottom:8px}
.row svg{width:100%;display:block;margin-top:8px}.on{background:#FF5F00;border-radius:10px;overflow:hidden;margin-top:8px}.on svg{width:100%;display:block}
.sm{display:flex;gap:16px;align-items:flex-end;margin-top:10px}.sm svg{display:block}"""
cards = ""
for i in range(4):
    sm = "".join(f'<div style="width:{w}px">{symbol(i, ORANGE)}</div>' for w in (90, 56, 36, 22))
    cards += (f'<div class="card"><h2>Variação {i+1}</h2><div class="top"><div>{symbol(i, ORANGE)}</div><div>{horiz(i, ORANGE, WHITE)}</div></div>'
              f'<div class="on">{horiz(i, WHITE, ORANGE)}</div><div class="sm">{sm}</div></div>')
    open(os.path.join(SD, f"p1-var{i+1}-horizontal-laranja.svg"), "w").write(horiz(i, ORANGE, WHITE))
    open(os.path.join(SD, f"p1-var{i+1}-horizontal-branco-sobre-laranja.svg"), "w").write(horiz(i, WHITE, ORANGE))
open(os.path.join(OUT, "p1-variacoes.html"), "w").write(f'<!doctype html><meta charset="utf-8"><style>{css}</style><body><h1>As 4 variações do P1</h1><p class="sub">As 4 do ChatGPT, vetorizadas, com as suas letras e o texto alinhado ao centro do símbolo. A variação 4 é a que vínhamos usando.</p><div class="grid">{cards}</div></body>')
print("ok")
