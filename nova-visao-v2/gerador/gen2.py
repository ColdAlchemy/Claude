import math, os, json
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

SCR = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(SCR, "fonts")
OUT = "/home/user/Claude/nova-visao-v2"
os.makedirs(os.path.join(OUT, "svg"), exist_ok=True)

ORANGE = "#FF5F00"
WHITE = "#FFFFFF"
CAFE = "#2B1A12"
f2 = lambda v: f"{v:.2f}"


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
        self.cap = os2.sCapHeight / self.upm

    def shape(self, text, size, tracking=0.0):
        buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
        hb.shape(self.hbfont, buf, {"kern": True, "liga": False})
        s = size / self.upm
        x = 0.0; items = []
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            items.append(dict(name=self.order[info.codepoint], x=x + pos.x_offset * s))
            x += pos.x_advance * s + tracking * size
        return items, x - tracking * size

    def path(self, items, size, ox, oy):
        s = size / self.upm
        pen = SVGPathPen(self.gs, ntos=f2)
        for it in items:
            self.gs[it["name"]].draw(TransformPen(pen, (s, 0, 0, -s, ox + it["x"], oy)))
        return pen.getCommands()


def svg(w, h, body, bg=None, pad=0):
    r = f'<rect x="{-pad}" y="{-pad}" width="{w+2*pad:.1f}" height="{h+2*pad:.1f}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {w+2*pad:.1f} {h+2*pad:.1f}" '
            f'role="img" aria-label="Ótica Nova Visão">{r}{body}</svg>')


def rrect(x0, y0, x1, y1, tl, tr, br, bl):
    """Retângulo com raios de canto independentes (sentido horário)."""
    return (f"M{x0+tl},{y0} H{x1-tr} A{tr},{tr} 0 0 1 {x1},{y0+tr} V{y1-br} A{br},{br} 0 0 1 {x1-br},{y1} "
            f"H{x0+bl} A{bl},{bl} 0 0 1 {x0},{y1-bl} V{y0+tl} A{tl},{tl} 0 0 1 {x0+tl},{y0} Z")


# ============================================================ A · SÍMBOLO REALISTA
def a_frame(color, bg):
    """Armação de acetato vista de frente (caixa 240 de largura, centro em y=100):
    aro mais grosso em cima que embaixo, ponte em arco, ponteiras com rebite e reflexo nas lentes."""
    p = []
    def lens(mir):
        X = (lambda x0, x1: (x0, x1)) if not mir else (lambda x0, x1: (240 - x1, 240 - x0))
        ox0, ox1 = X(24, 108)
        ix0, ix1 = X(34, 98)
        if not mir:
            return rrect(ox0, 62, ox1, 138, 38, 33, 38, 40) + " " + rrect(ix0, 74, ix1, 130, 28, 24, 30, 32)
        return rrect(ox0, 62, ox1, 138, 33, 38, 40, 38) + " " + rrect(ix0, 74, ix1, 130, 24, 28, 32, 30)
    p.append(f'<path d="{lens(False)} {lens(True)}" fill="{color}" fill-rule="evenodd"/>')
    # ponte em arco (chave)
    p.append(f'<path d="M100,102 L100,90 C100,64 140,64 140,90 L140,102 L132,102 L132,90 C132,78 108,78 108,90 L108,102 Z" fill="{color}"/>')
    # ponteiras com rebite
    p.append(f'<rect x="12" y="72" width="26" height="22" rx="6" fill="{color}"/><circle cx="19.5" cy="83" r="2.9" fill="{bg}"/>')
    p.append(f'<rect x="202" y="72" width="26" height="22" rx="6" fill="{color}"/><circle cx="220.5" cy="83" r="2.9" fill="{bg}"/>')
    # reflexo nas lentes: duas faixas paralelas
    g = []
    for mir in (False, True):
        for (x1, y1, x2, y2, w) in ((48, 112, 64, 87, 6.4), (71, 104, 78, 93, 4.8)):
            if mir:
                x1, x2 = 240 - x1, 240 - x2
            g.append(f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{color}" stroke-width="{w}" stroke-linecap="round" fill="none"/>')
    p.append("".join(g))
    return "".join(p)


def a_symbol(x, y, size, box, glass):
    k = size / 240
    return (f'<g transform="translate({x},{y}) scale({k:.4f})"><rect width="240" height="176" rx="54" fill="{box}"/>'
            f'<g transform="translate(120 88) scale(0.96) translate(-120 -100)">{a_frame(glass, box)}</g></g>')


def a_symbol_svg(box, glass, bg=None, size=240):
    return svg(size, size * 176 / 240, a_symbol(0, 0, size, box, glass), bg)


# ---- tipografia da versão original (vetorizada da sua imagem)
TA = json.load(open(os.path.join(SCR, "traced_A.json")))
WM_W, WM_H, WM_BASE = TA["wordmark"]["w"], TA["wordmark"]["h"], 158   # baseline dentro do recorte


def a_wordmark(x, y_top, scale, color):
    return f'<path d="{TA["wordmark"]["d"]}" transform="translate({x},{y_top}) scale({scale})" fill="{color}" fill-rule="evenodd"/>'


def a_descriptor(x, y_top, scale, color):
    return f'<path d="{TA["descriptor"]["d"]}" transform="translate({x},{y_top}) scale({scale})" fill="{color}" fill-rule="evenodd"/>'


def a_stacked(color, bg, box=None, glass=None):
    box = box or color; glass = glass or bg
    ws = 0.62
    W = WM_W * ws
    cw = 250
    ch = cw * 176 / 240
    sym = a_symbol(W / 2 - cw / 2, 0, cw, box, glass)
    top = ch + 40
    wm = a_wordmark(0, top, ws, color)
    ds = 0.74
    dx = W / 2 - TA["descriptor"]["w"] * ds / 2
    dy = top + WM_H * ws + 22
    desc = a_descriptor(dx, dy, ds, color)
    return svg(W, dy + TA["descriptor"]["h"] * ds, sym + wm + desc, bg, pad=60)


def a_horizontal(color, bg, box=None, glass=None):
    box = box or color; glass = glass or bg
    ws = 0.62
    base = WM_BASE * ws
    ch = base
    cw = ch * 240 / 176
    gap = 34
    wx = cw + gap
    sym = a_symbol(0, 0, cw, box, glass)
    wm = a_wordmark(wx, 0, ws, color)
    ds = 0.62
    desc = a_descriptor(wx + 4, WM_H * ws + 16, ds, color)
    return svg(wx + WM_W * ws, WM_H * ws + 16 + TA["descriptor"]["h"] * ds, sym + wm + desc, bg, pad=50)


# ============================================================ B · SÍMBOLO DE FIO REALISTA
COR = Face("Cormorant.ttf", {"wght": 600}, "cormorant600")
COR5 = Face("Cormorant.ttf", {"wght": 500}, "cormorant500")


def b_glasses(color, bg=None, sw=3.4, detail=True, temples=True):
    """Óculos de fio redondo, 300x150: aros, ponte em arco, plaquetas com haste, ponteiras com dobradiça,
    hastes com ponta curvada e reflexo nas lentes. Retorna (grupo, largura, altura)."""
    cx1, cx2, cy, R = 88, 212, 78, 42
    p = []
    mk = lambda w: f'fill="none" stroke="{color}" stroke-width="{w:.2f}" stroke-linecap="round" stroke-linejoin="round"'
    stroke = mk(sw)
    p.append(f'<circle cx="{cx1}" cy="{cy}" r="{R}" {stroke}/><circle cx="{cx2}" cy="{cy}" r="{R}" {stroke}/>')
    # ponte em arco
    a = math.radians(-40)
    x1, y1 = cx1 + R * math.cos(a), cy + R * math.sin(a)
    x2 = 300 - x1
    p.append(f'<path d="M{f2(x1)},{f2(y1)} C{f2(x1+9)},{f2(y1-19)} {f2(x2-9)},{f2(y1-19)} {f2(x2)},{f2(y1)}" {stroke}/>')
    for sx, cx in ((1, cx1), (-1, cx2)):
        # plaqueta de nariz (dentro da lente, encostada no aro)
        px, py = cx + sx * (R - 8.2), cy + 17
        p.append(f'<ellipse cx="{f2(px)}" cy="{f2(py)}" rx="{sw*0.78:.2f}" ry="{sw*2.2:.2f}" fill="{color}" transform="rotate({26*sx} {f2(px)} {f2(py)})"/>')
        if temples:
            # dobradiça e haste com ponta curvada
            ang2 = math.radians(-157)
            ex, ey = cx + sx * (-1) * R * math.cos(math.radians(23)) , cy + R * math.sin(ang2)
            ex = cx - sx * R * math.cos(math.radians(23)) ; ey = cy - R * math.sin(math.radians(23))
            hx0, hx1 = ex - sx * 1, ex - sx * 11
            p.append(f'<rect x="{f2(min(hx0,hx1))}" y="{f2(ey-3.4)}" width="10" height="6.8" rx="1.8" fill="{color}"/>')
            tx = ex - sx * 11
            p.append(f'<path d="M{f2(tx)},{f2(ey)} L{f2(tx - sx*28)},{f2(ey-3)} Q{f2(tx - sx*36)},{f2(ey-3.6)} {f2(tx - sx*37)},{f2(ey+7)}" {stroke}/>')
        if detail:
            # reflexo (arcos na lente)
            for (a0, a1, rr) in ((205, 238, 33), (247, 262, 33)):
                r0, r1 = math.radians(a0), math.radians(a1)
                gx0, gy0 = cx + rr * math.cos(r0) * sx if sx == 1 else cx - rr * math.cos(r0), cy + rr * math.sin(r0)
                gx1, gy1 = (cx + rr * math.cos(r1)) if sx == 1 else cx - rr * math.cos(r1), cy + rr * math.sin(r1)
                sweep = 1 if sx == 1 else 0
                p.append(f'<path d="M{f2(gx0)},{f2(gy0)} A{rr},{rr} 0 0 {sweep} {f2(gx1)},{f2(gy1)}" fill="none" stroke="{color}" stroke-width="{sw*0.75:.2f}" stroke-linecap="round"/>')
    return "".join(p)


def b_glasses_svg(color, bg=None):
    return svg(300, 150, b_glasses(color), bg, pad=24)


def b_icon(box, glass, size=240):
    """Ícone reduzido: sem hastes nem reflexo, traço mais grosso, dentro do contêiner."""
    g = b_glasses(glass, sw=6.2, detail=False, temples=False)
    return svg(240, 176, f'<rect width="240" height="176" rx="54" fill="{box}"/>'
                         f'<g transform="translate(120 88) scale(0.72) translate(-150 -78)">{g}</g>')


def b_wordmark(x, y, size, color, tracking=0.14):
    items, w = COR.shape("NOVA VISÃO", size, tracking)
    return f'<path d="{COR.path(items, size, x, y)}" fill="{color}"/>', w


def b_descriptor(cx, y, size, color, total_w):
    items, w = COR5.shape("ÓTICA", size, 0.62)
    d = COR5.path(items, size, cx - w / 2, y)
    gap = size * 1.0
    lw = (total_w - w) / 2 - gap
    ly = y - COR5.cap * size * 0.5
    hair = max(1.6, size * 0.07)
    rules = (f'<path d="M{f2(cx - w/2 - gap - lw)},{f2(ly)} H{f2(cx - w/2 - gap)} M{f2(cx + w/2 + gap)},{f2(ly)} H{f2(cx + w/2 + gap + lw)}" '
             f'stroke="{color}" stroke-width="{hair:.2f}"/>')
    return f'<path d="{d}" fill="{color}"/>{rules}'


def b_stacked(color, bg, accent=None):
    accent = accent or color
    S = 100
    items, W = COR.shape("NOVA VISÃO", S, 0.14)
    gs = W * 0.50 / 300
    gw = 300 * gs
    gl = f'<g transform="translate({f2(W/2 - gw/2)},0) scale({gs:.4f})">{b_glasses(accent)}</g>'
    gh = 150 * gs
    base = gh + 40 + COR.cap * S
    wm, _ = b_wordmark(0, base, S, color)
    desc = b_descriptor(W / 2, base + 76, 27, color, W)
    return svg(W, base + 82, gl + wm + desc, bg, pad=70)


def b_horizontal(color, bg, accent=None):
    accent = accent or color
    S = 100
    capH = COR.cap * S
    gs = (capH * 1.9) / 150
    gw = 300 * gs
    gl = f'<g transform="translate(0,{f2(0)}) scale({gs:.4f})">{b_glasses(accent, sw=3.8, detail=False)}</g>'
    base = 150 * gs / 2 + capH / 2
    wx = gw + 34
    wm, w = b_wordmark(wx, base, S, color)
    desc = b_descriptor(wx + w / 2, base + 66, 22, color, w)
    return svg(wx + w, base + 72, gl + wm + desc, bg, pad=70)


# ============================================================ exportar
def build_files():
    F = {}
    F["A-principal-laranja.svg"] = a_stacked(ORANGE, WHITE)
    F["A-principal-branco-sobre-laranja.svg"] = a_stacked(WHITE, ORANGE, box=WHITE, glass=ORANGE)
    F["A-horizontal-laranja.svg"] = a_horizontal(ORANGE, WHITE)
    F["A-horizontal-branco-sobre-laranja.svg"] = a_horizontal(WHITE, ORANGE, box=WHITE, glass=ORANGE)
    F["A-simbolo-laranja.svg"] = a_symbol_svg(ORANGE, WHITE)
    F["A-simbolo-branco.svg"] = a_symbol_svg(WHITE, ORANGE)
    F["B-principal-laranja.svg"] = b_stacked(ORANGE, WHITE)
    F["B-principal-branco-sobre-laranja.svg"] = b_stacked(WHITE, ORANGE)
    F["B-principal-cafe-com-laranja.svg"] = b_stacked(CAFE, WHITE, accent=ORANGE)
    F["B-horizontal-laranja.svg"] = b_horizontal(ORANGE, WHITE)
    F["B-horizontal-cafe-com-laranja.svg"] = b_horizontal(CAFE, WHITE, accent=ORANGE)
    F["B-oculos-laranja.svg"] = b_glasses_svg(ORANGE)
    F["B-icone-reduzido.svg"] = b_icon(ORANGE, WHITE)
    return F


if __name__ == "__main__":
    for n, s in build_files().items():
        open(os.path.join(OUT, "svg", n), "w").write(s)
    print("ok")
