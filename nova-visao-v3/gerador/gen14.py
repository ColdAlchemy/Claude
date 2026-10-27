import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen13 as g13
from gen13 import G as ARCHG, BG as ARCH_BG, FG as ARCH_FG, arch_svg, IVORY
from gen2 import TA, WM_W, WM_H, WM_BASE, ORANGE, WHITE, CAFE, COR, COR5

OUT = "/home/user/Claude/nova-visao-v3"
SD = os.path.join(OUT, "sistema"); os.makedirs(SD, exist_ok=True)
SYM = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gpt/popular_traced.json")))
VAR = 3   # variação 4 do P1


def inner(svg):
    return svg.split(">", 1)[1].rsplit("</svg>", 1)[0]


# ------------------------------------------------ POPULAR · P1
def p_sym(color, glass_unused=None):
    s = SYM[VAR]
    return s, f'<path d="{s["d"]}" fill="{color}" fill-rule="evenodd"/>'


def p_horizontal(color, bg, pad=40):
    s, path = p_sym(color)
    ws = 0.5
    ch = WM_BASE * ws * 1.35
    k = ch / s["h"]
    cw = s["w"] * k
    wx = cw + 30
    wy = ch - WM_BASE * ws
    W = wx + WM_W * ws
    H = ch + 4
    body = (f'<g transform="scale({k:.4f})">{path}</g>'
            f'<path d="{TA["wordmark"]["d"]}" transform="translate({wx:.2f},{wy:.2f}) scale({ws})" fill="{color}" fill-rule="evenodd"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {W+2*pad:.1f} {H+2*pad:.1f}"><rect x="{-pad}" y="{-pad}" width="{W+2*pad:.1f}" height="{H+2*pad:.1f}" fill="{bg}"/>{body}</svg>')


def p_stacked(color, bg, pad=50):
    s, path = p_sym(color)
    ws = 0.62
    W = WM_W * ws
    cw = W * 0.40
    k = cw / s["w"]
    ch = s["h"] * k
    top = ch + 34
    ds = 0.62
    dw, dh = TA["descriptor"]["w"] * ds, TA["descriptor"]["h"] * ds
    body = (f'<g transform="translate({W/2 - cw/2:.2f},0) scale({k:.4f})">{path}</g>'
            f'<path d="{TA["wordmark"]["d"]}" transform="translate(0,{top:.2f}) scale({ws})" fill="{color}" fill-rule="evenodd"/>'
            f'<path d="{TA["descriptor"]["d"]}" transform="translate({W/2 - dw/2:.2f},{top + WM_H*ws + 22:.2f}) scale({ds})" fill="{color}" fill-rule="evenodd"/>')
    H = top + WM_H * ws + 22 + dh
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {W+2*pad:.1f} {H+2*pad:.1f}"><rect x="{-pad}" y="{-pad}" width="{W+2*pad:.1f}" height="{H+2*pad:.1f}" fill="{bg}"/>{body}</svg>')


def p_avatar(color, bg=None, pad=14):
    s, path = p_sym(color)
    r = f'<rect x="{-pad}" y="{-pad}" width="{s["w"]+2*pad}" height="{s["h"]+2*pad}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {s["w"]+2*pad} {s["h"]+2*pad}">{r}{path}</svg>'


# ------------------------------------------------ PREMIUM · P4 horizontal
def prem_horizontal(i, text=CAFE, pad=60):
    S = 100
    items, W = COR.shape("NOVA VISÃO", S, 0.14)
    cap = COR.cap * S
    ah = cap * 3.1
    aw = ah * ARCHG[i]["w"] / ARCHG[i]["h"]
    gap = 54
    wx = aw + gap
    its, w5 = COR5.shape("ÓTICA", 25, 0.62)
    desc_off = 62
    block = cap + desc_off + 6
    base = ah / 2 - block / 2 + cap          # centraliza o bloco nome+descritor no arco
    wm = f'<path d="{COR.path(items, S, wx, base)}" fill="{text}"/>'
    d5 = COR5.path(its, 25, wx + W / 2 - w5 / 2, base + desc_off)
    lw = (W - w5) / 2 - 25
    ly = base + desc_off - COR5.cap * 25 * 0.5
    rules = f'<path d="M{wx:.2f},{ly:.2f} H{wx+lw:.2f} M{wx+W-lw:.2f},{ly:.2f} H{wx+W:.2f}" stroke="{text}" stroke-width="1.8"/>'
    sym = arch_svg(i).replace('<svg xmlns="http://www.w3.org/2000/svg" ', f'<svg x="0" y="0" width="{aw:.1f}" height="{ah:.1f}" ')
    TW = wx + W
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {TW+2*pad:.1f} {ah+2*pad:.1f}"><rect x="{-pad}" y="{-pad}" width="{TW+2*pad:.1f}" height="{ah+2*pad:.1f}" fill="{IVORY}"/>'
            f'{sym}{wm}<path d="{d5}" fill="{text}"/>{rules}</svg>')


css = """*{box-sizing:border-box;margin:0}body{background:#FAF6F1;color:#2B1A12;font:16px/1.45 'Inter',system-ui,sans-serif;padding:48px;width:1700px}
h1{font-size:40px;letter-spacing:-.02em;margin-bottom:6px}.sub{color:#6B5B52;font-size:19px;margin-bottom:22px;max-width:1250px}
h2{font-size:28px;margin:34px 0 4px}.hint{color:#6B5B52;margin-bottom:14px}
.card{background:#fff;border:1px solid #E6DDD3;border-radius:16px;padding:14px}.card svg{width:100%;display:block;border-radius:8px}
.card b{display:block;margin:8px 0 2px;font-size:16px}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:16px}.g3{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:16px}
.sm{display:flex;gap:18px;align-items:flex-end;padding:8px}.sm svg{display:block}.dark{background:#FF5F00;border-radius:12px;padding:8px}"""
files = {}
files["popular-horizontal-laranja.svg"] = p_horizontal(ORANGE, WHITE)
files["popular-horizontal-branco-sobre-laranja.svg"] = p_horizontal(WHITE, ORANGE)
files["popular-empilhada-laranja.svg"] = p_stacked(ORANGE, WHITE)
files["popular-empilhada-branco-sobre-laranja.svg"] = p_stacked(WHITE, ORANGE)
files["popular-avatar-laranja.svg"] = p_avatar(ORANGE)
files["popular-avatar-branco-sobre-laranja.svg"] = p_avatar(WHITE, ORANGE)
for i in range(4):
    files[f"premium-horizontal-{i+1}.svg"] = prem_horizontal(i)
    files[f"premium-avatar-{i+1}.svg"] = arch_svg(i)
for n, s in files.items():
    open(os.path.join(SD, n), "w").write(s)

sm_pop = "".join(f'<div style="width:{w}px">{p_avatar(ORANGE)}</div>' for w in (112, 64, 40, 24))
sm_pop_inv = "".join(f'<div style="width:{w}px">{p_avatar(WHITE)}</div>' for w in (112, 64, 40, 24))
sm_pre = "".join(f'<div style="width:{w}px">{arch_svg(1)}</div>' for w in (112, 64, 40, 24))
sm_pre2 = "".join(f'<div style="width:{w}px">{arch_svg(0)}</div>' for w in (112, 64, 40, 24))
LAB = ["Arco laranja · óculos marfim · ângulo 1", "Arco café · óculos laranja · ângulo 1", "Arco laranja · óculos marfim · ângulo 2", "Arco café · óculos laranja · ângulo 2"]
prem_cards = "".join(f'<div class="card">{files[f"premium-horizontal-{i+1}.svg"]}<b>{LAB[i]}</b></div>' for i in range(4))
html = f"""<!doctype html><meta charset="utf-8"><style>{css}</style><body><h1>Sistema · Popular (P1) e Premium (P4)</h1>
<p class="sub">Popular com o símbolo na diagonal do P1 e as suas letras. Premium com o arco do P4, agora com a logo principal na horizontal.</p>
<h2>Popular · P1</h2><p class="hint">Horizontal, empilhada e avatar. Variação 4 do P1, a da onda mais marcada.</p>
<div class="g2"><div class="card">{files["popular-horizontal-laranja.svg"]}<b>Horizontal · principal</b></div><div class="card dark" style="padding:14px;background:#FF5F00">{files["popular-horizontal-branco-sobre-laranja.svg"]}<b style="color:#fff">Horizontal · branco sobre laranja</b></div></div>
<div class="g3"><div class="card">{files["popular-empilhada-laranja.svg"]}<b>Empilhada</b></div><div class="card" style="background:#FF5F00">{files["popular-empilhada-branco-sobre-laranja.svg"]}<b style="color:#fff">Empilhada · branco sobre laranja</b></div><div class="card"><b>Avatar e favicon</b><div class="sm">{sm_pop}</div><div class="sm dark">{sm_pop_inv}</div></div></div>
<h2>Premium · P4 horizontal</h2><p class="hint">O arco à esquerda e o nome à direita, com “ÓTICA” entre fios. As 4 versões do P4.</p>
<div class="g2">{prem_cards}</div>
<div class="g2" style="margin-top:16px"><div class="card"><b>Avatar · arco café</b><div class="sm">{sm_pre}</div></div><div class="card"><b>Avatar · arco laranja</b><div class="sm">{sm_pre2}</div></div></div></body>"""
open(os.path.join(OUT, "sistema.html"), "w").write(html)
print("ok", len(files))
