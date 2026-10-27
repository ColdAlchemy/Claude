import os, sys, re, json
import numpy as np
import potrace
from PIL import Image, ImageFilter
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen2 import TA, ORANGE, WHITE

OUT = "/home/user/Claude/nova-visao-v3"
SVGD = os.path.join(OUT, "svg-p2"); os.makedirs(SVGD, exist_ok=True)
SRC = '/root/.claude/uploads/e19f6b0b-622f-5ee1-a4a5-f14c5bc9806b/10e2172e-image.png'
im = Image.open(SRC).convert('RGB')
a = np.array(im).astype(int)
orange = (a[:, :, 0] > 200) & (a[:, :, 1] < 160) & (a[:, :, 2] < 90)
lab, n = ndimage.label(orange)
comps = []
for i in range(1, n + 1):
    ys, xs = np.where(lab == i)
    if len(ys) > 50000:
        comps.append((i, xs.min(), xs.max(), ys.min(), ys.max()))
# ordem: topo-esquerda, topo-direita, base-esquerda, base-direita
comps.sort(key=lambda c: (round(c[3] / 300), c[1]))


def trace_mask(mask, up=3, alpha=1.15):
    img = Image.fromarray((mask * 255).astype('uint8'), 'L')
    img = img.resize((img.width * up, img.height * up), Image.LANCZOS).filter(ImageFilter.GaussianBlur(up * 0.5))
    arr = np.array(img) > 128
    pl = potrace.Bitmap(~arr).trace(turdsize=60, turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY, alphamax=alpha, opticurve=True, opttolerance=0.4)
    s = 1.0 / up
    f = lambda p: f"{p.x*s:.2f},{p.y*s:.2f}"
    d = []
    for c in pl:
        d.append("M" + f(c.start_point))
        for seg in c.segments:
            d.append(("L" + f(seg.c) + " L" + f(seg.end_point)) if seg.is_corner else ("C" + f(seg.c1) + " " + f(seg.c2) + " " + f(seg.end_point)))
        d.append("Z")
    return " ".join(d)


# ---- separa "nova" e "visão" da sua tipografia
WM = TA["wordmark"]["d"]
subs = [s for s in re.split(r"(?=M)", WM) if s.strip()]


def nums(sub):
    v = [float(x) for x in re.findall(r"-?\d+\.?\d*", sub)]
    return np.array(v).reshape(-1, 2)


boxes = []
for s in subs:
    p = nums(s)
    boxes.append((p[:, 0].min(), p[:, 0].max(), p[:, 1].min(), p[:, 1].max()))
iv = sorted((b[0], b[1]) for b in boxes)
merged = [list(iv[0])]
for x0, x1 in iv[1:]:
    if x0 <= merged[-1][1] + 1:
        merged[-1][1] = max(merged[-1][1], x1)
    else:
        merged.append([x0, x1])
gaps = [(merged[i + 1][0] - merged[i][1], (merged[i][1] + merged[i + 1][0]) / 2) for i in range(len(merged) - 1)]
gap_x = max(gaps)[1]
left = [s for s, b in zip(subs, boxes) if (b[0] + b[1]) / 2 < gap_x]
right = [s for s, b in zip(subs, boxes) if (b[0] + b[1]) / 2 >= gap_x]


def group_bbox(group):
    P = np.vstack([nums(s) for s in group])
    return P[:, 0].min(), P[:, 0].max(), P[:, 1].min(), P[:, 1].max()


GL, GR = group_bbox(left), group_bbox(right)
XH_TOP, BASE = 52.0, 158.0   # topo do x-height e linha de base do recorte vetorizado


def place(group, bb, tcx, tcy, target_w):
    k = target_w / (bb[1] - bb[0])
    cx = (bb[0] + bb[1]) / 2
    cy = (XH_TOP + BASE) / 2
    return f'<path d="{" ".join(group)}" transform="translate({tcx:.2f},{tcy:.2f}) scale({k:.4f}) translate({-cx:.2f},{-cy:.2f})" fill-rule="evenodd"/>'


VARS = []
for idx, (i, x0, x1, y0, y1) in enumerate(comps):
    pad = 8
    X0, X1, Y0, Y1 = x0 - pad, x1 + pad, y0 - pad, y1 + pad
    m = (lab == i)
    filled = ndimage.binary_fill_holes(m)
    letters = filled & ~m
    # centros dos dois grupos de letras
    ys, xs = np.where(letters)
    lab2, n2 = ndimage.label(ndimage.binary_dilation(letters, iterations=14))
    gx = sorted([(np.where(lab2 == j)[1].mean(), j) for j in range(1, n2 + 1)])
    # agrupa em esquerda/direita pelo ponto médio da silhueta
    mid = np.where(filled[(y0 + y1) // 2 + 60, x0:x1 + 1] == 0)[0]
    notch = x0 + (mid.mean() if len(mid) else (x1 - x0) / 2)
    Lm = letters & (np.arange(letters.shape[1])[None, :] < notch)
    Rm = letters & (np.arange(letters.shape[1])[None, :] >= notch)
    def bb(mm):
        yy, xx = np.where(mm)
        return xx.min(), xx.max(), yy.min(), yy.max()
    bl, br = bb(Lm), bb(Rm)
    d = trace_mask(filled[Y0:Y1, X0:X1])
    W, H = X1 - X0, Y1 - Y0
    tw = 0.96 * min(bl[1] - bl[0], br[1] - br[0])
    cyl = ((bl[2] + bl[3]) / 2 - Y0)
    cyr = ((br[2] + br[3]) / 2 - Y0)
    cyl = cyr = (cyl + cyr) / 2
    ltxt = place(left, GL, (bl[0] + bl[1]) / 2 - X0, cyl, tw)
    rtxt = place(right, GR, (br[0] + br[1]) / 2 - X0, cyr, tw)
    VARS.append(dict(d=d, W=W, H=H, l=ltxt, r=rtxt))


def logo_svg(v, body, text, bg=None, pad=30):
    r = f'<rect x="{-pad}" y="{-pad}" width="{v["W"]+2*pad}" height="{v["H"]+2*pad}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {v["W"]+2*pad} {v["H"]+2*pad}">{r}'
            f'<path d="{v["d"]}" fill="{body}" fill-rule="evenodd"/><g fill="{text}">{v["l"]}{v["r"]}</g></svg>')


for k, v in enumerate(VARS, 1):
    open(os.path.join(SVGD, f"p2-var{k}-laranja.svg"), "w").write(logo_svg(v, ORANGE, WHITE))
    open(os.path.join(SVGD, f"p2-var{k}-branco-sobre-laranja.svg"), "w").write(logo_svg(v, WHITE, ORANGE, bg=ORANGE))

css = """*{box-sizing:border-box;margin:0}body{background:#FAF6F1;color:#2B1A12;font:16px/1.45 'Inter',system-ui,sans-serif;padding:48px;width:1700px}
h1{font-size:40px;letter-spacing:-.02em;margin-bottom:6px}.sub{color:#6B5B52;font-size:19px;margin-bottom:26px;max-width:1250px}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}.card{background:#fff;border:1px solid #E6DDD3;border-radius:18px;padding:18px}
.card svg{width:100%;display:block}.card h2{font-size:21px;margin:8px 0}.on{border-radius:12px;overflow:hidden;margin-top:10px}.sm{display:flex;gap:18px;align-items:center;margin-top:12px}.sm svg{display:block}"""
cards = ""
for k, v in enumerate(VARS, 1):
    sm = "".join(f'<div style="width:{p}px">{logo_svg(v, ORANGE, WHITE, pad=4)}</div>' for p in (220, 140, 90))
    cards += (f'<div class="card"><h2>Variação {k}</h2>{logo_svg(v, ORANGE, WHITE)}<div class="on">{logo_svg(v, WHITE, ORANGE, bg=ORANGE)}</div><div class="sm">{sm}</div></div>')
html = (f'<!doctype html><meta charset="utf-8"><style>{css}</style><body><h1>P2 · a silhueta do óculos é a logo</h1>'
        f'<p class="sub">As 4 silhuetas do ChatGPT, vetorizadas, com as letras trocadas pela sua tipografia de verdade. Cada uma aparece em laranja, em branco sobre laranja e em tamanhos menores.</p><div class="grid">{cards}</div></body>')
open(os.path.join(OUT, "p2-silhuetas.html"), "w").write(html)
print("ok", len(VARS), [(v["W"], v["H"]) for v in VARS], "gap", gap_x)
