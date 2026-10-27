import os, json, math, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen2 import Face, COR, COR5, TA, WM_W, WM_H, WM_BASE, ORANGE, WHITE, CAFE, f2, svg

OUT = "/home/user/Claude/nova-visao-v3"
os.makedirs(OUT, exist_ok=True)


def rpoly(pts, r):
    """Polígono fechado com cantos arredondados (curvas quadráticas)."""
    n = len(pts)
    d = ""
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
        def toward(a, b, dist):
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            t = min(dist, L / 2) / L
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        a = toward(p1, p0, r)
        b = toward(p1, p2, r)
        d += ("M" if i == 0 else "L") + f"{a[0]:.2f},{a[1]:.2f} Q{p1[0]:.2f},{p1[1]:.2f} {b[0]:.2f},{b[1]:.2f} "
    return d + "Z"


def wave(x0, y0, w, amp):
    return (f"M{x0:.2f},{y0:.2f} C{x0+w*.17:.2f},{y0-amp*1.33:.2f} {x0+w*.33:.2f},{y0-amp*1.33:.2f} {x0+w*.5:.2f},{y0:.2f} "
            f"S{x0+w*.83:.2f},{y0+amp*1.33:.2f} {x0+w:.2f},{y0:.2f}")


def mirror_pts(pts):
    return [(200 - x, y) for x, y in pts][::-1]


def S(d, w, col, fill="none"):
    return f'<path d="{d}" fill="{fill}" stroke="{col}" stroke-width="{w:.2f}" stroke-linecap="round" stroke-linejoin="round"/>'


# ---------------------------------------------------------------- 4 silhuetas (caixa 200x200)
def c_til(sw, col):
    """1 · Til: lentes quadradas arredondadas ligadas por uma onda, a mesma do til do ã."""
    L = [(28, 74), (78, 74), (78, 126), (28, 126)]
    p = S(rpoly(L, 22), sw, col) + S(rpoly(mirror_pts(L), 22), sw, col)
    p += S(wave(80, 100, 40, 9), sw * 0.78, col)
    p += S("M28,92 L12,92", sw * 0.78, col) + S("M172,92 L188,92", sw * 0.78, col)
    return p


def c_lua(sw, col):
    """2 · Meia-lua: lente reta em cima e redonda embaixo, barra única no topo."""
    def lens(m):
        x0, x1 = (24, 84) if not m else (116, 176)
        return f"M{x0+9},76 H{x1-9} Q{x1},76 {x1},85 V92 A{(x1-x0)/2:.1f},{(x1-x0)/2:.1f} 0 0 1 {x0},92 V85 Q{x0},76 {x0+9},76 Z"
    p = S(lens(False), sw, col) + S(lens(True), sw, col)
    p += S("M84,76 H116", sw, col)
    p += S("M24,76 L10,76", sw * 0.82, col) + S("M176,76 L190,76", sw * 0.82, col)
    return f'<g transform="translate(0,6)">{p}</g>'


def c_brilho(sw, col):
    """3 · Brilho: aros redondos com um corte no canto, que é o reflexo na lente."""
    r = 27
    def ring(cx, a0, a1):
        p0 = (cx + r * math.cos(math.radians(a0)), 100 + r * math.sin(math.radians(a0)))
        p1 = (cx + r * math.cos(math.radians(a1)), 100 + r * math.sin(math.radians(a1)))
        return f'<path d="M{p0[0]:.2f},{p0[1]:.2f} A{r},{r} 0 1 1 {p1[0]:.2f},{p1[1]:.2f}" fill="none" stroke="{col}" stroke-width="{sw:.2f}" stroke-linecap="butt"/>'
    p = ring(54, 244, 566) + ring(146, 334, 656)
    p += S(wave(85, 90, 30, 6), sw * 0.8, col)
    p += S("M27,90 L12,90", sw * 0.8, col) + S("M173,90 L188,90", sw * 0.8, col)
    return p


def c_olho(sw, col):
    """4 · Olho: lentes em amêndoa com pupila. Óculos e olho na mesma forma."""
    def lens(m):
        cx = 56 if not m else 144
        d = f"M{cx-34},100 C{cx-18},64 {cx+18},64 {cx+34},100 C{cx+18},136 {cx-18},136 {cx-34},100 Z"
        return S(d, sw, col) + f'<circle cx="{cx}" cy="100" r="{sw*0.62:.2f}" fill="{col}"/>'
    p = lens(False) + lens(True)
    p += S("M90,98 Q100,92 110,98", sw * 0.8, col)
    p += S("M22,100 L10,100", sw * 0.8, col) + S("M178,100 L190,100", sw * 0.8, col)
    return p


CONCEPTS = [
    ("1", "Til", "A onda do til do “ã” vira a ponte do óculos.", c_til),
    ("2", "Meia-lua", "Lente reta em cima e redonda embaixo. Parece um sorriso.", c_lua),
    ("3", "Olho", "Lente em amêndoa com pupila: óculos e olho numa forma só.", c_olho),
]


def symbol(fn, sw=17, box=ORANGE, glass=WHITE, rx=48):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect width="200" height="200" rx="{rx}" fill="{box}"/>'
            f'<g>{fn(sw, glass)}</g></svg>')


def bare(fn, sw, col, w=200):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 30 200 140">{fn(sw, col)}</svg>'


def a_lockup(fn, color=ORANGE, bg=WHITE, box=None, glass=None, sw=17):
    box = box or color
    glass = glass or bg
    ws = 0.5
    ch = WM_BASE * ws * 1.30
    cw = ch
    wx = cw + 28
    sym = f'<g transform="scale({ch/200:.4f})"><rect width="200" height="200" rx="48" fill="{box}"/>{fn(sw, glass)}</g>'
    wy = ch - WM_BASE * ws
    wm = f'<path d="{TA["wordmark"]["d"]}" transform="translate({wx},{wy:.2f}) scale({ws})" fill="{color}" fill-rule="evenodd"/>'
    W = wx + WM_W * ws
    return svg(W, ch, sym + wm, bg, pad=22)


def b_lockup(fn, color=ORANGE, bg=WHITE, accent=None, sw=8):
    accent = accent or color
    S_ = 100
    items, W = COR.shape("NOVA VISÃO", S_, 0.14)
    gs = W * 0.46 / 200
    gh = 90 * gs
    gl = f'<g transform="translate({W/2 - 100*gs:.2f},{-55*gs:.2f}) scale({gs:.4f})">{fn(sw, accent)}</g>'
    base = gh + 34 + COR.cap * S_
    wm = f'<path d="{COR.path(items, S_, 0, base)}" fill="{color}"/>'
    its, w5 = COR5.shape("ÓTICA", 27, 0.62)
    d5 = COR5.path(its, 27, W / 2 - w5 / 2, base + 76)
    gap = 27
    lw = (W - w5) / 2 - gap
    ly = base + 76 - COR5.cap * 27 * 0.5
    rules = (f'<path d="M0,{ly:.2f} H{lw:.2f} M{W-lw:.2f},{ly:.2f} H{W:.2f}" stroke="{color}" stroke-width="1.8"/>')
    return svg(W, base + 82, gl + wm + f'<path d="{d5}" fill="{color}"/>' + rules, bg, pad=50)


def b_lockup_h(fn, color=ORANGE, bg=WHITE, box=ORANGE, glass=WHITE, sw=15):
    S_ = 100
    items, W = COR.shape("NOVA VISÃO", S_, 0.14)
    capH = COR.cap * S_
    ch = capH * 2.5
    sym = f'<g transform="scale({ch/200:.4f})"><rect width="200" height="200" rx="48" fill="{box}"/>{fn(sw, glass)}</g>'
    wx = ch + 36
    base = ch / 2 - 4 + capH / 2 - 6
    wm = f'<path d="{COR.path(items, S_, wx, base)}" fill="{color}"/>'
    its, w5 = COR5.shape("ÓTICA", 24, 0.62)
    d5 = COR5.path(its, 24, wx + W / 2 - w5 / 2, base + 52)
    gap = 24
    lw = (W - w5) / 2 - gap
    ly = base + 52 - COR5.cap * 24 * 0.5
    rules = f'<path d="M{wx:.2f},{ly:.2f} H{wx+lw:.2f} M{wx+W-lw:.2f},{ly:.2f} H{wx+W:.2f}" stroke="{color}" stroke-width="1.8"/>'
    return svg(wx + W, ch, sym + wm + f'<path d="{d5}" fill="{color}"/>' + rules, bg, pad=40)


if __name__ == "__main__":
    css = """
    *{box-sizing:border-box;margin:0}
    body{background:#FAF6F1;color:#2B1A12;font:16px/1.45 'Inter',system-ui,sans-serif;padding:56px 56px 64px;width:1712px}
    h1{font-size:44px;letter-spacing:-.02em;margin-bottom:6px}
    .sub{color:#6B5B52;font-size:19px;margin-bottom:36px;max-width:1100px}
    .grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
    .card{background:#fff;border:1px solid #E6DDD3;border-radius:20px;padding:20px}
    .card h2{font-size:22px;margin:14px 0 4px}
    .card h2 span{color:#FF5F00;margin-right:8px}
    .card p{color:#6B5B52;font-size:15px;min-height:44px}
    .big svg{width:100%;display:block}
    .row{margin-top:14px;border-top:1px solid #EFE7DE;padding-top:14px}
    .row svg{display:block;width:100%}
    .sm{display:flex;gap:14px;align-items:flex-end;margin-top:12px}
    .sm svg{display:block}
    .on{background:#FF5F00;border-radius:14px;overflow:hidden;margin-top:12px}
    """
    def card(i, n, desc, fn):
        big = symbol(fn)
        inv = symbol(fn, box=WHITE, glass=ORANGE)
        sm = "".join(f'<div style="width:{p}px">{symbol(fn)}</div>' for p in (64, 32, 16))
        return f'''<div class="card"><div class="big">{big}</div><h2><span>{i}</span>{n}</h2><p>{desc}</p>
        <div class="row">{a_lockup(fn)}</div>
        <div class="on">{a_lockup(fn, color=WHITE, bg=ORANGE, box=WHITE, glass=ORANGE)}</div>
        <div class="sm">{sm}</div></div>'''
    cards = "".join(card(*c) for c in CONCEPTS)
    html = f'<!doctype html><meta charset="utf-8"><style>{css}</style><body><h1>Nova Visão · três silhuetas</h1><p class="sub">Só a forma do óculos, sem detalhes desenhados. A personalidade está no formato, como na Diniz. A tipografia é a sua, da versão laranja.</p><div class="grid">{cards}</div></body>'
    open(os.path.join(OUT, "board-popular.html"), "w").write(html)

    css2 = css + ".card p{min-height:0}"
    def card2(i, n, desc, fn):
        return f'''<div class="card"><h2><span>{i}</span>{n}</h2><p>{desc}</p>
        <div class="row" style="border:0">{b_lockup(fn)}</div>
        <div class="row">{b_lockup(fn, color=CAFE, accent=ORANGE)}</div>
        <div class="row">{b_lockup_h(fn)}</div>
        <div class="row">{b_lockup_h(fn, color=CAFE, box=CAFE, glass=WHITE)}</div></div>'''
    cards2 = "".join(card2(*c) for c in CONCEPTS)
    html2 = f'<!doctype html><meta charset="utf-8"><style>{css2}</style><body><h1>Nova Visão · versão premium</h1><p class="sub">A mesma silhueta, mais leve, com a serifa Cormorant e o descritor entre fios. Duas versões por conceito: empilhada e horizontal com contêiner.</p><div class="grid">{cards2}</div></body>'
    open(os.path.join(OUT, "board-premium.html"), "w").write(html2)
    print("ok")
