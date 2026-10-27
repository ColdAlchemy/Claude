import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import potrace
from gen2 import COR, COR5, ORANGE, CAFE

OUT = "/home/user/Claude/nova-visao-v3"
IVORY = "#FBF6EC"
SRC = '/root/.claude/uploads/e19f6b0b-622f-5ee1-a4a5-f14c5bc9806b/c01f08c7-image.png'
im = Image.open(SRC).convert('RGB')
A = np.array(im).astype(int)
BOXES = [(263, 45, 583, 313), (954, 45, 1277, 313), (263, 533, 583, 802), (954, 533, 1277, 802)]
FG = [IVORY, ORANGE, IVORY, ORANGE]
BG = [ORANGE, CAFE, ORANGE, CAFE]


def trace_mask(mask, up=4):
    img = Image.fromarray((mask * 255).astype('uint8'), 'L')
    img = img.resize((img.width * up, img.height * up), Image.LANCZOS).filter(ImageFilter.GaussianBlur(up * 0.6))
    arr = np.array(img) > 128
    pl = potrace.Bitmap(~arr).trace(turdsize=40, turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY, alphamax=1.2, opticurve=True, opttolerance=0.5)
    s = 1.0 / up
    f = lambda p: f"{p.x*s:.2f},{p.y*s:.2f}"
    d = []
    for c in pl:
        d.append("M" + f(c.start_point))
        for seg in c.segments:
            d.append(("L" + f(seg.c) + " L" + f(seg.end_point)) if seg.is_corner else ("C" + f(seg.c1) + " " + f(seg.c2) + " " + f(seg.end_point)))
        d.append("Z")
    return " ".join(d)


G = []
for (x0, y0, x1, y1) in BOXES:
    w, h = x1 - x0, y1 - y0
    crop = A[y0:y1, x0:x1]
    arch = Image.new('L', (w, h), 0)
    dr = ImageDraw.Draw(arch)
    r = w / 2
    dr.rectangle([0, r, w, h], fill=255)
    dr.ellipse([0, 0, w, w], fill=255)
    inarch = np.array(arch) > 128
    ys, xs = np.where(inarch)
    base = np.median(crop[inarch].reshape(-1, 3), axis=0)
    dist = np.abs(crop - base).sum(2)
    ing = ndimage_mask = (dist > 70) & inarch
    # erode borda do arco para não pegar a transição com o fundo
    from scipy import ndimage
    inner = ndimage.binary_erosion(inarch, iterations=4)
    glass = ing & inner
    glass = ndimage.binary_opening(glass, iterations=1)
    G.append(dict(w=w, h=h, d=trace_mask(glass)))


def arch_svg(i):
    g = G[i]
    w, h = g['w'], g['h']
    r = w / 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"><path d="M0,{h} V{r} A{r},{r} 0 0 1 {w},{r} V{h} Z" fill="{BG[i]}"/>'
            f'<path d="{g["d"]}" fill="{FG[i]}" fill-rule="evenodd"/></svg>')


def lockup(i):
    S = 100
    items, W = COR.shape("NOVA VISÃO", S, 0.14)
    aw = W * 0.46
    ah = aw * G[i]['h'] / G[i]['w']
    sym = arch_svg(i).replace('<svg xmlns="http://www.w3.org/2000/svg" ', f'<svg x="{W/2 - aw/2:.1f}" y="0" width="{aw:.1f}" height="{ah:.1f}" ')
    base = ah + 40 + COR.cap * S
    wm = f'<path d="{COR.path(items, S, 0, base)}" fill="{CAFE}"/>'
    its, w5 = COR5.shape("ÓTICA", 27, 0.62)
    d5 = COR5.path(its, 27, W / 2 - w5 / 2, base + 74)
    lw = (W - w5) / 2 - 27
    ly = base + 74 - COR5.cap * 27 * 0.5
    rules = f'<path d="M0,{ly:.2f} H{lw:.2f} M{W-lw:.2f},{ly:.2f} H{W:.2f}" stroke="{CAFE}" stroke-width="1.8"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-60 -40 {W+120:.1f} {base+130:.1f}"><rect x="-60" y="-40" width="{W+120:.1f}" height="{base+130:.1f}" fill="{IVORY}"/>'
            f'{sym}{wm}<path d="{d5}" fill="{CAFE}"/>{rules}</svg>')


css = """*{box-sizing:border-box;margin:0}body{background:#FAF6F1;color:#2B1A12;font:16px/1.45 'Inter',system-ui,sans-serif;padding:48px;width:1700px}
h1{font-size:40px;letter-spacing:-.02em;margin-bottom:6px}.sub{color:#6B5B52;font-size:19px;margin-bottom:26px;max-width:1250px}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}.card{background:#fff;border:1px solid #E6DDD3;border-radius:18px;padding:14px}.card svg{width:100%;display:block}
.sm{display:flex;gap:18px;align-items:flex-end;margin-top:12px;padding:6px}.sm svg{display:block}"""
cards = ""
os.makedirs(os.path.join(OUT, "svg-p4-gpt"), exist_ok=True)
for i in range(4):
    L = lockup(i)
    open(os.path.join(OUT, "svg-p4-gpt", f"p4gpt-{i+1}.svg"), "w").write(L)
    sm = "".join(f'<div style="width:{w}px">{arch_svg(i)}</div>' for w in (96, 56, 32, 20))
    cards += f'<div class="card">{L}<div class="sm">{sm}</div></div>'
open(os.path.join(OUT, "p4-gpt-vetor.html"), "w").write(f'<!doctype html><meta charset="utf-8"><style>{css}</style><body><h1>P4 · o óculos do ChatGPT, vetorizado</h1><p class="sub">Arco refeito limpo, óculos do ChatGPT vetorizado a partir da imagem, e a serifa Cormorant no lugar das letras.</p><div class="grid">{cards}</div></body>')
print("ok")
