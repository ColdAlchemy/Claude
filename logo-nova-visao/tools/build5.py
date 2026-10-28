"""Nova Visão: coleção de versões do logo original refinado.

Símbolo e letra vêm das medidas do logo atual; cada versão muda um ou dois detalhes.
python3 build5.py -> ../versoes/<id>/
"""
import math, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from textpath import shape

OUT = os.path.join(os.path.dirname(__file__), "..", "versoes")
ORANGE, ESPRESSO, CREAM, WHITE, AMBER = "#FF6400", "#2B1710", "#FFF4E8", "#FFFFFF", "#FFA800"


def f(n):
    return f"{n:.2f}".rstrip("0").rstrip(".")


def mix(hex_a, hex_b, t):
    a = [int(hex_a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(hex_b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b))


def themes(o):
    return {
        "light": dict(container=o, orange=o, espresso=ESPRESSO, amber=AMBER, deep=mix(o, "#000000", 0.22), tag=mix(o, "#000000", 0.3),
                      band=mix(o, "#000000", 0.12), lens=mix(o, "#FFFFFF", 0.14), glint=WHITE),
        "dark": dict(container=o, orange=CREAM, espresso=CREAM, amber=AMBER, deep=CREAM, tag="#FFB27A",
                     band=mix(o, "#000000", 0.12), lens=mix(o, "#FFFFFF", 0.14), glint=WHITE),
        "reverse": dict(container=WHITE, orange=WHITE, espresso=WHITE, amber=WHITE, deep=WHITE, tag=WHITE,
                        band="#FFDCC6", lens="#FFE6D6", glint=o),
    }


# ---------------------------------------------------------------- símbolo (medidas do original)
RIGHT = dict(cx=59.7, cy=38.0, rx=18.7, ry=21.5, rot=-6)
LEFT = dict(cx=16.9, cy=55.3, rx=15.2, ry=19.2, rot=-9)
RING0 = 4.1
BAND = "M104 66V70Q100 75 92 78C84 81.5 78 82 72 82C56 82 44 73 30 69.5C20 67 12 73.5 6 73.5Q0 73.5 -4 70V110H104Z"
RIPPLE = "M5 95C14 95 20 91 30 91.5C44 92 56 104 72 104C82 104 90 102 96 98"


def container_path(r=11.5, w=1.0):
    wy = lambda y: 86.75 + (y - 86.75) * w
    q = lambda *ys: " ".join(f(wy(y)) if i % 2 else f(y) for i, y in enumerate(ys))
    return (f"M{r} 0H{100 - r}Q100 0 100 {r}V77Q100 {f(wy(86))} 92 {f(wy(89))}"
            f"C84 {f(wy(92.5))} 78 {f(wy(93))} 72 {f(wy(93))}C56 {f(wy(93))} 44 {f(wy(84))} 30 {f(wy(80.5))}"
            f"C20 {f(wy(78))} 12 {f(wy(84.5))} 6 {f(wy(84.5))}Q0 {f(wy(84.5))} 0 77V{r}Q0 0 {r} 0Z")


def ell(e, extra=""):
    return (f'<ellipse cx="{e["cx"]}" cy="{e["cy"]}" rx="{e["rx"]}" ry="{e["ry"]}" '
            f'transform="rotate({e["rot"]} {e["cx"]} {e["cy"]})"{extra}/>')


TEMPLE = "M77 23.2L106 31.4"
TEMPLE_WAVE = "M77 23.5C85 19.5 90 30 98 27S108 33 116 29"


def glasses_stroke(color, ring, L, R, temple=TEMPLE, bridge="M30.1 45.7Q36 40.3 41.6 43.6"):
    """Armação desenhada com traços (usada como recorte em máscara ou como traço visível)."""
    return (f'<g fill="none" stroke="{color}" stroke-width="{ring}" stroke-linecap="round">{ell(L)}{ell(R)}'
            f'<path d="{bridge}" stroke-width="{f(ring + 0.3)}"/></g>'
            f'<path d="{temple}" stroke="{color}" stroke-width="{7 if temple == TEMPLE else 6.4}" stroke-linecap="round" fill="none"/>')


def glint(color, L, R):
    def arc(e):
        rx, ry = e["rx"] - 5.2, e["ry"] - 5.2
        a0, a1 = math.radians(205), math.radians(250)
        p = lambda a: (e["cx"] + rx * math.cos(a), e["cy"] + ry * math.sin(a))
        (x0, y0), (x1, y1) = p(a0), p(a1)
        return (f'<path d="M{f(x0)} {f(y0)}A{f(rx)} {f(ry)} 0 0 1 {f(x1)} {f(y1)}" '
                f'transform="rotate({e["rot"]} {e["cx"]} {e["cy"]})"/>')
    return f'<g fill="none" stroke="{color}" stroke-width="2.2" stroke-linecap="round">{arc(L)}{arc(R)}</g>'


def mark(spec, th):
    w = spec.get("wave", 1.0)
    ring = spec.get("ring", RING0)
    tilt = spec.get("tilt", 0)
    L, R = LEFT, RIGHT
    if spec.get("circular"):
        L = dict(LEFT, rx=17.2, ry=17.2, rot=0, cy=56.5)
        R = dict(RIGHT, rx=20.1, ry=20.1, rot=0)
    temple = TEMPLE_WAVE if spec.get("haste_onda") else TEMPLE
    bridge = "M28.6 45.4Q35.2 40.4 41.6 44.6" if spec.get("circular") else "M30.1 45.7Q36 40.3 41.6 43.6"
    h = 106 if spec.get("ripple") else (86.75 + 6.25 * w)
    rot = f' transform="rotate({tilt} 40 46)"' if tilt else ""
    cp = container_path(spec.get("radius", 11.5), w)
    mk = spec.get("mark", "orange")
    cc = th["container"] if mk == "orange" else th[mk]
    wd = 100

    if spec.get("contorno"):
        # símbolo vazado: contorno do quadrado + armação em traço, recortada pelo quadrado
        defs = f'<clipPath id="cl"><path d="{cp}"/></clipPath>'
        body = (f'<g clip-path="url(#cl)"><g{rot}>{glasses_stroke(cc, ring + 0.6, L, R, temple, bridge)}</g></g>'
                f'<path d="{cp}" fill="none" stroke="{cc}" stroke-width="5" stroke-linejoin="round"/>')
        return 100, h, defs, body

    defs = (f'<mask id="k" maskUnits="userSpaceOnUse" x="-30" y="-30" width="170" height="170">'
            f'<rect x="-30" y="-30" width="170" height="170" fill="#fff"/><g{rot}>{glasses_stroke("#000", ring, L, R, temple, bridge)}</g></mask>')
    inner = ""
    if spec.get("sombra"):
        sh = th["deep"] if th["container"] != WHITE else th["band"]
        if th["container"] != WHITE:
            sh = mix(cc, "#000000", 0.26)
        inner += f'<path d="{cp}" fill="{sh}" transform="translate(3.2 3.6)"/>'
        wd, h = 104, h + 4
    inner += f'<path d="{cp}" fill="{cc}"/>'
    if spec.get("band"):
        defs += f'<clipPath id="cc"><path d="{cp}"/></clipPath>'
        bc = th["band"] if mk == "orange" else (mix(cc, "#000000", 0.25) if th["container"] != WHITE else th["band"])
        inner += f'<g clip-path="url(#cc)"><path d="{BAND}" fill="{bc}"/></g>'
    body = f'<g mask="url(#k)">{inner}</g>'
    extra = ""
    if spec.get("lens"):
        for e in (L, R):
            extra += ell(dict(e, rx=f(e["rx"] - ring / 2 + 0.1), ry=f(e["ry"] - ring / 2 + 0.1)), f' fill="{th["lens"]}"')
    if spec.get("glint"):
        extra += glint(th["glint"], L, R)
    if extra:
        body += f'<g{rot}>{extra}</g>'
    if spec.get("ripple"):
        body += f'<path d="{RIPPLE}" fill="none" stroke="{cc}" stroke-width="4.2" stroke-linecap="round"/>'
    return wd, h, defs, body


# ---------------------------------------------------------------- wordmark
def tilde(cx, y, width, sw, amp, color):
    x0, x1 = cx - width / 2, cx + width / 2
    return (f'<path d="M{f(x0)} {f(y)}Q{f(x0 + width / 4)} {f(y - 2 * amp)} {f(cx)} {f(y)}T{f(x1)} {f(y)}" '
            f'fill="none" stroke="{color}" stroke-width="{f(sw)}" stroke-linecap="round"/>')


def split_dot(d):
    subs = ["M" + s for s in d.split("M") if s]
    top = lambda s: min([float(n) for n in re.findall(r"-?\d+\.?\d*", s)][1::2])
    subs.sort(key=top)
    return subs[0], "".join(subs[1:])


FONTS = {"geo": dict(font="Outfit", weight=790, tracking=-0.008, soft=0.04),
         "soft": dict(font="Fredoka", weight=700, tracking=-0.01, soft=0.0)}


def wordmark(spec, xh_target, th, x, base):
    fs = FONTS[spec.get("fonte", "geo")]
    font, weight, tr, soft = fs["font"], spec.get("weight", fs["weight"]), spec.get("tracking", fs["tracking"]), spec.get("soft", fs["soft"])
    til_custom = spec.get("til") == "custom"
    txt = "nova visao" if til_custom else "nova visão"
    probe = shape(txt, font, 100, weight)
    size = 100 * xh_target / probe.xheight
    run = shape(txt, font, size, weight, tr, x=x, y=base)
    xh = run.xheight
    text_c, acc_c = th[spec.get("text", "orange")], th[spec.get("accent", "orange")]
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


def svg_doc(w, h, defs, body, title="Nova Visão ótica"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {f(w)} {f(h)}" role="img" aria-label="{title}">'
            f'<title>{title}</title><defs>{defs}</defs>{body}</svg>\n')


def horizontal(spec, th, pad=6, mhs=70):
    mw, mh, md, mb = mark(spec, th)
    s = mhs / 93
    xh, base, gap = 0.49 * mhs, pad + 0.745 * mhs, 0.34 * mhs
    x0 = pad + mw * s + gap
    wb, ww = wordmark(spec, xh, th, x0, base)
    extra = ""
    if spec.get("tag"):
        tg = shape("ÓTICA", "Outfit", 11, 500, 0.5, x=x0 + 2, y=base + 17)
        extra = f'<path d="{tg.d}" fill="{th["tag"]}"/>'
    W, H = pad * 2 + mw * s + gap + ww, max(pad * 2 + mh * s, pad * 2 + mhs)
    return svg_doc(W, H, md, f'<g transform="translate({pad} {pad}) scale({f(s)})">{mb}</g>{wb}{extra}')


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


def icon(spec, T, size=128):
    th = T["reverse"]
    mw, mh, md, mb = mark(spec, th)
    s = size * 0.60 / max(mw, mh)
    ox, oy = (size - mw * s) / 2, (size - mh * s) / 2
    bg = f'<rect width="{size}" height="{size}" rx="{size * 0.22}" fill="{T["light"]["container"]}"/>'
    return svg_doc(size, size, md, bg + f'<g transform="translate({f(ox)} {f(oy)}) scale({f(s)})">{mb}</g>')


# ---------------------------------------------------------------- coleção
VISTAS = "As que você já viu"
NOVAS = "Já apresentadas (novas na rodada anterior)"
NOVAS2 = "Novas"
VARIANTS = [
    ("V01-original-refinada", VISTAS, "Original refinada", "O logo atual redesenhado com precisão, sem nenhuma mudança. É a régua das outras.", {}),
    ("V02-letra-arredondada", VISTAS, "Letra arredondada", "Mesmo símbolo, com letras de cantos macios (Fredoka).", dict(fonte="soft", til="fonte")),
    ("V03-nome-em-cafe", VISTAS, "Nome em café", "O nome em marrom-café; símbolo e til continuam laranja.", dict(text="espresso", til="custom")),
    ("V04-brilho", VISTAS, "Brilho nas lentes", "Um reflexo pequeno dentro das duas lentes.", dict(glint=True)),
    ("V05-ambar", VISTAS, "Pingo e til âmbar", "O pingo do i e o til do ã em âmbar.", dict(til="custom", accent="amber", dot=True)),
    ("V06-mais-leve", VISTAS, "Letra mais leve", "Peso um degrau abaixo e um fio mais de espaço.", dict(weight=630, tracking=0.05, soft=0.025)),
    ("V07-assinatura", VISTAS, "Com assinatura ÓTICA", "A palavra ÓTICA discreta embaixo do nome, também na horizontal.", dict(tag=True)),
    ("V08-tom-sobre-tom", VISTAS, "Tom sobre tom", "Faixa de laranja mais escuro seguindo a onda da base.", dict(band=True)),
    ("V09-onda-eco", VISTAS, "Onda eco", "Uma segunda onda fina logo abaixo do ícone.", dict(ripple=True)),
    ("V10-lentes-claras", VISTAS, "Lentes em tom claro", "As lentes num laranja um pouco mais claro, como vidro.", dict(lens=True)),
    ("V11-cantos-suaves", VISTAS, "Cantos mais suaves", "Só os cantos do quadrado ficam mais arredondados.", dict(radius=19)),
    ("V12-arredondada-cafe", NOVAS, "Arredondada + café", "Letra arredondada com o nome em marrom-café.", dict(fonte="soft", text="espresso", til="fonte")),
    ("V13-arredondada-ambar", NOVAS, "Arredondada + âmbar", "Letra arredondada com pingo do i âmbar.", dict(fonte="soft", dot=True, accent="amber")),
    ("V14-brilho-cafe", NOVAS, "Brilho + café", "Reflexo nas lentes e nome em marrom-café.", dict(glint=True, text="espresso", til="custom")),
    ("V15-anel-fino", NOVAS, "Óculos de aro fino", "O aro das lentes mais fino: mais leve e delicado.", dict(ring=3.1)),
    ("V16-anel-grosso", NOVAS, "Óculos de aro grosso", "O aro mais grosso: mais presença em tamanho pequeno.", dict(ring=5.3)),
    ("V17-mais-inclinado", NOVAS, "Óculos mais inclinados", "A armação gira um pouco mais, com mais movimento.", dict(tilt=-9)),
    ("V18-onda-marcada", NOVAS, "Onda mais marcada", "A onda da base com mais subida e descida.", dict(wave=1.55)),
    ("V19-laranja-queimado", NOVAS, "Laranja queimado", "Um laranja mais fechado e quente (#F2530C).", dict(orange="#F2530C")),
    ("V20-laranja-solar", NOVAS, "Laranja solar", "Um laranja mais claro e luminoso (#FF7A00).", dict(orange="#FF7A00")),
    ("V21-nome-laranja-escuro", NOVAS, "Nome em laranja escuro", "Símbolo no laranja da marca e nome num laranja mais escuro.", dict(text="deep")),
    ("V22-mono-cafe", NOVAS, "Monocromática café", "Símbolo e nome inteiros em marrom-café, para uso sem cor.", dict(mark="espresso", text="espresso", accent="espresso")),
    ("V23-til-em-onda", NOVAS, "Til em onda", "Só o til do ã refeito como uma onda, como a base do ícone.", dict(til="custom")),
    ("V24-cafe-tom", NOVAS, "Café + tom sobre tom", "Nome em café e a faixa mais escura na onda.", dict(text="espresso", til="custom", band=True)),
    ("V25-respiro", NOVAS2, "Letras com respiro", "A mesma letra, com um fio mais de espaço entre elas. Lê melhor em tamanho grande.", dict(weight=775, tracking=0.034, soft=0.035)),
    ("V26-mais-pesada", NOVAS2, "Letra mais pesada", "Um degrau a mais de peso: ainda mais compacta e forte.", dict(weight=850, tracking=-0.014, soft=0.045)),
    ("V27-lentes-circulares", NOVAS2, "Lentes circulares", "As lentes ovais viram círculos perfeitos, sem mexer em mais nada.", dict(circular=True)),
    ("V28-haste-onda", NOVAS2, "Haste em onda", "A haste dos óculos ondula, repetindo a onda da base.", dict(haste_onda=True)),
    ("V29-contorno", NOVAS2, "Símbolo em contorno", "O quadrado vira contorno e a armação em traço: mais leve, bom para uso em uma cor.", dict(contorno=True)),
    ("V30-sombra-dura", NOVAS2, "Sombra dura", "Uma sombra sólida deslocada atrás do ícone, sem desfoque.", dict(sombra=True)),
    ("V31-brilho-tom", NOVAS2, "Brilho + tom sobre tom", "Reflexo nas lentes e faixa escura na onda.", dict(glint=True, band=True)),
    ("V32-brilho-lentes", NOVAS2, "Brilho + lentes claras", "Lentes em tom claro com o reflexo por cima.", dict(glint=True, lens=True)),
    ("V33-assinatura-cafe", NOVAS2, "Assinatura + café", "Nome em marrom-café com a palavra ÓTICA embaixo.", dict(tag=True, text="espresso", til="custom")),
    ("V34-queimado-brilho", NOVAS2, "Laranja queimado + brilho", "O laranja mais fechado com o reflexo nas lentes.", dict(orange="#F2530C", glint=True)),
    ("V35-til-ambar", NOVAS2, "Só o til âmbar", "Apenas o til do ã em âmbar, o resto igual.", dict(til="custom", accent="amber")),
    ("V36-arredondada-brilho", NOVAS2, "Arredondada + brilho", "Letra arredondada com o reflexo nas lentes.", dict(fonte="soft", glint=True, til="fonte")),
]


def build():
    for vid, grupo, nome, desc, spec in VARIANTS:
        T = themes(spec.get("orange", ORANGE))
        d = os.path.join(OUT, vid)
        os.makedirs(d, exist_ok=True)
        for nm, key in (("horizontal", "light"), ("horizontal-fundo-escuro", "dark"), ("horizontal-branco", "reverse")):
            open(os.path.join(d, nm + ".svg"), "w").write(horizontal(spec, T[key]))
        open(os.path.join(d, "vertical.svg"), "w").write(stacked(spec, T["light"]))
        open(os.path.join(d, "vertical-fundo-escuro.svg"), "w").write(stacked(spec, T["dark"]))
        open(os.path.join(d, "icone.svg"), "w").write(icon(spec, T))
        for nm, key in (("simbolo", "light"), ("simbolo-branco", "reverse")):
            mw, mh, md, mb = mark(spec, T[key])
            open(os.path.join(d, nm + ".svg"), "w").write(svg_doc(mw, mh, md, mb))
    print("ok", len(VARIANTS))


if __name__ == "__main__":
    build()
