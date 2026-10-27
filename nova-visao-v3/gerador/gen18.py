import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
import potrace
from gen2 import TA, WM_W, WM_H, ORANGE, WHITE

OUT = "/home/user/Claude/nova-visao-v3"
SD = os.path.join(OUT, "sistema"); os.makedirs(SD, exist_ok=True)
im = Image.open('/root/.claude/uploads/e19f6b0b-622f-5ee1-a4a5-f14c5bc9806b/38d71c23-image.png').convert('RGB')
a = np.array(im).astype(int)
orange = (a[:, :, 0] > 200) & (a[:, :, 1] < 160) & (a[:, :, 2] < 90)
x0, x1, y1 = 1571, 1996, 553
box = (x0 - 4, 154, x1 + 5, y1 + 5)
m = orange[box[1]:box[3], box[0]:box[2]]
h, w = m.shape
pad = 60
mp = np.pad(m, pad, constant_values=False)
st = np.ones((1, 1), bool)
yy, xx = np.ogrid[-45:46, -45:46]
disk = (xx * xx + yy * yy) <= 45 * 45
hull = ndimage.binary_closing(mp, structure=disk)[pad:-pad, pad:-pad] | m
hull = ndimage.binary_fill_holes(hull)
glasses = hull & ~m
SHIFT = 60
H = h + SHIFT


def canvas(src):
    c = np.zeros((H, w), bool)
    c[SHIFT:SHIFT + h] = src
    return c


ext = canvas(hull)
cols = np.where(hull.any(0))[0]
top_r = int(np.where(hull.any(1))[0].min())
ext[:SHIFT + top_r + 70, cols.min():cols.max() + 1] = True
# prolonga o topo do contêiner original para cima, para o recorte novo definir o formato
glass_s = canvas(glasses)


def cut_corner(M, r, corner):
    Y, X = np.mgrid[0:H, 0:w]
    if corner == "tl":
        bad = (X < r) & (Y < r) & ((X - r) ** 2 + (Y - r) ** 2 > r * r)
    else:
        bad = (X >= w - r) & (Y < r) & ((X - (w - r)) ** 2 + (Y - r) ** 2 > r * r)
    M = M.copy(); M[bad] = False
    return M


def container(kind):
    M = ext.copy()
    if kind == "arco":
        r = w // 2
        M = cut_corner(cut_corner(M, r, "tl"), r, "tr")
    elif kind == "folha":
        M = cut_corner(M, 230, "tl"); M = cut_corner(M, 40, "tr")
    else:  # "suave"
        M = cut_corner(cut_corner(M, 150, "tl"), 150, "tr")
    return M


def trace_mask(mask, up=3):
    img = Image.fromarray((mask * 255).astype('uint8'), 'L')
    img = img.resize((img.width * up, img.height * up), Image.LANCZOS).filter(ImageFilter.GaussianBlur(up * 0.6))
    arr = np.array(img) > 128
    pl = potrace.Bitmap(~arr).trace(turdsize=60, turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY, alphamax=1.2, opticurve=True, opttolerance=0.5)
    s = 1.0 / up
    f = lambda p: f"{p.x*s:.2f},{p.y*s:.2f}"
    d = []
    for c in pl:
        d.append("M" + f(c.start_point))
        for seg in c.segments:
            d.append(("L" + f(seg.c) + " L" + f(seg.end_point)) if seg.is_corner else ("C" + f(seg.c1) + " " + f(seg.c2) + " " + f(seg.end_point)))
        d.append("Z")
    return " ".join(d)


KINDS = [("arco", "Arco com onda", "Topo de janela e base em onda. É o formato que mais se afasta do quadrado da Diniz."),
         ("folha", "Folha", "Um canto de cima bem arredondado e o outro quase reto. Dá movimento."),
         ("suave", "Arco suave", "Dois cantos de cima bem redondos, sem chegar ao arco inteiro.")]
SYMS = {}
for k, n, d in KINDS:
    SYMS[k] = dict(d=trace_mask(container(k) & ~glass_s), w=w, h=H)
ORIG = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gpt/popular_traced.json")))[3]


def sym_svg(sd, col, bg=None, pad=14):
    r = f'<rect x="{-pad}" y="{-pad}" width="{sd["w"]+2*pad}" height="{sd["h"]+2*pad}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {sd["w"]+2*pad} {sd["h"]+2*pad}">{r}<path d="{sd["d"]}" fill="{col}" fill-rule="evenodd"/></svg>'


def horizontal(sd, col, bg, pad=44):
    ws = 0.5
    text_h = 158 * ws
    ch = text_h * 1.3
    k = ch / sd["h"]
    cw = sd["w"] * k
    wy = ch / 2 - ((52.0 + 158.0) / 2) * ws
    wx = cw + 30
    Wt = wx + WM_W * ws
    top = min(0, wy); bottom = max(ch, wy + WM_H * ws); Hh = bottom - top
    body = (f'<g transform="translate(0,{-top:.2f})"><g transform="scale({k:.4f})"><path d="{sd["d"]}" fill="{col}" fill-rule="evenodd"/></g>'
            f'<path d="{TA["wordmark"]["d"]}" transform="translate({wx:.2f},{wy:.2f}) scale({ws})" fill="{col}" fill-rule="evenodd"/></g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {Wt+2*pad:.1f} {Hh+2*pad:.1f}"><rect x="{-pad}" y="{-pad}" width="{Wt+2*pad:.1f}" height="{Hh+2*pad:.1f}" fill="{bg}"/>{body}</svg>')


css = """*{box-sizing:border-box;margin:0}body{background:#FAF6F1;color:#2B1A12;font:16px/1.45 'Inter',system-ui,sans-serif;padding:48px;width:1700px}
h1{font-size:40px;letter-spacing:-.02em;margin-bottom:6px}.sub{color:#6B5B52;font-size:19px;margin-bottom:22px;max-width:1300px}
.grid{display:grid;gap:16px;grid-template-columns:repeat(4,1fr)}.card{background:#fff;border:1px solid #E6DDD3;border-radius:16px;padding:16px}
.card svg,.card img{display:block;margin:0 auto}.sq{display:grid;place-items:center;height:300px}.sq svg,.sq img{max-width:100%;max-height:280px;width:auto}
.card b{display:block;margin-top:8px;font-size:18px}.card span{color:#6B5B52;font-size:14.5px}.row{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px}.row svg{width:100%}"""
D = "/tmp/claude-0/-home-user-Claude/e19f6b0b-622f-5ee1-a4a5-f14c5bc9806b/scratchpad/refs/diniz_symbol.png"
cards = f'<div class="card"><div class="sq"><img src="file://{D}"></div><b>Diniz</b><span>Quadrado arredondado.</span></div>'
cards += f'<div class="card"><div class="sq">{sym_svg(ORIG, ORANGE)}</div><b>P1 atual</b><span>Quadrado arredondado com base em onda.</span></div>'
rows = ""
for k, n, d in KINDS:
    open(os.path.join(SD, f"popular-container-{k}-simbolo-laranja.svg"), "w").write(sym_svg(SYMS[k], ORANGE))
    open(os.path.join(SD, f"popular-container-{k}-horizontal-laranja.svg"), "w").write(horizontal(SYMS[k], ORANGE, WHITE))
    open(os.path.join(SD, f"popular-container-{k}-horizontal-branco-sobre-laranja.svg"), "w").write(horizontal(SYMS[k], WHITE, ORANGE))
grid2 = ""
for k, n, d in KINDS:
    grid2 += f'<div class="card"><div class="sq">{sym_svg(SYMS[k], ORANGE)}</div><b>{n}</b><span>{d}</span></div>'
rows = "".join(f'<div class="row"><div class="card">{horizontal(SYMS[k], ORANGE, WHITE)}</div><div class="card" style="background:#FF5F00">{horizontal(SYMS[k], WHITE, ORANGE)}</div></div>' for k, n, d in KINDS)
html = (f'<!doctype html><meta charset="utf-8"><style>{css}</style><body><h1>P1 · mesmo óculos, container diferente</h1>'
        f'<p class="sub">O óculos é exatamente o mesmo do P1. Só mudei o formato do container, que é o elemento mais reconhecível da Diniz.</p>'
        f'<div class="grid">{cards}{grid2[:0]}</div><div class="grid" style="margin-top:16px;grid-template-columns:repeat(3,1fr)">{grid2}</div>{rows}</body>')
open(os.path.join(OUT, "p1-containers.html"), "w").write(html)
print("ok")
