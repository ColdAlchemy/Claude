import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen18
from gen18 import SYMS, ORIG
from gen2 import TA, WM_W, WM_H, ORANGE, WHITE

OUT = "/home/user/Claude/nova-visao-v3"
SD = os.path.join(OUT, "sistema"); os.makedirs(SD, exist_ok=True)
ALL = [("original", "Quadrado com onda · original", ORIG)] + [(k, n, SYMS[k]) for k, n, d in gen18.KINDS]
WM = TA["wordmark"]["d"]; DS = TA["descriptor"]["d"]


def avatar(sd, col, bg=None, pad=12):
    r = f'<rect x="{-pad}" y="{-pad}" width="{sd["w"]+2*pad}" height="{sd["h"]+2*pad}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {sd["w"]+2*pad} {sd["h"]+2*pad}">{r}<path d="{sd["d"]}" fill="{col}" fill-rule="evenodd"/></svg>'


def horizontal(sd, col, bg, pad=44):
    """Alinhamento D: texto maior, centro da altura-x no centro do símbolo."""
    ws = 0.56
    text_h = 158 * ws
    ch = text_h * 1.28
    k = ch / sd["h"]
    cw = sd["w"] * k
    wy = ch / 2 - ((52.0 + 158.0) / 2) * ws
    wx = cw + 30
    Wt = wx + WM_W * ws
    top = min(0, wy); bottom = max(ch, wy + WM_H * ws); H = bottom - top
    body = (f'<g transform="translate(0,{-top:.2f})"><g transform="scale({k:.4f})"><path d="{sd["d"]}" fill="{col}" fill-rule="evenodd"/></g>'
            f'<path d="{WM}" transform="translate({wx:.2f},{wy:.2f}) scale({ws})" fill="{col}" fill-rule="evenodd"/></g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {Wt+2*pad:.1f} {H+2*pad:.1f}"><rect x="{-pad}" y="{-pad}" width="{Wt+2*pad:.1f}" height="{H+2*pad:.1f}" fill="{bg}"/>{body}</svg>')


def stacked(sd, col, bg, pad=50):
    ws = 0.62
    W = WM_W * ws
    cw = W * 0.36
    k = cw / sd["w"]
    ch = sd["h"] * k
    top = ch + 30
    ds = 0.62
    dw, dh = TA["descriptor"]["w"] * ds, TA["descriptor"]["h"] * ds
    body = (f'<g transform="translate({W/2 - cw/2:.2f},0) scale({k:.4f})"><path d="{sd["d"]}" fill="{col}" fill-rule="evenodd"/></g>'
            f'<path d="{WM}" transform="translate(0,{top:.2f}) scale({ws})" fill="{col}" fill-rule="evenodd"/>'
            f'<path d="{DS}" transform="translate({W/2 - dw/2:.2f},{top + WM_H*ws + 20:.2f}) scale({ds})" fill="{col}" fill-rule="evenodd"/>')
    H = top + WM_H * ws + 20 + dh
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {W+2*pad:.1f} {H+2*pad:.1f}"><rect x="{-pad}" y="{-pad}" width="{W+2*pad:.1f}" height="{H+2*pad:.1f}" fill="{bg}"/>{body}</svg>')


css = """*{box-sizing:border-box;margin:0}body{background:#FAF6F1;color:#2B1A12;font:16px/1.45 'Inter',system-ui,sans-serif;padding:48px;width:1700px}
h1{font-size:40px;letter-spacing:-.02em;margin-bottom:6px}.sub{color:#6B5B52;font-size:19px;margin-bottom:22px;max-width:1300px}
.sec{margin-top:26px}.sec h2{font-size:26px;margin-bottom:10px}
.grid{display:grid;grid-template-columns:1.5fr 1.5fr 1fr 1fr;gap:12px;align-items:stretch}.card{background:#fff;border:1px solid #E6DDD3;border-radius:14px;padding:10px;display:grid;place-items:center}
.card svg{width:100%;display:block;border-radius:6px}.dk{background:#FF5F00}.sm{display:flex;gap:12px;align-items:flex-end;flex-wrap:wrap}.sm svg{display:block}
.mini{display:flex;flex-direction:column;gap:8px;align-items:flex-start;width:100%}"""
secs = ""
for k, n, sd in ALL:
    open(os.path.join(SD, f"p1-{k}-D-horizontal-laranja.svg"), "w").write(horizontal(sd, ORANGE, WHITE))
    open(os.path.join(SD, f"p1-{k}-D-horizontal-branco-sobre-laranja.svg"), "w").write(horizontal(sd, WHITE, ORANGE))
    open(os.path.join(SD, f"p1-{k}-D-empilhada-laranja.svg"), "w").write(stacked(sd, ORANGE, WHITE))
    open(os.path.join(SD, f"p1-{k}-D-empilhada-branco-sobre-laranja.svg"), "w").write(stacked(sd, WHITE, ORANGE))
    open(os.path.join(SD, f"p1-{k}-avatar-laranja.svg"), "w").write(avatar(sd, ORANGE))
    open(os.path.join(SD, f"p1-{k}-avatar-branco-sobre-laranja.svg"), "w").write(avatar(sd, WHITE, ORANGE))
    sm = "".join(f'<div style="width:{w}px">{avatar(sd, ORANGE)}</div>' for w in (84, 52, 34, 22))
    sm2 = "".join(f'<div style="width:{w}px">{avatar(sd, WHITE)}</div>' for w in (84, 52, 34, 22))
    secs += (f'<div class="sec"><h2>{n}</h2><div class="grid"><div class="card">{horizontal(sd, ORANGE, WHITE)}</div><div class="card dk">{horizontal(sd, WHITE, ORANGE)}</div>'
             f'<div class="card">{stacked(sd, ORANGE, WHITE)}</div><div class="card"><div class="mini"><div class="sm">{sm}</div><div class="sm" style="background:#FF5F00;border-radius:8px;padding:8px">{sm2}</div></div></div></div></div>')
html = (f'<!doctype html><meta charset="utf-8"><style>{css}</style><body><h1>P1 · alinhamento D em 4 containers</h1>'
        f'<p class="sub">O mesmo óculos e as mesmas letras, com o texto maior e centrado no símbolo. Só muda o container: o original, o arco com onda, a folha e o arco suave. Cada um aparece na horizontal, em branco sobre laranja, empilhado e como avatar.</p>{secs}</body>')
open(os.path.join(OUT, "p1-D-containers.html"), "w").write(html)
print("ok")
