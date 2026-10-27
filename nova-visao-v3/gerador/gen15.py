import os, sys, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from gen2 import TA, WM_W, WM_H, WM_BASE, ORANGE, WHITE

OUT = "/home/user/Claude/nova-visao-v3"
SD = os.path.join(OUT, "sistema"); os.makedirs(SD, exist_ok=True)
SYM = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gpt/popular_traced.json")))[3]
XH_TOP, BASE = 52.0, 158.0


def horizontal(mode, color=ORANGE, bg=WHITE, pad=44, guides=False):
    s = SYM
    ws = 0.5
    text_h = BASE * ws                       # do topo (pingo do i, til) até a linha de base
    xh = (BASE - XH_TOP) * ws                # altura-x
    if mode == "A":      # centro da altura-x no centro do símbolo
        ch = text_h * 1.3; wy = ch / 2 - ((XH_TOP + BASE) / 2) * ws
    elif mode == "B":    # centro da caixa inteira do texto (com pingo e til) no centro do símbolo
        ch = text_h * 1.3; wy = ch / 2 - (BASE / 2) * ws
    elif mode == "C":    # símbolo do tamanho da caixa do texto, topo no topo e base na linha de base
        ch = text_h; wy = 0
    else:                # D: símbolo maior, altura-x centrada, texto 12% maior
        ws = 0.56; text_h = BASE * ws
        ch = text_h * 1.28; wy = ch / 2 - ((XH_TOP + BASE) / 2) * ws
    k = ch / s["h"]
    cw = s["w"] * k
    wx = cw + 30
    W = wx + WM_W * ws
    top = min(0, wy)
    bottom = max(ch, wy + WM_H * ws)
    H = bottom - top
    body = (f'<g transform="translate(0,{-top:.2f})"><g transform="scale({k:.4f})"><path d="{s["d"]}" fill="{color}" fill-rule="evenodd"/></g>'
            f'<path d="{TA["wordmark"]["d"]}" transform="translate({wx:.2f},{wy:.2f}) scale({ws})" fill="{color}" fill-rule="evenodd"/></g>')
    g = ""
    if guides:
        cy = ch / 2 - top
        g = f'<line x1="-10" x2="{W+10:.1f}" y1="{cy:.1f}" y2="{cy:.1f}" stroke="#888" stroke-width="0.8" stroke-dasharray="4 4"/>'
        bl = wy + BASE * ws - top
        g += f'<line x1="-10" x2="{W+10:.1f}" y1="{bl:.1f}" y2="{bl:.1f}" stroke="#bbb" stroke-width="0.8" stroke-dasharray="2 4"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {W+2*pad:.1f} {H+2*pad:.1f}"><rect x="{-pad}" y="{-pad}" width="{W+2*pad:.1f}" height="{H+2*pad:.1f}" fill="{bg}"/>{body}{g}</svg>')


if __name__ == "__main__":
    LAB = {"A": ("A · Centro da altura-x", "O centro das letras minúsculas fica no centro do símbolo. É o alinhamento óptico clássico."),
           "B": ("B · Centro da caixa do texto", "Considera o pingo do “i” e o til. As letras descem um pouco em relação ao A."),
           "C": ("C · Mesma altura", "O símbolo ocupa do topo do pingo/til até a linha de base. Bloco compacto e alinhado nos dois lados."),
           "D": ("D · Texto maior e centrado", "Símbolo e texto crescem juntos, com o centro da altura-x no centro do símbolo.")}
    css = """*{box-sizing:border-box;margin:0}body{background:#FAF6F1;color:#2B1A12;font:16px/1.45 'Inter',system-ui,sans-serif;padding:48px;width:1700px}
h1{font-size:40px;letter-spacing:-.02em;margin-bottom:6px}.sub{color:#6B5B52;font-size:19px;margin-bottom:22px;max-width:1250px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.card{background:#fff;border:1px solid #E6DDD3;border-radius:16px;padding:14px}.card svg{width:100%;display:block;border-radius:8px}
.card h2{font-size:21px;margin:10px 0 2px}.card p{color:#6B5B52;font-size:15px}.row{display:grid;grid-template-columns:1fr 1fr;gap:10px}"""
    cards = ""
    for m in "ABCD":
        open(os.path.join(SD, f"popular-horizontal-{m}-laranja.svg"), "w").write(horizontal(m))
        open(os.path.join(SD, f"popular-horizontal-{m}-branco-sobre-laranja.svg"), "w").write(horizontal(m, WHITE, ORANGE))
        cards += (f'<div class="card"><div class="row">{horizontal(m, guides=True)}{horizontal(m, WHITE, ORANGE)}</div><h2>{LAB[m][0]}</h2><p>{LAB[m][1]}</p></div>')
    html = (f'<!doctype html><meta charset="utf-8"><style>{css}</style><body><h1>P1 · alinhando o texto ao símbolo</h1>'
            f'<p class="sub">Antes o texto ficava com a linha de base na base do símbolo, então parecia caído. Aqui estão 4 jeitos de alinhar. A linha tracejada é o centro do símbolo e a pontilhada é a linha de base do texto.</p><div class="grid">{cards}</div></body>')
    open(os.path.join(OUT, "p1-alinhamento.html"), "w").write(html)
    print("ok")
