import os, sys, math, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen2 import TA, WM_W, WM_H, WM_BASE, ORANGE, WHITE

OUT = "/home/user/Claude/nova-visao-v3"
SVGD = os.path.join(OUT, "svg-perspectiva"); os.makedirs(SVGD, exist_ok=True)

A, R = 1.05, 0.80          # semi-distância entre lentes e raio do aro


def ring(cx, n=160):
    t = np.linspace(0, 2 * math.pi, n, endpoint=False)
    return np.stack([cx + R * np.cos(t), R * np.sin(t), np.zeros(n)], 1)


def bridge(n=40):
    th = math.radians(52)
    p0 = np.array([-A + R * math.cos(th), R * math.sin(th), 0.0])
    p2 = np.array([A - R * math.cos(th), R * math.sin(th), 0.0])
    c = np.array([0.0, R * math.sin(th) + 0.55, 0.0])
    u = np.linspace(0, 1, n)[:, None]
    return (1 - u) ** 2 * p0 + 2 * u * (1 - u) * c + u ** 2 * p2


def temple(sx, L=2.6):
    h = np.array([sx * (A + R * math.cos(math.radians(28))), R * math.sin(math.radians(28)), 0.0])
    pts = [h, h + np.array([0, 0, -L * 0.82]), h + np.array([0, -0.10, -L]), h + np.array([0, -0.45, -L - 0.30])]
    out = []
    for a, b in zip(pts[:-1], pts[1:]):
        for u in np.linspace(0, 1, 14, endpoint=False):
            out.append(a + (b - a) * u)
    out.append(pts[-1])
    return np.array(out)


def project(P, yaw, roll, d=6.0, pitch=0.0):
    y, p, r = map(math.radians, (yaw, pitch, roll))
    x, yy, z = P[:, 0], P[:, 1], P[:, 2]
    x1 = x * math.cos(y) + z * math.sin(y)
    z1 = -x * math.sin(y) + z * math.cos(y)
    y1 = yy * math.cos(p) - z1 * math.sin(p)
    z2 = yy * math.sin(p) + z1 * math.cos(p)
    s = 1.0 / (d - z2)
    X, Y = x1 * s, -y1 * s
    c, sn = math.cos(r), math.sin(r)
    return np.stack([X * c - Y * sn, X * sn + Y * c], 1)


def glasses_paths(yaw, roll, size=760, cx=500, cy=470, sw=62, pitch=0.0):
    L = ring(-A); Rr = ring(A)
    parts = {"lensL": L, "lensR": Rr, "bridge": bridge(), "tL": temple(-1), "tR": temple(1)}
    proj = {k: project(v, yaw, roll, pitch=pitch) for k, v in parts.items()}
    allr = np.vstack([proj["lensL"], proj["lensR"]])
    mn, mx = allr.min(0), allr.max(0)
    k = size / (mx[0] - mn[0])
    mid = (mn + mx) / 2
    def tr(p):
        q = (p - mid) * k
        return q + np.array([cx, cy])
    # ordem de desenho: o que está mais longe primeiro
    zL = (project(np.array([[-A, 0, 0.0]]), yaw, 0)[0])
    d = []
    def poly(p, closed=False):
        q = tr(p)
        s = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in q)
        return s + (" Z" if closed else "")
    out = []
    near = "tL" if yaw > 0 else "tR"
    for name in (near, "lensL", "lensR", "bridge"):
        out.append(poly(proj[name], closed=name.startswith("lens")))
    return out, sw


def container(kind):
    if kind == "wave":
        return ("M120,0 H880 Q1000,0 1000,120 V830 Q1000,900 940,925 C820,975 680,880 520,905 "
                "C360,930 220,985 90,935 Q0,900 0,830 V120 Q0,0 120,0 Z")
    return "M130,0 H870 Q1000,0 1000,130 V870 Q1000,1000 870,1000 H130 Q0,1000 0,870 V130 Q0,0 130,0 Z"


uid = [0]


def symbol(kind, yaw, roll, fill=ORANGE, glass=WHITE, size=800, cx=520, cy=470, sw=64, pitch=0.0):
    uid[0] += 1
    cid = f"c{uid[0]}"
    paths, w = glasses_paths(yaw, roll, size, cx, cy, sw, pitch)
    g = "".join(f'<path d="{p}" fill="none" stroke="{glass}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>' for p in paths)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><defs><clipPath id="{cid}"><path d="{container(kind)}"/></clipPath></defs>'
            f'<path d="{container(kind)}" fill="{fill}"/><g clip-path="url(#{cid})">{g}</g></svg>')


def lockup(kind, yaw, roll, color, bg, glass, pitch=0.0, pad=36):
    ws = 0.5
    ch = WM_BASE * ws * 1.35
    k = ch / 1000
    cw = ch
    wx = cw + 28
    wy = ch - WM_BASE * ws
    inner = symbol(kind, yaw, roll, color, glass, pitch=pitch).replace('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">', f'<svg x="0" y="0" width="{cw:.1f}" height="{ch:.1f}" viewBox="0 0 1000 1000">')
    wm = f'<path d="{TA["wordmark"]["d"]}" transform="translate({wx:.2f},{wy:.2f}) scale({ws})" fill="{color}" fill-rule="evenodd"/>'
    W = wx + WM_W * ws
    H = ch + 4
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {W+2*pad:.1f} {H+2*pad:.1f}"><rect x="{-pad}" y="{-pad}" width="{W+2*pad:.1f}" height="{H+2*pad:.1f}" fill="{bg}"/>{inner}{wm}</svg>')


# 6 combinações: perspectiva x container
SETS = [
    ("A", "Perspectiva suave", 26, -12),
    ("B", "Perspectiva média", 36, -22),
    ("C", "Espelhada", -32, 16),
]
if __name__ == "__main__":
    css = """*{box-sizing:border-box;margin:0}body{background:#FAF6F1;color:#2B1A12;font:16px/1.45 'Inter',system-ui,sans-serif;padding:48px;width:1700px}
h1{font-size:40px;letter-spacing:-.02em;margin-bottom:6px}.sub{color:#6B5B52;font-size:19px;margin-bottom:26px;max-width:1250px}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.card{background:#fff;border:1px solid #E6DDD3;border-radius:18px;padding:18px}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:14px}.pair svg{width:100%;display:block}.card h2{font-size:21px;margin:12px 0 4px}.card p{color:#6B5B52;font-size:15px}
.row{margin-top:10px;border-top:1px solid #EFE7DE;padding-top:10px}.row svg{width:100%;display:block}.on{border-radius:12px;overflow:hidden;margin-top:10px}.on svg{width:100%;display:block}
.sm{display:flex;gap:14px;align-items:flex-end;margin-top:12px}.sm svg{display:block}"""
    cards = ""
    for (k, name, yaw, roll) in SETS:
        sm = "".join(f'<div style="width:{p}px">{symbol("wave", yaw, roll)}</div>' for p in (96, 48, 32, 16))
        cards += (f'<div class="card"><div class="pair">{symbol("plain", yaw, roll)}{symbol("wave", yaw, roll)}</div>'
                  f'<h2>{k} · {name}</h2><p>Giro de {abs(yaw)}° e inclinação de {abs(roll)}°. Container reto e com onda.</p>'
                  f'<div class="row">{lockup("wave", yaw, roll, ORANGE, WHITE, WHITE)}</div>'
                  f'<div class="on">{lockup("wave", yaw, roll, WHITE, ORANGE, ORANGE)}</div><div class="sm">{sm}</div></div>')
    html = (f'<!doctype html><meta charset="utf-8"><style>{css}</style><body><h1>Óculos em perspectiva 3/4, construído em 3D</h1>'
            f'<p class="sub">O óculos foi modelado em 3D, girado e projetado com perspectiva real: a lente próxima é maior, a distante é menor e a haste foge para trás. O traço é uniforme e o símbolo é cortado pela moldura. Cada opção aparece com container reto e com a onda do til.</p><div class="grid">{cards}</div></body>')
    open(os.path.join(OUT, "perspectiva-3d.html"), "w").write(html)
    for (k, name, yaw, roll) in SETS:
        for kind in ("plain", "wave"):
            open(os.path.join(SVGD, f"{k}-{kind}-simbolo-laranja.svg"), "w").write(symbol(kind, yaw, roll))
            open(os.path.join(SVGD, f"{k}-{kind}-simbolo-branco.svg"), "w").write(symbol(kind, yaw, roll, WHITE, ORANGE))
    print("ok")
