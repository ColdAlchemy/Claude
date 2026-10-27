"""Gera os conceitos de logo da Nova Visão (SVG puro, texto em curvas).

python3 build.py            -> escreve em ../conceitos/<id>/
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from textpath import shape

OUT = os.path.join(os.path.dirname(__file__), "..", "conceitos")

ORANGE = "#FF6400"
ESPRESSO = "#2B1710"
CREAM = "#FFF4E8"
WHITE = "#FFFFFF"


def f(n):
    return f"{n:.2f}".rstrip("0").rstrip(".")


def pt(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


# ---------------------------------------------------------------- containers
def wave_square(r=26):
    """Quadrado de cantos suaves; a base é uma onda em S com tangentes horizontais nos extremos."""
    return (
        f"M{r} 0H{100 - r}A{r} {r} 0 0 1 100 {r}V72Q100 96 76 96"
        "C58 96 43 86 25 86Q0 86 0 62V26"
        f"A{r} {r} 0 0 1 {r} 0Z"
    )


# ---------------------------------------------------------------- themes
class Theme:
    def __init__(self, name, container, glass, text, accent, shadow, tag):
        self.name, self.container, self.glass = name, container, glass
        self.text, self.accent, self.shadow, self.tag = text, accent, shadow, tag


LIGHT = Theme("light", ORANGE, WHITE, ESPRESSO, "#FFB800", ESPRESSO, "#8A6B5A")
DARK = Theme("dark", ORANGE, WHITE, CREAM, "#FFB800", CREAM, "#C9A58E")
REVERSE = Theme("reverse", WHITE, ORANGE, WHITE, WHITE, WHITE, WHITE)
THEMES = [LIGHT, DARK, REVERSE]


# ---------------------------------------------------------------- marcas
# Cada marca devolve (w, h, defs, body) para um tema. Coordenadas locais.
def glasses_knock(cx1, cy1, r1, cx2, cy2, r2, sw, arm_to, bridge_deg=38, lift=9):
    """Armação como traços pretos (para máscara de recorte)."""
    bx1, by1 = pt(cx1, cy1, r1, -bridge_deg)
    bx2, by2 = pt(cx2, cy2, r2, -180 + bridge_deg)
    mx, my = (bx1 + bx2) / 2, min(by1, by2) - lift
    ax, ay = cx2 + r2, cy2
    return (
        f'<g fill="none" stroke="#000" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">'
        f'<circle cx="{f(cx1)}" cy="{f(cy1)}" r="{f(r1)}"/>'
        f'<circle cx="{f(cx2)}" cy="{f(cy2)}" r="{f(r2)}"/>'
        f'<path d="M{f(bx1)} {f(by1)}Q{f(mx)} {f(my)} {f(bx2)} {f(by2)}"/>'
        f'<path d="M{f(ax)} {f(ay)}L{f(arm_to)} {f(ay - 1)}"/></g>'
    )


def std_glasses(sw, lift=8):
    return glasses_knock(32, 46, 20, 68, 41, 16.5, sw, 108, lift=lift)


def knockout(uid, w, h, shape_svg, knock_svg, fill, extra=""):
    return (
        f'<mask id="{uid}" maskUnits="userSpaceOnUse" x="-20" y="-20" width="{w + 40}" height="{h + 40}">'
        f'<rect x="-20" y="-20" width="{w + 40}" height="{h + 40}" fill="#fff"/>{knock_svg}</mask>',
        f'<g mask="url(#{uid})">{shape_svg.replace("FILL", fill)}</g>{extra}',
    )


def mark_01(t):
    """Traço único: o óculos é um só gesto e a haste termina em onda."""
    c = ORANGE if t.name != "reverse" else WHITE
    body = (
        f'<g fill="none" stroke="{c}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="30" cy="36" r="20"/><circle cx="80" cy="32" r="16.5"/>'
        '<path d="M46 23Q55 14 66 21"/>'
        '<path d="M96 31C103 24 111 24 117 31S131 38 138 31"/></g>'
    )
    return 146, 72, "", body


def mark_02(t):
    """Container com onda, óculos finos e um brilho na lente (premium)."""
    k = std_glasses(4.6, lift=9)
    sh = f'<path d="{wave_square()}" fill="FILL"/>'
    d, b = knockout("k02", 100, 100, sh, k, t.container)
    glint = f'<path d="M20 40A12 12 0 0 1 28 32" fill="none" stroke="{t.container}" stroke-width="3.2" stroke-linecap="round"/>'
    return 100, 100, d, b + glint


def mark_03(t):
    """Duas lentes, um horizonte: uma única onda atravessa as duas lentes."""
    c = ORANGE if t.name != "reverse" else WHITE
    wave = "M-4 40C8 31 22 31 34 40S58 49 70 40S96 31 108 40S128 49 136 40"
    defs = (
        f'<mask id="m03" maskUnits="userSpaceOnUse" x="-20" y="-20" width="190" height="110"><rect x="-20" y="-20" width="190" height="110" fill="#fff"/>'
        f'<path d="{wave}" fill="none" stroke="#000" stroke-width="5.5" stroke-linecap="round"/></mask>'
    )
    body = (
        f'<g mask="url(#m03)" fill="{c}"><circle cx="27" cy="34" r="26"/><circle cx="97" cy="31" r="24"/></g>'
        f'<path d="M49 23Q62 8 76 22" fill="none" stroke="{c}" stroke-width="6" stroke-linecap="round"/>'
        f'<path d="M120 29C127 22 134 22 140 29S154 36 161 29" fill="none" stroke="{c}" stroke-width="6" stroke-linecap="round"/>'
    )
    return 164, 62, defs, body


def mark_04(t):
    """Evolução fiel: o original, redesenhado e polido."""
    k = std_glasses(6.8)
    sh = f'<path d="{wave_square()}" fill="FILL"/>'
    d, b = knockout("k04", 100, 100, sh, k, t.container)
    return 100, 100, d, b


def mark_05(t):
    """Olhar que sorri: óculos como olhos e uma onda-sorriso."""
    blob = "M50 2C80 2 98 18 98 48C98 74 86 98 50 98C14 98 2 74 2 48C2 18 20 2 50 2Z"
    k = glasses_knock(33, 38, 18, 67, 38, 18, 6.6, 108, lift=9)
    k += '<path d="M31 70C41 83 59 83 69 70" fill="none" stroke="#000" stroke-width="6.6" stroke-linecap="round"/>'
    sh = f'<path d="{blob}" fill="FILL"/>'
    d, b = knockout("k05", 100, 100, sh, k, t.container)
    return 100, 100, d, b


def mark_06(t):
    """Folha: container orgânico; a haste vira nervura em onda."""
    leaf = "M0 50A50 50 0 0 1 50 0H84Q100 0 100 16V50A50 50 0 0 1 50 100H16Q0 100 0 84Z"
    k = std_glasses(6)
    k = k.replace("L108 40", "C118 33 124 47 130 40")
    sh = f'<path d="{leaf}" fill="FILL"/>'
    d, b = knockout("k06", 100, 100, sh, k, t.container)
    return 100, 100, d, b


def mark_07(t):
    """Sticker: container inclinado, sombra dura e lentes amarelas."""
    sh_c = t.shadow if t.name != "reverse" else WHITE
    lens = "#FFC247" if t.name != "reverse" else WHITE
    wsq = wave_square()
    k = std_glasses(7.6)
    d, b = knockout("k07", 100, 100, f'<path d="{wsq}" fill="FILL"/>', k, t.container)
    lenses = (
        f'<circle cx="32" cy="46" r="17" fill="{lens}"/><circle cx="68" cy="41" r="13.5" fill="{lens}"/>'
        if t.name != "reverse" else ""
    )
    shadow = "" if t.name == "reverse" else f'<path d="{wsq}" fill="{sh_c}" transform="translate(5 6)"/>'
    body = f'<g transform="rotate(-7 50 50)">{shadow}{b}{lenses}</g>'
    return 108, 108, d, f'<g transform="translate(4 2)">{body}</g>'


def mark_08(t):
    """Órbita: dois aros que se cruzam; a interseção vira a ponte e a haste é onda."""
    a, b_, ov = (ORANGE, "#FFB800", "#E8330B") if t.name != "reverse" else (WHITE, WHITE, "#FFD9C2")
    defs = '<clipPath id="c08"><circle cx="30" cy="38" r="25"/></clipPath>'
    body = (
        f'<circle cx="30" cy="38" r="25" fill="none" stroke="{a}" stroke-width="10"/>'
        f'<circle cx="68" cy="34" r="22" fill="none" stroke="{b_}" stroke-width="10"/>'
        f'<g clip-path="url(#c08)"><circle cx="68" cy="34" r="22" fill="none" stroke="{ov}" stroke-width="10"/></g>'
        f'<path d="M90 34C98 26 106 26 112 34S126 42 134 34" fill="none" stroke="{b_}" stroke-width="7" stroke-linecap="round"/>'
    )
    return 140, 72, defs, body


# ---------------------------------------------------------------- wordmark
def tilde_wave(cx, y, width, sw, amp, color):
    x0, x1 = cx - width / 2, cx + width / 2
    q = width / 4
    return (
        f'<path d="M{f(x0)} {f(y + amp * .2)}C{f(x0 + q * .8)} {f(y - amp)} {f(x0 + q * 1.5)} {f(y - amp)} {f(cx)} {f(y)}'
        f'S{f(x1 - q * .8)} {f(y + amp)} {f(x1)} {f(y - amp * .2)}" fill="none" stroke="{color}" stroke-width="{f(sw)}" stroke-linecap="round"/>'
    )


def wordmark(spec, xh_target, t, x=0, base=0):
    """Texto em curvas, tamanho calculado pelo x-height alvo. Retorna (svg, largura, xh)."""
    probe = shape("nova visao", spec["font"], 100, spec["weight"])
    size = 100 * xh_target / probe.xheight
    run = shape("nova visao", spec["font"], size, spec["weight"], spec.get("tracking", 0), x=x, y=base,
                custom_adv=spec.get("adv"))
    xh = run.xheight
    parts = [f'<path d="{run.d}" fill="{t.text}"/>']
    a = run.glyphs[8]
    tilde_c = spec.get("tilde_color", t.text)
    if tilde_c == "accent":
        tilde_c = t.accent if t.name != "reverse" else WHITE
    cxa = a.x + a.adv / 2 - spec.get("tracking", 0) * size / 2
    parts.append(tilde_wave(cxa + spec.get("tilde_dx", 0) * size, base - xh - spec.get("tilde_gap", 0.2) * xh,
                            spec.get("tilde_w", 0.7) * xh, spec.get("tilde_sw", 0.2) * xh,
                            spec.get("tilde_amp", 0.12) * xh, tilde_c))
    return "".join(parts), run.width, xh


# ---------------------------------------------------------------- conceitos
CONCEPTS = [
    dict(id="01-traco-unico", nome="Traço único", mood="Premium acessível", ref="Warby Parker",
         desc="Óculos desenhados num só gesto: a haste escorre e vira a onda da marca. Sem container, leve e elegante.",
         mark=mark_01, mh=62, gap=26,
         wm=dict(font="Outfit", weight=500, tracking=0.01, tilde_color="accent", tilde_w=.62, tilde_sw=.17)),
    dict(id="02-serifa-suave", nome="Serifa suave", mood="Premium acessível", ref="Warby Parker",
         desc="Serifa de cantos suaves traz calor editorial; o ícone ganha traço fino e um brilho na lente.",
         mark=mark_02, mh=74, gap=22,
         wm=dict(font="Fraunces", weight=600, tracking=0.0, tilde_color="accent", tilde_w=.5, tilde_sw=.16, tilde_gap=.16)),
    dict(id="03-horizonte", nome="Duas lentes, um horizonte", mood="Geométrico & ousado", ref="Lenscrafters",
         desc="Duas lentes cortadas por uma única onda contínua: o horizonte de uma visão nova.",
         mark=mark_03, mh=58, gap=24,
         wm=dict(font="Sora", weight=700, tracking=-0.01, tilde_w=.6, tilde_sw=.2)),
    dict(id="04-evolucao", nome="Evolução fiel", mood="Geométrico & ousado", ref="Lenscrafters",
         desc="O logo atual, refinado: proporções de lente mais precisas, onda com ritmo e tipografia redesenhada.",
         mark=mark_04, mh=74, gap=22,
         wm=dict(font="Outfit", weight=700, tracking=0.0, tilde_w=.6, tilde_sw=.2)),
    dict(id="05-sorriso", nome="Olhar que sorri", mood="Orgânico & humano", ref="Óticas Carol",
         desc="Duas lentes viram olhos e a onda vira sorriso. Marca de gente, próxima e acolhedora.",
         mark=mark_05, mh=74, gap=22,
         wm=dict(font="Nunito", weight=800, tracking=0.0, adv={" ": -0.07}, tilde_w=.6, tilde_sw=.2)),
    dict(id="06-folha", nome="Folha", mood="Orgânico & humano", ref="Óticas Carol",
         desc="Container em formato de folha, com a haste em onda. Cuidado, frescor e crescimento.",
         mark=mark_06, mh=74, gap=22,
         wm=dict(font="Quicksand", weight=700, tracking=0.0, adv={" ": -0.1}, tilde_color="accent", tilde_w=.6, tilde_sw=.17)),
    dict(id="07-sticker", nome="Sticker", mood="Jovem & divertido", ref="Chilli Beans",
         desc="Container inclinado com sombra dura e lentes amarelas. Pede para virar adesivo, sacola e story.",
         mark=mark_07, mh=78, gap=20,
         wm=dict(font="Baloo2", weight=800, tracking=0.0, tilde_color="accent", tilde_w=.55, tilde_sw=.2, tilde_gap=.1)),
    dict(id="08-orbita", nome="Órbita", mood="Jovem & divertido", ref="Chilli Beans",
         desc="Dois aros em laranja e amarelo; onde se cruzam nasce a ponte dos óculos. A onda assina por baixo.",
         mark=mark_08, mh=66, gap=22,
         wm=dict(font="Lexend", weight=800, tracking=-0.01, adv={" ": -0.14}, tilde_color="accent", tilde_w=.55, tilde_sw=.2)),
]


# ---------------------------------------------------------------- composição
def svg_doc(w, h, defs, body, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {f(w)} {f(h)}" role="img" aria-label="{title}">'
        f'<title>{title}</title>' + (f"<defs>{defs}</defs>" if defs else "") + body + "</svg>\n"
    )


def horizontal(c, t, pad=6):
    mw, mh, mdefs, mbody = c["mark"](t)
    s = c["mh"] / mh
    mark_w = mw * s
    xh = c["mh"] * c["wm"].get("xh", 0.46)
    base_y = pad + c["mh"] / 2 + xh / 2
    wm, ww, _ = wordmark(c["wm"], xh, t, x=pad + mark_w + c["gap"], base=base_y)
    W = pad * 2 + mark_w + c["gap"] + ww
    H = pad * 2 + c["mh"]
    body = f'<g transform="translate({pad} {pad}) scale({f(s)})">{mbody}</g>{wm}'
    return svg_doc(W, H, mdefs, body, "Nova Visão ótica")


def stacked(c, t, pad=8):
    mw, mh, mdefs, mbody = c["mark"](t)
    mhs = 108
    s = mhs / mh
    mark_w = mw * s
    xh = 30
    wm_probe, ww, _ = wordmark(c["wm"], xh, t, x=0, base=0)
    W = pad * 2 + max(mark_w, ww)
    mx = (W - mark_w) / 2
    base = pad + mhs + 22 + xh
    wm, ww, _ = wordmark(c["wm"], xh, t, x=(W - ww) / 2, base=base)
    tag = shape("ÓTICA", "Outfit", 15, 500, 0.5)
    tx = (W - tag.width) / 2
    tag = shape("ÓTICA", "Outfit", 15, 500, 0.5, x=tx, y=base + 34)
    H = base + 34 + pad + 2
    body = (
        f'<g transform="translate({f(mx)} {pad}) scale({f(s)})">{mbody}</g>{wm}'
        f'<path d="{tag.d}" fill="{t.tag}"/>'
    )
    return svg_doc(W, H, mdefs, body, "Nova Visão ótica")


def icon(c, t_name="light", size=128):
    """Avatar: marca branca sobre quadrado laranja arredondado (ou o próprio container)."""
    t = REVERSE
    mw, mh, mdefs, mbody = c["mark"](t)
    inner = size * (0.74 if mw / mh > 1.3 else 0.64)
    s = min(inner / mw, inner / mh)
    ox, oy = (size - mw * s) / 2, (size - mh * s) / 2
    bg = f'<rect width="{size}" height="{size}" rx="{size * 0.24}" fill="{ORANGE}"/>'
    body = bg + f'<g transform="translate({f(ox)} {f(oy)}) scale({f(s)})">{mbody}</g>'
    return svg_doc(size, size, mdefs, body, "Nova Visão ótica, ícone")


def build():
    for c in CONCEPTS:
        d = os.path.join(OUT, c["id"])
        os.makedirs(d, exist_ok=True)
        for t in THEMES:
            suffix = {"light": "", "dark": "-fundo-escuro", "reverse": "-branco"}[t.name]
            open(os.path.join(d, f"horizontal{suffix}.svg"), "w").write(horizontal(c, t))
        open(os.path.join(d, "vertical.svg"), "w").write(stacked(c, LIGHT))
        open(os.path.join(d, "vertical-fundo-escuro.svg"), "w").write(stacked(c, DARK))
        open(os.path.join(d, "icone.svg"), "w").write(icon(c))
    print("ok")


if __name__ == "__main__":
    build()
