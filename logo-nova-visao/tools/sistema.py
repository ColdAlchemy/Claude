"""Sistema de aplicações da logo Nova Visão (versão V01, Original refinada).

A mesma logo em formatos para cada uso. python3 sistema.py -> ../sistema/
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from textpath import shape
from build5 import themes, mark, wordmark, horizontal, stacked, icon, svg_doc, f, ORANGE, ESPRESSO, CREAM, WHITE

OUT = os.path.join(os.path.dirname(__file__), "..", "sistema")
T = themes(ORANGE)
BASE = {}
CAFE = dict(mark="espresso", text="espresso", accent="espresso")
SMALL = dict(ring=5.7, temple_w=8.4)  # mesma marca, traço mais grosso para tamanhos pequenos


def w(name, svg):
    open(os.path.join(OUT, name + ".svg"), "w").write(svg)


def nome_only(spec, th, xh=36, pad=6):
    base = pad + 1.72 * xh
    parts, ww = wordmark(spec, xh, th, pad, base)
    return svg_doc(ww + pad * 2, base + 0.12 * xh + pad, "", parts)


def mark_only(spec, th):
    mw, mh, md, mb = mark(spec, th)
    return svg_doc(mw, mh, md, mb)


def horizontal_otica_linha(spec, th, pad=6, mhs=70):
    """Símbolo + nome + divisor fino + ÓTICA (letreiros e assinaturas largas)."""
    mw, mh, md, mb = mark(spec, th)
    s = mhs / 93
    xh, base, gap = 0.49 * mhs, pad + 0.745 * mhs, 0.34 * mhs
    x0 = pad + mw * s + gap
    wb, ww = wordmark(spec, xh, th, x0, base)
    xd = x0 + ww + 0.5 * mhs
    tg = shape("ÓTICA", "Outfit", 0.30 * mhs, 500, 0.32)
    tg = shape("ÓTICA", "Outfit", 0.30 * mhs, 500, 0.32, x=xd + 0.34 * mhs, y=base - xh / 2 + 0.15 * mhs)
    div = (f'<path d="M{f(xd)} {f(base - xh * 1.15)}V{f(base + 0.12 * xh)}" stroke="{th["tag"]}" '
           f'stroke-width="2" stroke-linecap="round"/>')
    W = xd + 0.34 * mhs + tg.width + pad
    return svg_doc(W, pad * 2 + mhs, md, f'<g transform="translate({pad} {pad}) scale({f(s)})">{mb}</g>{wb}{div}<path d="{tg.d}" fill="{th["tag"]}"/>')


def avatar_circulo(size=128):
    th = T["reverse"]
    mw, mh, md, mb = mark(SMALL, th)
    s = size * 0.56 / mw
    ox, oy = (size - mw * s) / 2, (size - mh * s) / 2
    return svg_doc(size, size, md, f'<circle cx="{size / 2}" cy="{size / 2}" r="{size / 2}" fill="{ORANGE}"/>'
                   f'<g transform="translate({f(ox)} {f(oy)}) scale({f(s)})">{mb}</g>')


def icone_pequeno(size=128):
    th = T["reverse"]
    mw, mh, md, mb = mark(SMALL, th)
    s = size * 0.64 / mw
    ox, oy = (size - mw * s) / 2, (size - mh * s) / 2
    return svg_doc(size, size, md, f'<rect width="{size}" height="{size}" rx="{size * 0.22}" fill="{ORANGE}"/>'
                   f'<g transform="translate({f(ox)} {f(oy)}) scale({f(s)})">{mb}</g>')


def scallop(cx, cy, R, n=30, k=0.54):
    """Borda ondulada (festonada): n arcos levemente salientes ao redor do círculo."""
    chord = 2 * R * math.sin(math.pi / n)
    r = chord * k
    pts = [(cx + R * math.sin(2 * math.pi * i / n), cy - R * math.cos(2 * math.pi * i / n)) for i in range(n)]
    d = f"M{f(pts[0][0])} {f(pts[0][1])}"
    for i in range(1, n + 1):
        x, y = pts[i % n]
        d += f"A{f(r)} {f(r)} 0 0 1 {f(x)} {f(y)}"
    return d + "Z"


def arc_text(text, size, tracking, R, top, weight=700):
    """Texto em arco. top=True: no alto, lendo para fora; top=False: embaixo, de pé, lendo da esquerda para a direita."""
    run = shape(text, "Outfit", size, weight, tracking)
    Wt = run.width
    out = []
    for g in run.glyphs:
        if not g.d or g.ch == " ":
            continue
        m = g.x + g.adv / 2 - tracking * size / 2
        off = (m - Wt / 2) / R
        if top:
            out.append(f'<path d="{g.d}" transform="translate(120 120) rotate({f(math.degrees(off))}) translate({f(-m)} {-R})"/>')
        else:
            out.append(f'<path d="{g.d}" transform="translate(120 120) rotate({f(-math.degrees(off))}) translate({f(-m)} {R})"/>')
    return "".join(out)


def star(cx, cy, r):
    """Estrela de 4 pontas (separador)."""
    k = r * 0.28
    return (f'M{f(cx)} {f(cy - r)}L{f(cx + k)} {f(cy - k)}L{f(cx + r)} {f(cy)}L{f(cx + k)} {f(cy + k)}'
            f'L{f(cx)} {f(cy + r)}L{f(cx - k)} {f(cy + k)}L{f(cx - r)} {f(cy)}L{f(cx - k)} {f(cy - k)}Z')


def icone_sem_cantos(size=1024):
    """Ícone de app em quadrado cheio, sem cantos arredondados (iOS e lojas aplicam a máscara)."""
    th = T["reverse"]
    mw, mh, md, mb = mark(SMALL, th)
    s = size * 0.62 / mw
    ox, oy = (size - mw * s) / 2, (size - mh * s) / 2
    return svg_doc(size, size, md, f'<rect width="{size}" height="{size}" fill="{ORANGE}"/>'
                   f'<g transform="translate({f(ox)} {f(oy)}) scale({f(s)})">{mb}</g>')


def seal(kind):
    """Selo: borda ondulada, NOVA VISÃO em arco no alto, ÓTICA embaixo, símbolo no centro."""
    C = 120
    cfg = {
        "laranja": dict(disc=ORANGE, ink=WHITE, core=CREAM, sym=T["light"], sym_spec=SMALL),
        "contorno": dict(disc=None, ink=ORANGE, core=None, sym=T["light"], sym_spec=SMALL),
        "cafe": dict(disc=ESPRESSO, ink=CREAM, core=CREAM, sym=T["light"], sym_spec=dict(SMALL, mark="espresso")),
    }[kind]
    ink, disc, core = cfg["ink"], cfg["disc"], cfg["core"]
    body = ""
    if disc:
        body += f'<path d="{scallop(C, C, 112)}" fill="{disc}"/>'
    else:
        body += f'<path d="{scallop(C, C, 110)}" fill="none" stroke="{ink}" stroke-width="2.6" stroke-linejoin="round"/>'
    body += f'<circle cx="{C}" cy="{C}" r="97" fill="none" stroke="{ink}" stroke-width="1.6"/>'
    body += f'<circle cx="{C}" cy="{C}" r="68" fill="{core or "none"}" stroke="{ink if not core else "none"}" stroke-width="1.6"/>'
    body += f'<g fill="{ink}">{arc_text("NOVA VISÃO", 19, 0.16, 77, True)}{arc_text("ÓTICA", 19, 0.4, 90, False)}'
    body += f'<path d="{star(C - 83, C, 6)}"/><path d="{star(C + 83, C, 6)}"/></g>'
    mw, mh, md, mb = mark(cfg["sym_spec"], cfg["sym"])
    s = 84 / mw
    body += f'<g transform="translate({f(C - mw * s / 2)} {f(C - mh * s / 2)}) scale({f(s)})">{mb}</g>'
    return svg_doc(240, 240, md, body)


def build():
    os.makedirs(OUT, exist_ok=True)
    L, D, R = T["light"], T["dark"], T["reverse"]
    # 1. horizontal (principal) e variações de fundo
    w("01-horizontal", horizontal(BASE, L))
    w("01-horizontal-fundo-escuro", horizontal(BASE, D))
    w("01-horizontal-sobre-laranja-ou-foto", horizontal(BASE, R))
    w("01-horizontal-uma-cor-cafe", horizontal(CAFE, L))
    w("01-horizontal-uma-cor-cafe-fundo-escuro", horizontal(CAFE, D))
    # 2. horizontal com assinatura
    w("02-horizontal-assinatura-otica", horizontal(dict(tag=True), L))
    w("02-horizontal-linha-otica", horizontal_otica_linha(BASE, L))
    w("02-horizontal-linha-otica-fundo-escuro", horizontal_otica_linha(BASE, D))
    w("02-horizontal-linha-otica-sobre-laranja", horizontal_otica_linha(BASE, R))
    # 3. vertical
    w("03-vertical", stacked(BASE, L))
    w("03-vertical-fundo-escuro", stacked(BASE, D))
    w("03-vertical-sobre-laranja-ou-foto", stacked(BASE, R))
    w("03-vertical-uma-cor-cafe", stacked(CAFE, L))
    # 4. símbolo
    w("04-simbolo", mark_only(BASE, L))
    w("04-simbolo-branco", mark_only(BASE, R))
    w("04-simbolo-uma-cor-cafe", mark_only(CAFE, L))
    w("04-simbolo-tamanho-pequeno", mark_only(SMALL, L))
    w("04-simbolo-tamanho-pequeno-branco", mark_only(SMALL, R))
    # 5. só o nome
    w("05-nome", nome_only(BASE, L))
    w("05-nome-branco", nome_only(BASE, R))
    w("05-nome-cafe", nome_only(CAFE, L))
    # 6. avatar, ícone, favicon
    w("06-avatar-circulo", avatar_circulo())
    w("06-icone-app-quadrado", icon(BASE, T))
    w("06-favicon", icone_pequeno())
    w("06-icone-app-sem-cantos", icone_sem_cantos())
    # 7. selo
    w("07-selo-laranja", seal("laranja"))
    w("07-selo-contorno", seal("contorno"))
    w("07-selo-cafe", seal("cafe"))
    print("ok", len(os.listdir(OUT)))


if __name__ == "__main__":
    build()
