"""Converte texto em path SVG usando HarfBuzz (kerning real) + fontes variáveis.

Uso: shape("nova visao", font_path, size, weight, tracking) -> Run
"""
from dataclasses import dataclass, field
import uharfbuzz as hb
from fontTools.ttLib import TTFont

FONT_DIR = "/tmp/claude-0/-home-user-Claude/798b6a45-9182-5b29-a04a-aa3de179d4ec/scratchpad/fonts"


class _Pen:
    def __init__(self, sx, ox, oy):
        self.sx, self.ox, self.oy = sx, ox, oy
        self.d = []

    def _p(self, x, y):
        return f"{self.ox + x * self.sx:.2f} {self.oy - y * self.sx:.2f}"

    def moveTo(self, p): self.d.append("M" + self._p(*p))
    def lineTo(self, p): self.d.append("L" + self._p(*p))
    def qCurveTo(self, *pts):
        self.d.append("Q" + " ".join(self._p(*p) for p in pts))
    def curveTo(self, *pts):
        self.d.append("C" + " ".join(self._p(*p) for p in pts))
    def closePath(self): self.d.append("Z")
    def endPath(self): pass


@dataclass
class Glyph:
    ch: str
    x: float          # origem x (px)
    adv: float        # avanço (px)
    d: str            # path já posicionado


@dataclass
class Run:
    glyphs: list = field(default_factory=list)
    width: float = 0.0
    xheight: float = 0.0
    capheight: float = 0.0
    ascender: float = 0.0

    @property
    def d(self):
        return "".join(g.d for g in self.glyphs if g.d)


def _load(name, weight):
    path = f"{FONT_DIR}/{name}.ttf"
    blob = hb.Blob.from_file_path(path)
    face = hb.Face(blob)
    font = hb.Font(face)
    tt = TTFont(path)
    if "fvar" in tt:
        axes = {a.axisTag: a for a in tt["fvar"].axes}
        var = {}
        if "wght" in axes:
            var["wght"] = max(axes["wght"].minValue, min(axes["wght"].maxValue, weight))
        if "opsz" in axes:
            var["opsz"] = axes["opsz"].defaultValue
        font.set_variations(var)
    return font, face, tt


def shape(text, name, size, weight=700, tracking=0.0, x=0.0, y=0.0, features=None, custom_adv=None):
    """tracking em em (ex.: 0.02). custom_adv: dict char->ajuste de avanço em em."""
    font, face, tt = _load(name, weight)
    upem = face.upem
    s = size / upem
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, features or {"kern": True, "liga": False})
    run = Run()
    os2 = tt["OS/2"]
    run.xheight = getattr(os2, "sxHeight", 0) * s
    run.capheight = getattr(os2, "sCapHeight", 0) * s
    run.ascender = tt["hhea"].ascent * s
    cx = x
    for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
        ch = text[info.cluster]
        pen = _Pen(s, cx + pos.x_offset * s, y - pos.y_offset * s)
        font.draw_glyph_with_pen(info.codepoint, pen)
        adv = pos.x_advance * s + tracking * size
        if custom_adv and ch in custom_adv:
            adv += custom_adv[ch] * size
        run.glyphs.append(Glyph(ch, cx, adv, "".join(pen.d)))
        cx += adv
    run.width = cx - x - tracking * size
    return run
