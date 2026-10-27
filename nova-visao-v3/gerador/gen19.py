import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen2 import TA, WM_W, WM_H, ORANGE, WHITE
OUT = "/home/user/Claude/nova-visao-v3"
SD = os.path.join(OUT, "sistema")
S = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gpt/popular_traced.json")))[3]
W0, H0 = S["w"], S["h"]


def sym(col, mirror, pad=14, bg=None):
    t = f'transform="translate({W0},0) scale(-1,1)"' if mirror else ""
    r = f'<rect x="{-pad}" y="{-pad}" width="{W0+2*pad}" height="{H0+2*pad}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {W0+2*pad} {H0+2*pad}">{r}<g {t}><path d="{S["d"]}" fill="{col}" fill-rule="evenodd"/></g></svg>'


def horiz(col, bg, mirror, pad=44):
    ws = 0.5; ch = 158 * ws * 1.3; k = ch / H0; cw = W0 * k
    wy = ch / 2 - 105 * ws; wx = cw + 30; Wt = wx + WM_W * ws
    top = min(0, wy); bot = max(ch, wy + WM_H * ws); H = bot - top
    t = f'transform="translate({W0},0) scale(-1,1)"' if mirror else ""
    body = (f'<g transform="translate(0,{-top:.2f})"><g transform="scale({k:.4f})"><g {t}><path d="{S["d"]}" fill="{col}" fill-rule="evenodd"/></g></g>'
            f'<path d="{TA["wordmark"]["d"]}" transform="translate({wx:.2f},{wy:.2f}) scale({ws})" fill="{col}" fill-rule="evenodd"/></g>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {Wt+2*pad:.1f} {H+2*pad:.1f}"><rect x="{-pad}" y="{-pad}" width="{Wt+2*pad:.1f}" height="{H+2*pad:.1f}" fill="{bg}"/>{body}</svg>'


D = "/tmp/claude-0/-home-user-Claude/e19f6b0b-622f-5ee1-a4a5-f14c5bc9806b/scratchpad/refs/diniz_symbol.png"
css = """*{box-sizing:border-box;margin:0}body{background:#FAF6F1;color:#2B1A12;font:16px/1.45 'Inter',system-ui,sans-serif;padding:48px;width:1700px}
h1{font-size:40px;letter-spacing:-.02em;margin-bottom:6px}.sub{color:#6B5B52;font-size:19px;margin-bottom:22px;max-width:1300px}
.grid{display:grid;gap:16px;grid-template-columns:repeat(3,1fr)}.card{background:#fff;border:1px solid #E6DDD3;border-radius:16px;padding:16px}
.sq{display:grid;place-items:center;height:300px}.sq svg,.sq img{max-width:100%;max-height:280px;width:auto}.card b{display:block;margin-top:8px;font-size:18px}.card span{color:#6B5B52;font-size:14.5px}
.row{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px}.row svg{width:100%;display:block}"""
html = (f'<!doctype html><meta charset="utf-8"><style>{css}</style><body><h1>P1 · espelhado</h1><p class="sub">O mesmo desenho, só invertido na horizontal: a lente grande passa para a direita e a haste para a esquerda. Nada mais muda.</p>'
        f'<div class="grid"><div class="card"><div class="sq"><img src="file://{D}"></div><b>Diniz</b><span>Lente grande à esquerda, haste à direita.</span></div>'
        f'<div class="card"><div class="sq">{sym(ORANGE, False)}</div><b>P1 atual</b><span>Lente grande à esquerda, haste à direita.</span></div>'
        f'<div class="card"><div class="sq">{sym(ORANGE, True)}</div><b>P1 espelhado</b><span>Lente grande à direita, haste à esquerda.</span></div></div>'
        f'<div class="row"><div class="card">{horiz(ORANGE, WHITE, True)}</div><div class="card" style="background:#FF5F00">{horiz(WHITE, ORANGE, True)}</div></div></body>')
open(os.path.join(OUT, "p1-espelhado.html"), "w").write(html)
open(os.path.join(SD, "popular-espelhado-horizontal-laranja.svg"), "w").write(horiz(ORANGE, WHITE, True))
open(os.path.join(SD, "popular-espelhado-horizontal-branco-sobre-laranja.svg"), "w").write(horiz(WHITE, ORANGE, True))
open(os.path.join(SD, "popular-espelhado-simbolo-laranja.svg"), "w").write(sym(ORANGE, True))
print("ok")
