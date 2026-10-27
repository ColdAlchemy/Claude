"""Nova Visão v3: réplica fiel do logo atual + variações mínimas (1 ou 2 detalhes).

Medidas tiradas da imagem original (container 100 de largura).
python3 build3.py -> ../conceitos/<id>/
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from textpath import shape

OUT = os.path.join(os.path.dirname(__file__), "..", "conceitos")
ORANGE, ESPRESSO, CREAM, WHITE = "#FF6400", "#2B1710", "#FFF4E8", "#FFFFFF"


def f(n):
    return f"{n:.2f}".rstrip("0").rstrip(".")


class Theme:
    def __init__(self, name, container, text, accent, tag, glint):
        self.name, self.container, self.text, self.accent, self.tag, self.glint = name, container, text, accent, tag, glint


# ---------------------------------------------------------------- símbolo
CONTAINER = ("M11.5 0H88.5Q100 0 100 11.5V77Q100 86 92 89C84 92.5 78 93 72 93C56 93 44 84 30 80.5"
             "C20 78 12 84.5 6 84.5Q0 84.5 0 77V11.5Q0 0 11.5 0Z")
H = 93  # altura do símbolo

# lentes (linha central do aro = furo + metade do aro), medidas no original
RIGHT = dict(cx=59.7, cy=38.0, rx=18.7, ry=21.5, rot=-6)
LEFT = dict(cx=16.9, cy=55.3, rx=15.2, ry=19.2, rot=-9)
RING = 4.1


def knock():
    def ell(e):
        return (f'<ellipse cx="{e["cx"]}" cy="{e["cy"]}" rx="{e["rx"]}" ry="{e["ry"]}" '
                f'transform="rotate({e["rot"]} {e["cx"]} {e["cy"]})"/>')
    return (f'<g fill="none" stroke="#000" stroke-width="{RING}" stroke-linecap="round">{ell(LEFT)}{ell(RIGHT)}'
            f'<path d="M30.1 45.7Q36 40.3 41.6 43.6" stroke-width="4.4"/></g>'
            f'<path d="M77 23.2L106 31.4" stroke="#000" stroke-width="7" stroke-linecap="round" fill="none"/>')


def glint(color):
    def arc(e):
        rx, ry = e["rx"] - 5.2, e["ry"] - 5.2
        a0, a1 = math.radians(205), math.radians(250)
        p = lambda a: (e["cx"] + rx * math.cos(a), e["cy"] + ry * math.sin(a))
        (x0, y0), (x1, y1) = p(a0), p(a1)
        return (f'<path d="M{f(x0)} {f(y0)}A{f(rx)} {f(ry)} 0 0 1 {f(x1)} {f(y1)}" '
                f'transform="rotate({e["rot"]} {e["cx"]} {e["cy"]})"/>')
    return (f'<g fill="none" stroke="{color}" stroke-width="2.2" stroke-linecap="round">{arc(LEFT)}{arc(RIGHT)}</g>')


def mark(variant, t):
    defs = (f'<mask id="k" maskUnits="userSpaceOnUse" x="-20" y="-20" width="150" height="140">'
            f'<rect x="-20" y="-20" width="150" height="140" fill="#fff"/>{knock()}</mask>')
    body = f'<g mask="url(#k)"><path d="{CONTAINER}" fill="{t.container}"/></g>'
    if variant == "brilho":
        body += glint(t.glint)
    return 100, H, defs, body


# ---------------------------------------------------------------- wordmark
def tilde(cx, y, width, sw, amp, color):
    x0, x1 = cx - width / 2, cx + width / 2
    return (f'<path d="M{f(x0)} {f(y)}Q{f(x0 + width / 4)} {f(y - 2 * amp)} {f(cx)} {f(y)}T{f(x1)} {f(y)}" '
            f'fill="none" stroke="{color}" stroke-width="{f(sw)}" stroke-linecap="round"/>')


SPEC = {
    "base": dict(font="Outfit", weight=790, tracking=-0.008, til="fonte", soft=0.04),
    "suave": dict(font="Fredoka", weight=700, tracking=-0.01, til="fonte"),
    "tom": dict(font="Outfit", weight=790, tracking=-0.008, til="custom", soft=0.04),
    "brilho": dict(font="Outfit", weight=790, tracking=-0.008, til="fonte", soft=0.04),
}


def wordmark(variant, xh_target, t, x, base):
    sp = SPEC[variant]
    custom = sp["til"] == "custom"
    txt = "nova visao" if custom else "nova visão"
    probe = shape(txt, sp["font"], 100, sp["weight"])
    size = 100 * xh_target / probe.xheight
    run = shape(txt, sp["font"], size, sp["weight"], sp["tracking"], x=x, y=base)
    soft = sp.get("soft", 0)
    stroke = f' stroke="{t.text}" stroke-width="{f(soft * size)}" stroke-linejoin="round"' if soft else ""
    parts = f'<path d="{run.d}" fill="{t.text}"{stroke}/>'
    if custom:
        a = run.glyphs[8]
        xh = run.xheight
        parts += tilde(a.x + a.adv / 2, base - xh - 0.30 * xh, 0.6 * xh, 0.2 * xh, 0.1 * xh, t.accent)
    return "", parts, run.width


def svg_doc(w, h, defs, body, title="Nova Visão ótica"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {f(w)} {f(h)}" role="img" aria-label="{title}">'
            f'<title>{title}</title><defs>{defs}</defs>{body}</svg>\n')


def horizontal(variant, t, pad=6, mhs=70):
    mw, mh, md, mb = mark(variant, t)
    s = mhs / H
    xh = 0.49 * mhs
    base = pad + 0.745 * mhs
    gap = 0.34 * mhs
    wd, wb, ww = wordmark(variant, xh, t, pad + mw * s + gap, base)
    W, Ht = pad * 2 + mw * s + gap + ww, pad * 2 + mhs
    return svg_doc(W, Ht, md + wd, f'<g transform="translate({pad} {pad}) scale({f(s)})">{mb}</g>{wb}')


def stacked(variant, t, pad=10):
    mw, mh, md, mb = mark(variant, t)
    s = 100 / H
    xh = 31
    _, _, ww = wordmark(variant, xh, t, 0, 0)
    W = pad * 2 + max(100, ww)
    base = pad + 100 + 18 + xh
    wd, wb, ww = wordmark(variant, xh, t, (W - ww) / 2, base)
    tag = shape("ÓTICA", "Outfit", 14, 500, 0.6)
    tag = shape("ÓTICA", "Outfit", 14, 500, 0.6, x=(W - tag.width) / 2, y=base + 32)
    body = (f'<g transform="translate({f((W - mw * s) / 2)} {pad}) scale({f(s)})">{mb}</g>{wb}'
            f'<path d="{tag.d}" fill="{t.tag}"/>')
    return svg_doc(W, base + 32 + pad, md + wd, body)


def icon(variant, size=128):
    t = REVERSE
    mw, mh, md, mb = mark(variant, t)
    s = size * 0.60 / 100
    ox, oy = (size - mw * s) / 2, (size - H * s) / 2
    bg = f'<rect width="{size}" height="{size}" rx="{size * 0.22}" fill="{ORANGE}"/>'
    return svg_doc(size, size, md, bg + f'<g transform="translate({f(ox)} {f(oy)}) scale({f(s)})">{mb}</g>')


LIGHT = Theme("light", ORANGE, ORANGE, ORANGE, "#B24A00", WHITE)
DARK = Theme("dark", ORANGE, CREAM, ORANGE, "#FFB27A", WHITE)
REVERSE = Theme("reverse", WHITE, WHITE, WHITE, WHITE, ORANGE)
# variante "tom": texto em marrom-café, só o til fica laranja
TOM_LIGHT = Theme("light", ORANGE, ESPRESSO, ORANGE, "#8A6B5A", WHITE)

VARIANTS = [
    ("A-original-refinada", "base", "Original refinada",
     "O logo atual redesenhado com precisão, com as medidas tiradas da sua imagem: mesmas lentes ovais, mesma haste, mesma onda. Só a geometria ficou limpa."),
    ("B-letra-arredondada", "suave", "Letra arredondada",
     "Único ajuste: letras de cantos arredondados (Fredoka), um pouco mais macias que a A. O símbolo não muda."),
    ("C-nome-em-cafe", "tom", "Nome em café",
     "Único ajuste: o nome em marrom-café e só o til em laranja. O símbolo e as letras não mudam."),
    ("D-brilho-nas-lentes", "brilho", "Brilho nas lentes",
     "Único ajuste: um pequeno reflexo dentro das duas lentes. O resto é idêntico ao original."),
]


def build():
    for vid, v, _, _ in VARIANTS:
        d = os.path.join(OUT, vid)
        os.makedirs(d, exist_ok=True)
        tl = TOM_LIGHT if v == "tom" else LIGHT
        open(os.path.join(d, "horizontal.svg"), "w").write(horizontal(v, tl))
        open(os.path.join(d, "horizontal-fundo-escuro.svg"), "w").write(horizontal(v, DARK))
        open(os.path.join(d, "horizontal-branco.svg"), "w").write(horizontal(v, REVERSE))
        open(os.path.join(d, "vertical.svg"), "w").write(stacked(v, tl))
        open(os.path.join(d, "vertical-fundo-escuro.svg"), "w").write(stacked(v, DARK))
        open(os.path.join(d, "icone.svg"), "w").write(icon(v))
    print("ok")


if __name__ == "__main__":
    build()
