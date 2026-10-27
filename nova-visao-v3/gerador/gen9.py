import os, sys, re, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen2 import TA, ORANGE, WHITE, rrect

OUT = "/home/user/Claude/nova-visao-v3"
SVGD = os.path.join(OUT, "svg-p2-explorar"); os.makedirs(SVGD, exist_ok=True)

# ---- separa "nova" e "visão" da tipografia original
WM = TA["wordmark"]["d"]
subs = [s for s in re.split(r"(?=M)", WM) if s.strip()]
nums = lambda s: np.array([float(x) for x in re.findall(r"-?\d+\.?\d*", s)]).reshape(-1, 2)
boxes = [(nums(s)[:, 0].min(), nums(s)[:, 0].max()) for s in subs]
iv = sorted(boxes)
merged = [list(iv[0])]
for x0, x1 in iv[1:]:
    if x0 <= merged[-1][1] + 1:
        merged[-1][1] = max(merged[-1][1], x1)
    else:
        merged.append([x0, x1])
gap_x = max(((merged[i + 1][0] - merged[i][1], (merged[i][1] + merged[i + 1][0]) / 2) for i in range(len(merged) - 1)))[1]
LEFT = [s for s, b in zip(subs, boxes) if (b[0] + b[1]) / 2 < gap_x]
RIGHT = [s for s, b in zip(subs, boxes) if (b[0] + b[1]) / 2 >= gap_x]
bb = lambda g: (lambda P: (P[:, 0].min(), P[:, 0].max()))(np.vstack([nums(s) for s in g]))
BL, BR = bb(LEFT), bb(RIGHT)
XH_MID = (52.0 + 158.0) / 2   # centro do x-height no recorte vetorizado


def word(group, b, cx, cy, tw):
    k = tw / (b[1] - b[0])
    return (f'<path d="{" ".join(group)}" transform="translate({cx:.2f},{cy:.2f}) scale({k:.4f}) translate({-(b[0]+b[1])/2:.2f},{-XH_MID:.2f})" fill-rule="evenodd"/>')


def wave(x0, y0, w, amp):
    f = lambda v: f"{v:.2f}"
    return (f"M{f(x0)},{f(y0)} C{f(x0+w*.17)},{f(y0-amp*1.33)} {f(x0+w*.33)},{f(y0-amp*1.33)} {f(x0+w*.5)},{f(y0)} "
            f"S{f(x0+w*.83)},{f(y0+amp*1.33)} {f(x0+w)},{f(y0)}")


def arch(x0, x1, y, rise):
    return f"M{x0},{y} C{x0+(x1-x0)*.2},{y-rise*1.33} {x1-(x1-x0)*.2},{y-rise*1.33} {x1},{y}"


def logo(p, body, text, bg=None, pad=34):
    w, h, g = p["w"], p["h"], p["g"]
    t = p["t"]
    x0 = 30
    y0 = 20
    xl0, xl1 = x0, x0 + w
    xr0, xr1 = xl1 + g, xl1 + g + w
    yb = y0 + p["by"] * h
    parts = []
    rt, rb = p["rt"] * h, p["rb"] * h
    lens = rrect(xl0, y0, xl1, y0 + h, rt, rt * p["inner"], rb * p["inner"], rb) + " " + rrect(xr0, y0, xr1, y0 + h, rt * p["inner"], rt, rb, rb * p["inner"])
    parts.append(f'<path d="{lens}" fill="{body}"/>')
    # ponte
    if p["bridge"] == "wave":
        parts.append(f'<path d="{wave(xl1 - 16, yb, g + 32, p["amp"])}" fill="none" stroke="{body}" stroke-width="{t}" stroke-linecap="round" stroke-linejoin="round"/>')
    elif p["bridge"] == "arch":
        parts.append(f'<path d="{arch(xl1 - 12, xr0 + 12, yb + 8, p["amp"])}" fill="none" stroke="{body}" stroke-width="{t}" stroke-linecap="round"/>')
    else:
        parts.append(f'<rect x="{xl1-10}" y="{yb-t/2}" width="{g+20}" height="{t}" fill="{body}"/>')
    # hastes
    sh = p["stub"]
    parts.append(f'<rect x="{xl0-sh}" y="{yb-9}" width="{sh+10}" height="20" rx="9" fill="{body}"/>')
    parts.append(f'<rect x="{xr1-10}" y="{yb-9}" width="{sh+10}" height="20" rx="9" fill="{body}"/>')
    # texto
    cy = y0 + h * p["ty"]
    tw = w * p["tw"]
    txt = word(LEFT, BL, (xl0 + xl1) / 2 - 2, cy, tw) + word(RIGHT, BR, (xr0 + xr1) / 2 + 2, cy, tw)
    W = xr1 + sh - xl0 + 2 * 0
    H = h
    vb = (xl0 - sh - pad, y0 - 24 - pad + 8, xr1 + sh - xl0 + 2 * pad + 4, h + 40 + 2 * pad - 14)
    r = f'<rect x="{vb[0]}" y="{vb[1]}" width="{vb[2]}" height="{vb[3]}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb[0]:.1f} {vb[1]:.1f} {vb[2]:.1f} {vb[3]:.1f}">{r}'
            f'{"".join(parts)}<g fill="{text}">{txt}</g></svg>')


BASE = dict(w=230, h=150, g=26, t=20, rt=0.36, rb=0.42, inner=1.0, by=0.22, amp=7, bridge="wave", stub=24, tw=0.80, ty=0.58)
VARIANTS = [
    ("1 · Base limpa", "As lentes quadradas arredondadas da variação 1, com a ponte em onda e o recorte do nariz reto, sem a seta.", dict()),
    ("2 · Nome maior", "Lentes mais baixas e o nome ocupando quase toda a largura da lente. Sem laranja vazio.", dict(h=128, tw=0.93, ty=0.55, rt=0.40, rb=0.44)),
    ("3 · Ponte em arco aberta", "A ponte vira um arco e o espaço entre as lentes abre. O nariz fica um “U” limpo.", dict(g=40, bridge="arch", amp=16, t=18, tw=0.86, h=140, ty=0.58)),
    ("4 · Lente mais quadrada", "Proporção mais alta e cantos firmes, com letras grandes. Lê como um óculos de armação grossa.", dict(h=165, w=215, rt=0.26, rb=0.30, tw=0.88, ty=0.56)),
    ("5 · Travesseiro", "Cantos bem redondos e mais macios, com o fundo mais cheio. É a versão mais simpática.", dict(h=148, rt=0.50, rb=0.50, tw=0.86, ty=0.56)),
    ("7 · Combinação", "O melhor de cada: cantos macios do 5, ponte em arco aberta do 3 e nome grande, mas com respiro, do 2.", dict(h=142, rt=0.46, rb=0.48, g=38, bridge="arch", amp=16, t=18, tw=0.87, ty=0.57)),
    ("6 · Til forte", "A onda da ponte é mais alta e grossa, igual ao til do “ã”. A ponte vira assinatura.", dict(amp=13, t=24, g=34, tw=0.86, by=0.2, h=138, ty=0.57)),
]
if __name__ == "__main__":
    css = """*{box-sizing:border-box;margin:0}body{background:#FAF6F1;color:#2B1A12;font:16px/1.45 'Inter',system-ui,sans-serif;padding:48px;width:1700px}
h1{font-size:40px;letter-spacing:-.02em;margin-bottom:6px}.sub{color:#6B5B52;font-size:19px;margin-bottom:26px;max-width:1250px}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}.card{background:#fff;border:1px solid #E6DDD3;border-radius:18px;padding:18px}
.card svg{width:100%;display:block}.card h2{font-size:21px;margin:6px 0 2px}.card p{color:#6B5B52;font-size:15px;margin-bottom:8px}.on{border-radius:12px;overflow:hidden;margin-top:8px}.sm{display:flex;gap:18px;align-items:center;margin-top:10px}.sm svg{display:block}"""
    cards = ""
    for i, (name, desc, ch) in enumerate(VARIANTS, 1):
        p = dict(BASE); p.update(ch)
        o = logo(p, ORANGE, WHITE)
        inv = logo(p, WHITE, ORANGE, bg=ORANGE)
        open(os.path.join(SVGD, f"v{i}-laranja.svg"), "w").write(o)
        open(os.path.join(SVGD, f"v{i}-branco-sobre-laranja.svg"), "w").write(inv)
        sm = "".join(f'<div style="width:{w}px">{logo(p, ORANGE, WHITE, pad=6)}</div>' for w in (200, 120, 72))
        cards += f'<div class="card"><h2>{name}</h2><p>{desc}</p>{o}<div class="on">{inv}</div><div class="sm">{sm}</div></div>'
    html = (f'<!doctype html><meta charset="utf-8"><style>{css}</style><body><h1>P2 · explorando as mudanças</h1>'
            f'<p class="sub">Silhueta reconstruída em vetor, para variar o recorte do nariz, a proporção das lentes e o tamanho do nome. As letras são as suas, de verdade.</p><div class="grid">{cards}</div></body>')
    open(os.path.join(OUT, "p2-explorar.html"), "w").write(html)
    print("ok")
