import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
import gen18
from gen18 import m, glasses, trace_mask, ORIG
from gen2 import TA, WM_W, WM_H, ORANGE, WHITE

OUT = "/home/user/Claude/nova-visao-v3"
SD = os.path.join(OUT, "sistema"); os.makedirs(SD, exist_ok=True)
h, w = m.shape
P = 80
G = np.zeros((h + 2 * P, w + 2 * P), bool)
G[P:P + h, P:P + w] = glasses

# --- completa a lente da esquerda (cortada pela borda do contêiner)
lab, n = ndimage.label(m)
sizes = ndimage.sum(m, lab, range(1, n + 1))
cands = []
for i in range(1, n + 1):
    s = sizes[i - 1]
    if 2000 < s < 40000:
        ys, xs = np.where(lab == i)
        cands.append((xs.mean(), ys.mean(), i, s))
cands.sort()
cx0, cy0, idx, _ = cands[0]            # lente interna mais à esquerda
comp = lab == idx
edge = comp & ~ndimage.binary_erosion(comp)
ys, xs = np.where(edge)
x = xs.astype(float); y = ys.astype(float)
A = np.stack([x * x, x * y, y * y, x, y], 1)
coef = np.linalg.lstsq(A, np.ones(len(x)), rcond=None)[0]
a_, b_, c_, d_, e_ = coef
M = np.array([[a_, b_ / 2], [b_ / 2, c_]])
ctr = np.linalg.solve(2 * M, -np.array([d_, e_]))
val = 1 + ctr @ M @ ctr
ev, evec = np.linalg.eigh(M / val)
axes = 1 / np.sqrt(ev)                  # semieixos
# espessura do aro: do bordo direito da lente interna até o contêiner laranja
row = int(round(ctr[1]))
col = int(xs[ys == row].max()) if (ys == row).any() else int(ctr[0] + axes.max())
t = 0
while not m[row, min(col + 1 + t, w - 1)] and t < 60:
    t += 1
# usa a espessura da lente da direita (mais confiável, sem o apoio de nariz)
cx1, cy1, idx1, _ = cands[1]
comp1 = lab == idx1
ys1, xs1 = np.where(comp1)
xc = int(round(xs1.mean())); ytop = int(ys1[xs1 == xc].min())
t1 = 0
while not m[max(ytop - 1 - t1, 0), xc] and t1 < 60:
    t1 += 1
t = max(14, min(t, t1 + 2))
print('t_dir', t1, 't', t)
print("elipse", ctr, axes, "espessura", t)


def ellipse_poly(c, ax, evec, grow, n=360):
    th = np.linspace(0, 2 * math.pi, n, endpoint=False)
    pts = []
    for q in th:
        v = evec @ np.array([(ax[0] + grow) * math.cos(q), (ax[1] + grow) * math.sin(q)])
        pts.append((float(c[0] + v[0] + P), float(c[1] + v[1] + P)))
    return pts


img = Image.new('L', (G.shape[1], G.shape[0]), 0)
dr = ImageDraw.Draw(img)
dr.polygon(ellipse_poly(ctr, axes, evec, t), fill=255)
dr.polygon(ellipse_poly(ctr, axes, evec, 0), fill=0)
ring = np.array(img) > 128
G = G | ring
# o miolo da lente da esquerda continua vazio
inner = Image.new('L', (G.shape[1], G.shape[0]), 0)
ImageDraw.Draw(inner).polygon(ellipse_poly(ctr, axes, evec, -1), fill=255)
G = G & ~(np.array(inner) > 128)

# ponta da haste arredondada na borda direita
EXr, EYr, TH = w - 1 - 4, 131.5, 25.0
im2 = Image.fromarray((G * 255).astype('uint8'), 'L')
ImageDraw.Draw(im2).ellipse([EXr + P - TH / 2 + 3, EYr + P - TH / 2 + 2, EXr + P + TH / 2 + 3, EYr + P + TH / 2 + 2], fill=255)
G = np.array(im2) > 128
G = ndimage.binary_opening(G, iterations=1)

d = trace_mask(G)
SY = dict(d=d, w=G.shape[1], h=G.shape[0])
# recorta a caixa útil
ys2, xs2 = np.where(G)
bx0, bx1, by0, by1 = xs2.min() - 6, xs2.max() + 6, ys2.min() - 6, ys2.max() + 6
SY["vb"] = (bx0, by0, bx1 - bx0, by1 - by0)


def sym(col, bg=None, pad=10):
    x0, y0, ww, hh = SY["vb"]
    r = f'<rect x="{x0-pad}" y="{y0-pad}" width="{ww+2*pad}" height="{hh+2*pad}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0-pad} {y0-pad} {ww+2*pad} {hh+2*pad}">{r}<path d="{SY["d"]}" fill="{col}" fill-rule="evenodd"/></svg>'


def horizontal(col, bg, pad=44):
    x0, y0, ww, hh = SY["vb"]
    ws = 0.56
    text_h = 158 * ws
    ch = text_h * 1.15
    k = ch / hh
    cw = ww * k
    wy = ch / 2 - ((52.0 + 158.0) / 2) * ws
    wx = cw + 30
    Wt = wx + WM_W * ws
    top = min(0, wy); bottom = max(ch, wy + WM_H * ws); H = bottom - top
    body = (f'<g transform="translate(0,{-top:.2f})"><g transform="scale({k:.4f}) translate({-x0},{-y0})"><path d="{SY["d"]}" fill="{col}" fill-rule="evenodd"/></g>'
            f'<path d="{TA["wordmark"]["d"]}" transform="translate({wx:.2f},{wy:.2f}) scale({ws})" fill="{col}" fill-rule="evenodd"/></g>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {Wt+2*pad:.1f} {H+2*pad:.1f}"><rect x="{-pad}" y="{-pad}" width="{Wt+2*pad:.1f}" height="{H+2*pad:.1f}" fill="{bg}"/>{body}</svg>'


def stacked(col, bg, pad=50):
    x0, y0, ww, hh = SY["vb"]
    ws = 0.62
    W = WM_W * ws
    cw = W * 0.46
    k = cw / ww
    ch = hh * k
    top = ch + 28
    ds = 0.62
    dw, dh = TA["descriptor"]["w"] * ds, TA["descriptor"]["h"] * ds
    body = (f'<g transform="translate({W/2 - cw/2:.2f},0) scale({k:.4f}) translate({-x0},{-y0})"><path d="{SY["d"]}" fill="{col}" fill-rule="evenodd"/></g>'
            f'<path d="{TA["wordmark"]["d"]}" transform="translate(0,{top:.2f}) scale({ws})" fill="{col}" fill-rule="evenodd"/>'
            f'<path d="{TA["descriptor"]["d"]}" transform="translate({W/2 - dw/2:.2f},{top + WM_H*ws + 20:.2f}) scale({ds})" fill="{col}" fill-rule="evenodd"/>')
    H = top + WM_H * ws + 20 + dh
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {W+2*pad:.1f} {H+2*pad:.1f}"><rect x="{-pad}" y="{-pad}" width="{W+2*pad:.1f}" height="{H+2*pad:.1f}" fill="{bg}"/>{body}</svg>'


files = {"p1-sem-container-simbolo-laranja.svg": sym(ORANGE), "p1-sem-container-simbolo-branco-sobre-laranja.svg": sym(WHITE, ORANGE),
         "p1-sem-container-horizontal-laranja.svg": horizontal(ORANGE, WHITE), "p1-sem-container-horizontal-branco-sobre-laranja.svg": horizontal(WHITE, ORANGE),
         "p1-sem-container-empilhada-laranja.svg": stacked(ORANGE, WHITE), "p1-sem-container-empilhada-branco-sobre-laranja.svg": stacked(WHITE, ORANGE)}
for n_, s in files.items():
    open(os.path.join(SD, n_), "w").write(s)

css = """*{box-sizing:border-box;margin:0}body{background:#FAF6F1;color:#2B1A12;font:16px/1.45 'Inter',system-ui,sans-serif;padding:48px;width:1700px}
h1{font-size:40px;letter-spacing:-.02em;margin-bottom:6px}.sub{color:#6B5B52;font-size:19px;margin-bottom:22px;max-width:1300px}
.grid{display:grid;gap:14px}.g2{grid-template-columns:1fr 1fr}.g3{grid-template-columns:1.2fr 1.2fr 1fr}.card{background:#fff;border:1px solid #E6DDD3;border-radius:14px;padding:14px;display:grid;place-items:center}
.card svg{width:100%;display:block;border-radius:6px}.dk{background:#FF5F00}.sq{height:340px}.sq svg{height:100%;width:auto;max-width:100%}
.sm{display:flex;gap:14px;align-items:flex-end}.sm svg{display:block}.card b{display:block;margin-top:8px}"""
cmp_ = f'<div class="card"><div class="sq">{gen18.sym_svg(ORIG, ORANGE)}</div><b>Com container (original)</b></div>'
sm = "".join(f'<div style="width:{wv}px">{sym(ORANGE)}</div>' for wv in (140, 80, 52, 32))
smi = "".join(f'<div style="width:{wv}px">{sym(WHITE)}</div>' for wv in (140, 80, 52, 32))
html = (f'<!doctype html><meta charset="utf-8"><style>{css}</style><body><h1>P1 · sem o container</h1>'
        f'<p class="sub">O mesmo óculos, sozinho. Completei a lente da esquerda, que era cortada pela borda do container, e arredondei a ponta da haste.</p>'
        f'<div class="grid g2">{cmp_}<div class="card"><div class="sq">{sym(ORANGE)}</div><b>Sem container</b></div></div>'
        f'<div class="grid g2" style="margin-top:14px"><div class="card">{horizontal(ORANGE, WHITE)}</div><div class="card dk">{horizontal(WHITE, ORANGE)}</div></div>'
        f'<div class="grid g3" style="margin-top:14px"><div class="card">{stacked(ORANGE, WHITE)}</div><div class="card dk">{stacked(WHITE, ORANGE)}</div>'
        f'<div class="card"><div><div class="sm">{sm}</div><div class="sm dk" style="margin-top:10px;border-radius:8px;padding:8px;background:#FF5F00">{smi}</div></div></div></div></body>')
open(os.path.join(OUT, "p1-sem-container.html"), "w").write(html)
print("ok")
