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


def seal(kind):
    """Selo circular: NOVA VISÃO · ÓTICA em volta do símbolo."""
    fill_disc = kind == "laranja"
    ink = WHITE if fill_disc else ORANGE
    th = T["reverse"] if fill_disc else T["light"]
    C, R = 110, 74
    txt = "NOVA VISÃO • ÓTICA • "
    probe = shape(txt, "Outfit", 20, 650, 0.08)
    tot = sum(g.adv for g in probe.glyphs)
    size = 20 * (2 * math.pi * R) / tot
    run = shape(txt, "Outfit", size, 650, 0.08)
    # centraliza "NOVA VISÃO" no topo
    mid_first = (run.glyphs[0].x + run.glyphs[9].x + run.glyphs[9].adv) / 2
    off = -mid_first / R
    parts = ""
    for g in run.glyphs:
        if not g.d or g.ch == " ":
            continue
        m = g.x + g.adv / 2
        ang = math.degrees(m / R + off)
        parts += f'<path d="{g.d}" transform="translate({C} {C}) rotate({f(ang)}) translate({f(-m)} {-R})" fill="{ink}"/>'
    mw, mh, md, mb = mark(SMALL, th)
    s = 74 / mw
    body = ""
    if fill_disc:
        body += f'<circle cx="{C}" cy="{C}" r="106" fill="{ORANGE}"/>'
    body += (f'<circle cx="{C}" cy="{C}" r="100" fill="none" stroke="{ink}" stroke-width="1.6"/>'
             f'<circle cx="{C}" cy="{C}" r="54" fill="none" stroke="{ink}" stroke-width="1.6"/>{parts}'
             f'<g transform="translate({f(C - mw * s / 2)} {f(C - mh * s / 2)}) scale({f(s)})">{mb}</g>')
    return svg_doc(220, 220, md, body)


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
    # 7. selo
    w("07-selo-laranja", seal("laranja"))
    w("07-selo-contorno", seal("contorno"))
    print("ok", len(os.listdir(OUT)))


if __name__ == "__main__":
    build()
