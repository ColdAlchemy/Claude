import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from gen2 import TA, WM_W, WM_H, WM_BASE, ORANGE, WHITE

OUT = "/home/user/Claude/nova-visao-v3"
SD = os.path.join(OUT, "sistema"); os.makedirs(SD, exist_ok=True)
S = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gpt/popular_traced.json")))[3]
W0, H0 = S["w"], S["h"]
EX, EY, TH, SL = 429.0, 131.5, 25.0, 0.37       # saída da haste: borda direita, centro, espessura e inclinação
XH_TOP, BASE = 52.0, 158.0
L = 125.0


def ext_straight(col):
    x1 = EX + L; y1 = EY + SL * L
    return (f'<path d="M{EX+0.5:.1f},{EY+SL*0.5:.1f} L{x1:.1f},{y1:.1f}" stroke="{col}" stroke-width="{TH}" fill="none" stroke-linecap="butt"/>'
            f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="{TH/2}" fill="{col}"/>')


def ext_wave(col):
    pts = []
    n = 90
    ux, uy = 1 / math.hypot(1, SL), SL / math.hypot(1, SL)
    nx, ny = -uy, ux
    for i in range(n + 1):
        t = L * i / n
        a = 10 * math.sin(2 * math.pi * t / (L * 0.62)) * min(1, t / 25)
        pts.append((EX + 0.5 + t * ux + nx * a, EY + SL * 0.5 + t * uy + ny * a))
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    ex, ey = pts[-1]
    return (f'<path d="{d}" stroke="{col}" stroke-width="{TH}" fill="none" stroke-linecap="butt" stroke-linejoin="round"/>'
            f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{TH/2}" fill="{col}"/>')


def symbol(col, ext=None, pad=0, bg=None):
    extra = ext(col) if ext else ""
    w = W0 + (L + TH if ext else 0)
    r = f'<rect x="{-pad}" y="{-pad}" width="{w+2*pad}" height="{H0+2*pad}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {w+2*pad:.1f} {H0+2*pad}">{r}'
            f'<path d="{S["d"]}" fill="{col}" fill-rule="evenodd"/>{extra}</svg>')


def horizontal(col, bg, ext=None, pad=44):
    ws = 0.5
    text_h = BASE * ws
    ch = text_h * 1.3
    wy = ch / 2 - ((XH_TOP + BASE) / 2) * ws
    k = ch / H0
    cw = (W0 + (L + TH / 2 if ext else 0)) * k
    wx = cw + 30
    Wt = wx + WM_W * ws
    top = min(0, wy); bottom = max(ch, wy + WM_H * ws); H = bottom - top
    extra = ext(col) if ext else ""
    body = (f'<g transform="translate(0,{-top:.2f})"><g transform="scale({k:.4f})"><path d="{S["d"]}" fill="{col}" fill-rule="evenodd"/>{extra}</g>'
            f'<path d="{TA["wordmark"]["d"]}" transform="translate({wx:.2f},{wy:.2f}) scale({ws})" fill="{col}" fill-rule="evenodd"/></g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {Wt+2*pad:.1f} {H+2*pad:.1f}"><rect x="{-pad}" y="{-pad}" width="{Wt+2*pad:.1f}" height="{H+2*pad:.1f}" fill="{bg}"/>{body}</svg>')


if __name__ == "__main__":
    css = """*{box-sizing:border-box;margin:0}body{background:#FAF6F1;color:#2B1A12;font:16px/1.45 'Inter',system-ui,sans-serif;padding:48px;width:1700px}
h1{font-size:40px;letter-spacing:-.02em;margin-bottom:6px}.sub{color:#6B5B52;font-size:19px;margin-bottom:22px;max-width:1300px}
h2{font-size:26px;margin:30px 0 8px}.grid{display:grid;gap:16px}.g3{grid-template-columns:repeat(3,1fr)}.g2{grid-template-columns:1fr 1fr}
.card{background:#fff;border:1px solid #E6DDD3;border-radius:16px;padding:16px}.card svg,.card img{width:100%;display:block}
.card b{display:block;margin-top:8px;font-size:18px}.card span{color:#6B5B52;font-size:15px}.sq{display:grid;place-items:center;height:330px}.sq svg,.sq img{width:auto;max-width:100%;max-height:310px}"""
    D = "/tmp/claude-0/-home-user-Claude/e19f6b0b-622f-5ee1-a4a5-f14c5bc9806b/scratchpad/refs/diniz_symbol.png"
    html = f"""<!doctype html><meta charset="utf-8"><style>{css}</style><body><h1>O P1 está parecido com a Diniz?</h1>
<p class="sub">Comparação lado a lado e duas mudanças que mantêm o P1 como está, mas quebram a semelhança: a haste do óculos sai da moldura.</p>
<div class="grid g3"><div class="card"><div class="sq"><img src="file://{D}"></div><b>Diniz</b><span>Quadrado arredondado, óculos 3/4 na diagonal, traço branco grosso, tudo dentro da moldura.</span></div>
<div class="card"><div class="sq">{symbol(ORANGE)}</div><b>P1 atual</b><span>Mesma construção: container, óculos 3/4 na diagonal, traço branco grosso. Muda a cor, as lentes redondas e a base em onda.</span></div>
<div class="card"><div class="sq">{symbol(ORANGE, ext_straight)}</div><b>P1 com a haste fora da moldura</b><span>A haste atravessa a borda e continua do lado de fora, mudando de cor. A moldura deixa de ser uma caixa fechada.</span></div></div>
<h2>Duas formas de a haste sair</h2><div class="grid g2">
<div class="card"><div class="sq">{symbol(ORANGE, ext_wave)}</div><b>Haste em onda</b><span>A haste termina em um til, a mesma onda do “ã”. É a mudança mais própria da Nova Visão.</span></div>
<div class="card"><div class="sq">{symbol(ORANGE, ext_straight)}</div><b>Haste reta</b><span>Mais discreta. Mantém o símbolo limpo e só tira a semelhança de &ldquo;caixa fechada&rdquo;.</span></div></div>
<h2>Na logo horizontal</h2><div class="grid g2">
<div class="card">{horizontal(ORANGE, WHITE, ext_wave)}</div><div class="card" style="background:#FF5F00;padding:16px">{horizontal(WHITE, ORANGE, ext_wave)}</div>
<div class="card">{horizontal(ORANGE, WHITE, ext_straight)}</div><div class="card" style="background:#FF5F00;padding:16px">{horizontal(WHITE, ORANGE, ext_straight)}</div></div></body>"""
    open(os.path.join(OUT, "p1-vs-diniz.html"), "w").write(html)
    for n, e in (("onda", ext_wave), ("reta", ext_straight)):
        open(os.path.join(SD, f"popular-haste-{n}-horizontal-laranja.svg"), "w").write(horizontal(ORANGE, WHITE, e))
        open(os.path.join(SD, f"popular-haste-{n}-horizontal-branco-sobre-laranja.svg"), "w").write(horizontal(WHITE, ORANGE, e))
        open(os.path.join(SD, f"popular-haste-{n}-simbolo-laranja.svg"), "w").write(symbol(ORANGE, e, pad=14))
        open(os.path.join(SD, f"popular-haste-{n}-simbolo-branco.svg"), "w").write(symbol(WHITE, e, pad=14, bg=ORANGE))
    print("ok")
