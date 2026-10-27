"""Nova Visão v2: o logo atual refinado, 4 versões com um detalhe próprio cada.

python3 build2.py  -> ../conceitos/<id>/
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from textpath import shape

OUT = os.path.join(os.path.dirname(__file__), "..", "conceitos")
ORANGE, ESPRESSO, CREAM, WHITE = "#FF6400", "#2B1710", "#FFF4E8", "#FFFFFF"


def f(n):
    return f"{n:.2f}".rstrip("0").rstrip(".")


class Theme:
    def __init__(self, name, container, glint, text, tag, band):
        self.name, self.container, self.glint, self.text, self.tag, self.band = name, container, glint, text, tag, band


LIGHT = Theme("light", ORANGE, WHITE, ORANGE, "#B24A00", "#E35000")
DARK = Theme("dark", ORANGE, WHITE, CREAM, "#FFB27A", "#E35000")
REVERSE = Theme("reverse", WHITE, ORANGE, WHITE, WHITE, "#FFDCC6")

# ---- container: quadrado de cantos pequenos, base em onda (crista à esquerda, vale à direita)
CONTAINER = "M11 0H89Q100 0 100 11V86C100 93 86 97 71 97C54 97 47 85 30 85C16 85 3 88 0 76V11Q0 0 11 0Z"
# onda "eco" desenhada logo abaixo da base
RIPPLE = "M6 93C12 90 20 95 31 95C47 95 54 107 71 107C84 107 92 104 97 99"
# faixa interna mais escura, paralela à base
BAND = "M-2 74C12 77 20 73 30 73C46 73 54 85 71 85C86 85 94 82 102 78V120H-2Z"

# ---- óculos (antes da rotação): lente esquerda maior, direita menor, haste longa
L = (22, 52, 17.5)
R = (60, 52, 14.8)
SW = 5.2


def glasses_knock(sw=SW):
    bx1 = L[0] + L[2] * math.cos(math.radians(-42)); by1 = L[1] + L[2] * math.sin(math.radians(-42))
    bx2 = R[0] + R[2] * math.cos(math.radians(-138)); by2 = R[1] + R[2] * math.sin(math.radians(-138))
    return (
        f'<g fill="none" stroke="#000" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" '
        f'transform="translate(0 -4) rotate(-13 40 52)">'
        f'<circle cx="{L[0]}" cy="{L[1]}" r="{L[2]}"/><circle cx="{R[0]}" cy="{R[1]}" r="{R[2]}"/>'
        f'<path d="M{f(bx1)} {f(by1)}Q{f((bx1 + bx2) / 2)} {f(min(by1, by2) - 5)} {f(bx2)} {f(by2)}"/>'
        f'<path d="M{R[0] + R[2]} {R[1] - 1}L124 {R[1] - 3}"/></g>'
    )


def glint_arcs(color):
    def arc(c, r):
        a0, a1 = math.radians(205), math.radians(250)
        x0, y0, x1, y1 = c[0] + r * math.cos(a0), c[1] + r * math.sin(a0), c[0] + r * math.cos(a1), c[1] + r * math.sin(a1)
        return f'<path d="M{f(x0)} {f(y0)}A{r} {r} 0 0 1 {f(x1)} {f(y1)}"/>'
    return (
        f'<g fill="none" stroke="{color}" stroke-width="2.1" stroke-linecap="round" '
        f'transform="translate(0 -4) rotate(-13 40 52)">{arc(L, 11)}{arc(R, 8.8)}</g>'
    )


def mark(variant, t):
    """Devolve (w, h, defs, body). variant: base | brilho | onda | tom"""
    h = 110 if variant == "onda" else 100
    kn = glasses_knock()
    defs = (
        f'<mask id="k" maskUnits="userSpaceOnUse" x="-20" y="-30" width="160" height="160">'
        f'<rect x="-20" y="-30" width="160" height="160" fill="#fff"/>{kn}</mask>'
    )
    inner = f'<path d="{CONTAINER}" fill="{t.container}"/>'
    if variant == "tom":
        defs += f'<clipPath id="cc"><path d="{CONTAINER}"/></clipPath>'
        inner += f'<g clip-path="url(#cc)"><path d="{BAND}" fill="{t.band}"/></g>'
    body = f'<g mask="url(#k)">{inner}</g>'
    if variant == "brilho":
        body += glint_arcs(t.glint)
    if variant == "onda":
        body += f'<path d="{RIPPLE}" fill="none" stroke="{t.container}" stroke-width="4.2" stroke-linecap="round"/>'
    return 100, h, defs, body


# ---- wordmark
FONT = dict(font="Outfit", weight=720, tracking=-0.005)


def tilde(cx, y, width, sw, amp, color):
    """Til em onda limpa: duas parábolas espelhadas, y é a linha central."""
    x0, x1 = cx - width / 2, cx + width / 2
    return (f'<path d="M{f(x0)} {f(y)}Q{f(x0 + width / 4)} {f(y - 2 * amp)} {f(cx)} {f(y)}T{f(x1)} {f(y)}" '
            f'fill="none" stroke="{color}" stroke-width="{f(sw)}" stroke-linecap="round"/>')


def wordmark(variant, xh_target, t, x, base, uid="w"):
    probe = shape("nova visao", FONT["font"], 100, FONT["weight"])
    size = 100 * xh_target / probe.xheight
    run = shape("nova visao", FONT["font"], size, FONT["weight"], FONT["tracking"], x=x, y=base)
    xh = run.xheight
    d = run.d
    defs = ""
    attr = ""
    if variant == "brilho":
        # brilho nas duas letras "o": mesmo arco que aparece nas lentes
        arcs = ""
        for gi in (1, 9):
            g = run.glyphs[gi]
            cx, cy = g.x + g.adv / 2, base - xh / 2
            r = xh * 0.365
            a0, a1 = math.radians(205), math.radians(252)
            arcs += (f'<path d="M{f(cx + r * math.cos(a0))} {f(cy + r * math.sin(a0))}A{f(r)} {f(r)} 0 0 1 '
                     f'{f(cx + r * math.cos(a1))} {f(cy + r * math.sin(a1))}"/>')
        defs = (f'<mask id="{uid}" maskUnits="userSpaceOnUse" x="{f(x - 10)}" y="{f(base - xh * 2)}" '
                f'width="{f(run.width + 20)}" height="{f(xh * 3)}"><rect x="{f(x - 10)}" y="{f(base - xh * 2)}" '
                f'width="{f(run.width + 20)}" height="{f(xh * 3)}" fill="#fff"/>'
                f'<g fill="none" stroke="#000" stroke-width="{f(xh * 0.085)}" stroke-linecap="round">{arcs}</g></mask>')
        attr = f' mask="url(#{uid})"'
    parts = f'<path d="{d}" fill="{t.text}"{attr}/>'
    a = run.glyphs[8]
    parts += tilde(a.x + a.adv / 2, base - xh - 0.30 * xh, 0.56 * xh, 0.17 * xh, 0.085 * xh, t.text)
    return defs, parts, run.width


def svg_doc(w, h, defs, body, title="Nova Visão ótica"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {f(w)} {f(h)}" role="img" aria-label="{title}">'
            f'<title>{title}</title><defs>{defs}</defs>{body}</svg>\n')


def horizontal(variant, t, pad=6):
    mw, mh, md, mb = mark(variant, t)
    mhs = 72
    s = mhs / 100
    xh = 36
    gap = 20
    base = pad + mhs / 2 + xh / 2 + 2
    wd, wb, ww = wordmark(variant, xh, t, pad + mw * s + gap, base)
    W, H = pad * 2 + mw * s + gap + ww, pad * 2 + mh * s
    return svg_doc(W, H, md + wd, f'<g transform="translate({pad} {pad}) scale({f(s)})">{mb}</g>{wb}')


def stacked(variant, t, pad=10):
    mw, mh, md, mb = mark(variant, t)
    s = 1.05
    xh = 31
    _, _, ww = wordmark(variant, xh, t, 0, 0)
    W = pad * 2 + max(mw * s, ww)
    base = pad + mh * s + 18 + xh
    wd, wb, ww = wordmark(variant, xh, t, (W - ww) / 2, base)
    tag = shape("ÓTICA", "Outfit", 14.5, 500, 0.55)
    tag = shape("ÓTICA", "Outfit", 14.5, 500, 0.55, x=(W - tag.width) / 2, y=base + 33)
    body = (f'<g transform="translate({f((W - mw * s) / 2)} {pad}) scale({f(s)})">{mb}</g>{wb}'
            f'<path d="{tag.d}" fill="{t.tag}"/>')
    return svg_doc(W, base + 33 + pad, md + wd, body)


def icon(variant, size=128):
    mw, mh, md, mb = mark(variant, REVERSE)
    s = size * 0.62 / 100
    ox, oy = (size - mw * s) / 2, (size - 100 * s) / 2
    bg = f'<rect width="{size}" height="{size}" rx="{size * 0.22}" fill="{ORANGE}"/>'
    return svg_doc(size, size, md, bg + f'<g transform="translate({f(ox)} {f(oy)}) scale({f(s)})">{mb}</g>')


VARIANTS = [
    ("A-fiel-refinada", "Fiel, refinada",
     "O logo atual com a geometria limpa: lentes e haste redesenhadas, onda com ritmo, letras mais compactas e um til em onda que repete a base do ícone."),
    ("B-brilho", "Brilho",
     "Igual à A, com um pequeno reflexo nas lentes que se repete nos dois 'o' do nome. Um detalhe que só esta marca tem."),
    ("C-onda-eco", "Onda eco",
     "Igual à A, com uma segunda onda fina logo abaixo do ícone, como o reflexo na água. A onda ganha presença sem mudar o símbolo."),
    ("D-tom-sobre-tom", "Tom sobre tom",
     "Igual à A, com uma faixa de laranja mais escuro seguindo a onda da base. Mais profundidade e acabamento, ainda com uma cor só."),
]
KEY = {"A-fiel-refinada": "base", "B-brilho": "brilho", "C-onda-eco": "onda", "D-tom-sobre-tom": "tom"}


def build():
    for vid, _, _ in VARIANTS:
        d = os.path.join(OUT, vid)
        os.makedirs(d, exist_ok=True)
        v = KEY[vid]
        for t, suf in ((LIGHT, ""), (DARK, "-fundo-escuro"), (REVERSE, "-branco")):
            open(os.path.join(d, f"horizontal{suf}.svg"), "w").write(horizontal(v, t))
        open(os.path.join(d, "vertical.svg"), "w").write(stacked(v, LIGHT))
        open(os.path.join(d, "vertical-fundo-escuro.svg"), "w").write(stacked(v, DARK))
        open(os.path.join(d, "icone.svg"), "w").write(icon(v))
    print("ok")


if __name__ == "__main__":
    build()
