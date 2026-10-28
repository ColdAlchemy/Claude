"""Nova Visão: variações da versão A (original refinada).

Cada variação muda 1 ou 2 detalhes pequenos; símbolo e letra base vêm de build3.
python3 build4.py -> ../variacoes-A/<id>/
"""
import math, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from textpath import shape
from build3 import RIGHT, LEFT, RING, knock, glint, tilde, svg_doc, f

OUT = os.path.join(os.path.dirname(__file__), "..", "variacoes-A")
ORANGE, ESPRESSO, CREAM, WHITE, AMBER = "#FF6400", "#2B1710", "#FFF4E8", "#FFFFFF", "#FFA800"

# ---------------------------------------------------------------- temas
THEMES = {
    "light": dict(container=ORANGE, orange=ORANGE, espresso=ESPRESSO, amber=AMBER, tag="#B24A00",
                  band="#E35000", lens="#FF7E2E", glint=WHITE),
    "dark": dict(container=ORANGE, orange=CREAM, espresso=CREAM, amber=AMBER, tag="#FFB27A",
                 band="#E35000", lens="#FF7E2E", glint=WHITE),
    "reverse": dict(container=WHITE, orange=WHITE, espresso=WHITE, amber=WHITE, tag=WHITE,
                    band="#FFDCC6", lens="#FFE6D6", glint=ORANGE),
}


def pick(th, key):
    """'orange' como cor de acento só vale no tema claro/escuro (o til continua laranja no escuro)."""
    return th[key]


# ---------------------------------------------------------------- símbolo
def container_path(r):
    return (f"M{r} 0H{100 - r}Q100 0 100 {r}V77Q100 86 92 89C84 92.5 78 93 72 93C56 93 44 84 30 80.5"
            f"C20 78 12 84.5 6 84.5Q0 84.5 0 77V{r}Q0 0 {r} 0Z")


BAND = ("M104 66V70Q100 75 92 78C84 81.5 78 82 72 82C56 82 44 73 30 69.5C20 67 12 73.5 6 73.5Q0 73.5 -4 70V110H104Z")
RIPPLE = "M5 95C14 95 20 91 30 91.5C44 92 56 104 72 104C82 104 90 102 96 98"


def mark(spec, th):
    h = 106 if spec.get("ripple") else 93
    defs = (f'<mask id="k" maskUnits="userSpaceOnUse" x="-20" y="-20" width="150" height="150">'
            f'<rect x="-20" y="-20" width="150" height="150" fill="#fff"/>{knock()}</mask>')
    cp = container_path(spec.get("radius", 11.5))
    inner = f'<path d="{cp}" fill="{th["container"]}"/>'
    if spec.get("band"):
        defs += f'<clipPath id="cc"><path d="{cp}"/></clipPath>'
        inner += f'<g clip-path="url(#cc)"><path d="{BAND}" fill="{th["band"]}"/></g>'
    body = f'<g mask="url(#k)">{inner}</g>'
    if spec.get("lens"):
        for e in (LEFT, RIGHT):
            body += (f'<ellipse cx="{e["cx"]}" cy="{e["cy"]}" rx="{f(e["rx"] - RING / 2 + 0.1)}" '
                     f'ry="{f(e["ry"] - RING / 2 + 0.1)}" transform="rotate({e["rot"]} {e["cx"]} {e["cy"]})" '
                     f'fill="{th["lens"]}"/>')
    if spec.get("glint"):
        body += glint(th["glint"])
    if spec.get("ripple"):
        body += f'<path d="{RIPPLE}" fill="none" stroke="{th["container"]}" stroke-width="4.2" stroke-linecap="round"/>'
    return 100, h, defs, body


# ---------------------------------------------------------------- wordmark
def split_dot(d):
    """Separa o pingo do 'i' (subpath mais alto) do resto do glifo."""
    subs = ["M" + s for s in d.split("M") if s]
    def top(s):
        nums = [float(n) for n in re.findall(r"-?\d+\.?\d*", s)]
        return min(nums[1::2])
    subs.sort(key=top)
    return subs[0], "".join(subs[1:])


def wordmark(spec, xh_target, th, x, base):
    font, weight, tr = spec.get("font", "Outfit"), spec.get("weight", 775), spec.get("tracking", 0.034)
    soft = spec.get("soft", 0.035)
    til_custom = spec.get("til") == "custom"
    txt = "nova visao" if til_custom else "nova visão"
    probe = shape(txt, font, 100, weight)
    size = 100 * xh_target / probe.xheight
    run = shape(txt, font, size, weight, tr, x=x, y=base)
    xh = run.xheight
    text_c = th[spec.get("text", "orange")]
    acc_c = th[spec.get("accent", "orange")]
    st = lambda c: f' stroke="{c}" stroke-width="{f(soft * size)}" stroke-linejoin="round"' if soft else ""
    if spec.get("dot"):
        dot, rest = split_dot(run.glyphs[6].d)
        body = "".join(g.d for i, g in enumerate(run.glyphs) if i != 6) + rest
        parts = f'<path d="{body}" fill="{text_c}"{st(text_c)}/><path d="{dot}" fill="{acc_c}"{st(acc_c)}/>'
    else:
        parts = f'<path d="{run.d}" fill="{text_c}"{st(text_c)}/>'
    if til_custom:
        a = run.glyphs[8]
        parts += tilde(a.x + a.adv / 2, base - xh - 0.30 * xh, 0.6 * xh, 0.2 * xh, 0.1 * xh, acc_c)
    return parts, run.width


# ---------------------------------------------------------------- composições
def horizontal(spec, th, pad=6, mhs=70):
    mw, mh, md, mb = mark(spec, th)
    s = mhs / 93
    xh = 0.49 * mhs
    base = pad + 0.745 * mhs
    gap = 0.34 * mhs
    x0 = pad + mw * s + gap
    wb, ww = wordmark(spec, xh, th, x0, base)
    extra = ""
    if spec.get("tag"):
        tg = shape("ÓTICA", "Outfit", 11, 500, 0.5)
        tg = shape("ÓTICA", "Outfit", 11, 500, 0.5, x=x0 + 2, y=base + 17)
        extra = f'<path d="{tg.d}" fill="{th["tag"]}"/>'
    W, H = pad * 2 + mw * s + gap + ww, pad * 2 + mh * s
    return svg_doc(W, max(H, pad * 2 + mhs), md, f'<g transform="translate({pad} {pad}) scale({f(s)})">{mb}</g>{wb}{extra}')


def stacked(spec, th, pad=10):
    mw, mh, md, mb = mark(spec, th)
    s = 100 / 93
    xh = 31
    _, ww = wordmark(spec, xh, th, 0, 0)
    W = pad * 2 + max(100, ww)
    base = pad + mh * s + 18 + xh
    wb, ww = wordmark(spec, xh, th, (W - ww) / 2, base)
    tg = shape("ÓTICA", "Outfit", 14, 500, 0.6)
    tg = shape("ÓTICA", "Outfit", 14, 500, 0.6, x=(W - tg.width) / 2, y=base + 32)
    body = (f'<g transform="translate({f((W - mw * s) / 2)} {pad}) scale({f(s)})">{mb}</g>{wb}'
            f'<path d="{tg.d}" fill="{th["tag"]}"/>')
    return svg_doc(W, base + 32 + pad, md, body)


def icon(spec, size=128):
    th = THEMES["reverse"]
    mw, mh, md, mb = mark(spec, th)
    s = size * 0.60 / max(mw, mh)
    ox, oy = (size - mw * s) / 2, (size - mh * s) / 2
    bg = f'<rect width="{size}" height="{size}" rx="{size * 0.22}" fill="{ORANGE}"/>'
    return svg_doc(size, size, md, bg + f'<g transform="translate({f(ox)} {f(oy)}) scale({f(s)})">{mb}</g>')


VARIANTS = [
    ("A00-original", "Original refinada", "A versão que você aprovou, sem nenhuma mudança. Serve de régua.", {}),
    ("A01-nome-em-cafe", "Nome em café", "O nome em marrom-café; símbolo e til continuam laranja.",
     dict(text="espresso", til="custom", accent="orange")),
    ("A02-brilho", "Brilho nas lentes", "Um reflexo pequeno dentro das duas lentes.", dict(glint=True)),
    ("A03-ambar", "Pingo e til âmbar", "O pingo do i e o til do ã em âmbar: dois toques de cor, como o brilho de um olhar.",
     dict(til="custom", accent="amber", dot=True)),
    ("A04-mais-leve", "Letra mais leve", "Peso um degrau abaixo e um fio mais de espaço: mais elegante, menos gordinho.",
     dict(weight=630, tracking=0.05, soft=0.025)),
    ("A05-assinatura", "Com assinatura ÓTICA", "A palavra ÓTICA discreta embaixo do nome, também na versão horizontal.",
     dict(tag=True)),
    ("A06-tom-sobre-tom", "Tom sobre tom", "Uma faixa de laranja mais escuro seguindo a onda da base.", dict(band=True)),
    ("A07-onda-eco", "Onda eco", "Uma segunda onda fina logo abaixo do ícone, como reflexo na água.", dict(ripple=True)),
    ("A08-lentes-claras", "Lentes em tom claro", "As lentes ganham um laranja um pouco mais claro, como vidro.", dict(lens=True)),
    ("A09-cantos-suaves", "Cantos mais suaves", "Só os cantos do quadrado ficam mais arredondados.", dict(radius=19)),
]


def build():
    for vid, nome, desc, spec in VARIANTS:
        d = os.path.join(OUT, vid)
        os.makedirs(d, exist_ok=True)
        for nm, key in (("horizontal", "light"), ("horizontal-fundo-escuro", "dark"), ("horizontal-branco", "reverse")):
            open(os.path.join(d, nm + ".svg"), "w").write(horizontal(spec, THEMES[key]))
        open(os.path.join(d, "vertical.svg"), "w").write(stacked(spec, THEMES["light"]))
        open(os.path.join(d, "vertical-fundo-escuro.svg"), "w").write(stacked(spec, THEMES["dark"]))
        open(os.path.join(d, "icone.svg"), "w").write(icon(spec))
        for nm, key in (("simbolo", "light"), ("simbolo-branco", "reverse")):
            mw, mh, md, mb = mark(spec, THEMES[key])
            open(os.path.join(d, nm + ".svg"), "w").write(svg_doc(mw, mh, md, mb))
    print("ok", len(VARIANTS))


if __name__ == "__main__":
    build()
