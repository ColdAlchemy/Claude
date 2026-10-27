import math, os, sys
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

SCR = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(SCR, "fonts")
OUT = "/home/user/Claude/nova-visao-refinadas"
os.makedirs(os.path.join(OUT, "svg"), exist_ok=True)

ORANGE = "#FF5F00"
WHITE = "#FFFFFF"
CAFE = "#2B1A12"


class Face:
    def __init__(self, src, axes, name):
        out = os.path.join(FONTS, name + ".ttf")
        f = TTFont(os.path.join(FONTS, src))
        instancer.instantiateVariableFont(f, axes, inplace=True)
        f.save(out)
        self.tt = TTFont(out)
        self.gs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        self.upm = self.tt["head"].unitsPerEm
        self.hbfont = hb.Font(hb.Face(hb.Blob.from_file_path(out)))
        os2 = self.tt["OS/2"]
        self.xh = os2.sxHeight / self.upm
        self.cap = os2.sCapHeight / self.upm

    def shape(self, text, size, tracking=0.0):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hbfont, buf, {"kern": True, "liga": False})
        s = size / self.upm
        x = 0.0
        items = []
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            name = self.order[info.codepoint]
            items.append(dict(name=name, x=x + pos.x_offset * s, adv=pos.x_advance * s))
            x += pos.x_advance * s + tracking * size
        return items, x - tracking * size

    def path(self, items, size, ox, oy):
        s = size / self.upm
        pen = SVGPathPen(self.gs, ntos=lambda v: f"{v:.2f}")
        for it in items:
            self.gs[it["name"]].draw(TransformPen(pen, (s, 0, 0, -s, ox + it["x"], oy)))
        return pen.getCommands()

    def bounds(self, it, size):
        bp = BoundsPen(self.gs)
        self.gs[it["name"]].draw(bp)
        s = size / self.upm
        x0, y0, x1, y1 = bp.bounds
        return (it["x"] + x0 * s, y0 * s, it["x"] + x1 * s, y1 * s)


def wave(x0, y0, w, amp):
    f = lambda v: f"{v:.2f}"
    return (f"M{f(x0)},{f(y0)} C{f(x0+w*.17)},{f(y0-amp*1.33)} {f(x0+w*.33)},{f(y0-amp*1.33)} {f(x0+w*.5)},{f(y0)} "
            f"S{f(x0+w*.83)},{f(y0+amp*1.33)} {f(x0+w)},{f(y0)}")


def svg(w, h, body, bg=None, pad=0):
    r = f'<rect x="{-pad}" y="{-pad}" width="{w+2*pad}" height="{h+2*pad}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {w+2*pad:.1f} {h+2*pad:.1f}" '
            f'role="img" aria-label="Ótica Nova Visão">{r}{body}</svg>')


# ------------------------------------------------------------------ A · POPULAR
NUN = Face("Nunito.ttf", {"wght": 900}, "nunito900")
NUN8 = Face("Nunito.ttf", {"wght": 800}, "nunito800")


def a_symbol(x, y, size, box, glass):
    """Contêiner compacto 240x240: óculos-olhos com ponte em til e pupilas olhando adiante."""
    k = size / 240
    cy = 106
    parts = []
    parts.append(f'<rect width="240" height="200" rx="62" fill="{box}"/>')
    R, r_, c1, c2 = 38, 14, 71, 169
    ring = ""
    for cx in (c1, c2):
        ring += (f"M{cx-R},{cy} a{R},{R} 0 1,0 {2*R},0 a{R},{R} 0 1,0 {-2*R},0 Z "
                 f"M{cx+5-r_},{cy-4} a{r_},{r_} 0 1,0 {2*r_},0 a{r_},{r_} 0 1,0 {-2*r_},0 Z ")
    parts.append(f'<path d="{ring}" fill="{glass}" fill-rule="evenodd"/>')
    by = cy - 18
    sw = 9
    parts.append(f'<path d="{wave(90, by, 60, 6)}" fill="none" stroke="{glass}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>')
    for sx0, sx1 in ((c1 - 28, 26), (c2 + 28, 214)):
        parts.append(f'<path d="M{sx0},{by} L{sx1},{by}" stroke="{glass}" stroke-width="{sw}" stroke-linecap="round"/>')
    return f'<g transform="translate({x},{y}) scale({k:.4f})">{"".join(parts)}</g>'


def a_wordmark(x, y, size, color, face=NUN):
    """x,y = origem da linha de base. O til do ã é a mesma onda da ponte do óculos."""
    items, w = face.shape("nova visao", size, tracking=-0.012)
    d = face.path(items, size, x, y)
    a = face.bounds(items[8], size)
    cx = x + (a[0] + a[2]) / 2
    til_w = (a[2] - a[0]) * 0.95
    ty = y - face.xh * size - size * 0.125
    sw = size * 0.085
    til = (f'<path d="{wave(cx - til_w/2, ty, til_w, size*0.062)}" fill="none" stroke="{color}" '
           f'stroke-width="{sw:.2f}" stroke-linecap="round" stroke-linejoin="round"/>')
    return f'<path d="{d}" fill="{color}"/>{til}', w


def a_descriptor(cx, y, size, color, text="ÓTICA", tracking=0.5):
    items, w = NUN8.shape(text, size, tracking)
    d = NUN8.path(items, size, cx - w / 2, y)
    return f'<path d="{d}" fill="{color}"/>', w


def a_stacked(color, bg, box=None, glass=None):
    box = box or color
    glass = glass or bg
    S = 150
    wm, w = a_wordmark(0, 0, S, color)
    W = w
    sym = 230
    symH = sym * 200 / 240
    body = a_symbol(W / 2 - sym / 2, 0, sym, box, glass)
    base = symH + 44 + S * NUN.xh + S * 0.26   # espaço p/ til
    wm, w = a_wordmark(0, base, S, color)
    desc, dw = a_descriptor(W / 2, base + 62, 30, color)
    H = base + 62 + 6
    return svg(W, H, body + wm + desc, bg, pad=60), (W + 120, H + 120)


def a_horizontal(color, bg, box=None, glass=None):
    box = box or color
    glass = glass or bg
    S = 130
    sym = 175
    symH = sym * 200 / 240
    gap = 34
    wmx = sym + gap
    base = symH / 2 + S * NUN.xh / 2 + 4
    wm, w = a_wordmark(wmx, base, S, color)
    items, dwd = NUN8.shape("ÓTICA", 26, 0.5)
    d = NUN8.path(items, 26, wmx + 4, base + 52)
    descr = f'<path d="{d}" fill="{color}"/>'
    W = wmx + w
    H = symH
    body = a_symbol(0, 0, sym, box, glass) + wm + descr
    return svg(W, H + 38, body, bg, pad=50)


def a_symbol_svg(box, glass, bg=None, size=240):
    return svg(size, size * 200 / 240, a_symbol(0, 0, size, box, glass), bg, pad=0)


# ------------------------------------------------------------------ B · PREMIUM
FRA = Face("Fraunces.ttf", {"wght": 500, "opsz": 144, "SOFT": 0, "WONK": 0}, "fraunces500")


def b_glasses(cx, cy, scale, color, hair=1.0, side=1.0, bridge=True):
    """Óculos de fio com aros de traço modulado (grosso nas laterais, fino em cima/baixo),
    como o 'O' da serifa. hair/side ajustam a espessura para tamanhos menores."""
    R, off = 34, 47
    ts, tt = 5.4 * side, 1.7 * hair
    parts = []
    ring = ""
    for sx in (-1, 1):
        ox = cx + sx * off * scale
        Ro = R * scale
        rx_i, ry_i = (R - ts) * scale, (R - tt) * scale
        ring += (f"M{ox-Ro:.2f},{cy:.2f} a{Ro:.2f},{Ro:.2f} 0 1,0 {2*Ro:.2f},0 a{Ro:.2f},{Ro:.2f} 0 1,0 {-2*Ro:.2f},0 Z "
                 f"M{ox-rx_i:.2f},{cy:.2f} a{rx_i:.2f},{ry_i:.2f} 0 1,1 {2*rx_i:.2f},0 a{rx_i:.2f},{ry_i:.2f} 0 1,1 {-2*rx_i:.2f},0 Z ")
    parts.append(f'<path d="{ring}" fill="{color}" fill-rule="evenodd"/>')
    sw = tt * scale * 1.05
    by = cy - 12 * scale
    if bridge:
        parts.append(f'<path d="{wave(cx-19*scale, by, 38*scale, 5.2*scale)}" fill="none" stroke="{color}" stroke-width="{sw:.2f}" stroke-linecap="round"/>')
    for sx in (-1, 1):
        x0 = cx + sx * (off + math.sqrt(R * R - 144) - 1.5) * scale
        x1 = cx + sx * (off + R + 26) * scale
        x2 = cx + sx * (off + R + 33) * scale
        parts.append(f'<path d="M{x0:.2f},{by:.2f} L{x1:.2f},{by:.2f} Q{x2:.2f},{by:.2f} {x2:.2f},{by+9*scale:.2f}" fill="none" stroke="{color}" stroke-width="{sw:.2f}" stroke-linecap="round"/>')
    return "".join(parts)


def b_wordmark(x, y, size, color, accent=None, tracking=0.17):
    accent = accent or color
    items, w = FRA.shape("NOVA VISAO", size, tracking)
    d = FRA.path(items, size, x, y)
    a = FRA.bounds(items[8], size)
    cx = x + (a[0] + a[2]) / 2
    til_w = (a[2] - a[0]) * 0.62
    ty = y - FRA.cap * size - size * 0.115
    til = (f'<path d="{wave(cx - til_w/2, ty, til_w, size*0.045)}" fill="none" stroke="{accent}" '
           f'stroke-width="{size*0.030:.2f}" stroke-linecap="round"/>')
    return f'<path d="{d}" fill="{color}"/>{til}', w


def b_descriptor(cx, y, size, color, total_w, accent=None):
    items, w = FRA.shape("ÓTICA", size, 0.55)
    d = FRA.path(items, size, cx - w / 2, y)
    gap = size * 1.1
    lw = (total_w - w) / 2 - gap
    hair = max(1.6, size * 0.06)
    l1 = f'<path d="M{cx - w/2 - gap - lw:.2f},{y - size*0.33:.2f} H{cx - w/2 - gap:.2f} M{cx + w/2 + gap:.2f},{y - size*0.33:.2f} H{cx + w/2 + gap + lw:.2f}" stroke="{color}" stroke-width="{hair:.2f}" stroke-linecap="butt"/>'
    return f'<path d="{d}" fill="{color}"/>{l1}'


def b_stacked(color, bg, accent=None):
    accent = accent or color
    S = 100
    wm_items, W = FRA.shape("NOVA VISAO", S, 0.17)
    scale = 1.75
    gy = 130
    glasses = b_glasses(W / 2, gy, scale, accent)
    base = gy + 34 * scale + 36 + FRA.cap * S + S * 0.10
    wm, w = b_wordmark(0, base, S, color, accent)
    desc = b_descriptor(W / 2, base + 70, 26, color, W)
    H = base + 76
    return svg(W, H, glasses + wm + desc, bg, pad=70)


def b_horizontal(color, bg, accent=None):
    accent = accent or color
    S = 100
    capH = FRA.cap * S
    scale = 1.2
    gw = (47 + 34 + 33) * 2 * scale
    cy = capH * 0.5 + 6
    glasses = b_glasses(gw / 2, cy, scale, accent, hair=1.1, side=1.05)
    base = cy + capH / 2
    wmx = gw + 40
    wm, w = b_wordmark(wmx, base, S, color, accent)
    desc = b_descriptor(wmx + w / 2, base + 62, 22, color, w)
    W = wmx + w
    return svg(W, base + 70, glasses + wm + desc, bg, pad=70)


def b_symbol_icon(box, glass, size=240, rx=66):
    """Versão reduzida: óculos mais encorpado dentro do contêiner, para avatar/favicon/gravação."""
    k = size / 240
    g = b_glasses(120, 124, 0.8, glass, hair=2.3, side=1.4)
    return svg(240, 240, f'<rect width="240" height="240" rx="{rx}" fill="{box}"/><g transform="translate(0,0)">{g}</g>')


def b_glasses_svg(color, bg=None):
    g = b_glasses(150, 80, 1.5, color)
    return svg(300, 160, g, bg, pad=40)


# ------------------------------------------------------------------ exportar
files = {}
a_s_w, _ = a_stacked(ORANGE, WHITE)
files["A-principal-laranja.svg"] = a_s_w
files["A-principal-branco-sobre-laranja.svg"] = a_stacked(WHITE, ORANGE, box=WHITE, glass=ORANGE)[0]
files["A-horizontal-laranja.svg"] = a_horizontal(ORANGE, WHITE)
files["A-horizontal-branco-sobre-laranja.svg"] = a_horizontal(WHITE, ORANGE, box=WHITE, glass=ORANGE)
files["A-simbolo-laranja.svg"] = a_symbol_svg(ORANGE, WHITE)
files["A-simbolo-branco.svg"] = a_symbol_svg(WHITE, ORANGE)
files["B-principal-laranja.svg"] = b_stacked(ORANGE, WHITE)
files["B-principal-branco-sobre-laranja.svg"] = b_stacked(WHITE, ORANGE)
files["B-principal-cafe-com-laranja.svg"] = b_stacked(CAFE, WHITE, accent=ORANGE)
files["B-horizontal-laranja.svg"] = b_horizontal(ORANGE, WHITE)
files["B-horizontal-branco-sobre-laranja.svg"] = b_horizontal(WHITE, ORANGE)
files["B-horizontal-cafe-com-laranja.svg"] = b_horizontal(CAFE, WHITE, accent=ORANGE)
files["B-oculos-laranja.svg"] = b_glasses_svg(ORANGE)
files["B-icone-reduzido.svg"] = b_symbol_icon(ORANGE, WHITE)

for n, s in files.items():
    open(os.path.join(OUT, "svg", n), "w").write(s)
print("ok", len(files))
