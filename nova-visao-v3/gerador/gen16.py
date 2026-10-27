import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import gen13 as g13
from gen13 import G as GL
from gen2 import COR, COR5, ORANGE, WHITE

OUT = "/home/user/Claude/nova-visao-v3"
SD = os.path.join(OUT, "sistema"); os.makedirs(SD, exist_ok=True)


def bbox(d):
    P = np.array([float(x) for x in re.findall(r"-?\d+\.?\d*", d)]).reshape(-1, 2)
    return P[:, 0].min(), P[:, 1].min(), P[:, 0].max(), P[:, 1].max()


GB = [bbox(g["d"]) for g in GL]

# (nome, caminho, caixa (x,y,w,h), largura do óculos em relação à caixa, deslocamento vertical do centro)
CONT = [
    ("Arco", "M0,860 V500 A500,500 0 0 1 1000,500 V860 Z", (0, 0, 1000, 860), 0.80, 0.585),
    ("Círculo", "M500,0 A500,500 0 1 1 500,1000 A500,500 0 1 1 500,0 Z", (0, 0, 1000, 1000), 0.76, 0.50),
    ("Quadrado arredondado", "M220,0 H780 Q1000,0 1000,220 V780 Q1000,1000 780,1000 H220 Q0,1000 0,780 V220 Q0,0 220,0 Z", (0, 0, 1000, 1000), 0.78, 0.50),
    ("Oval", "M500,0 A500,380 0 1 1 500,760 A500,380 0 1 1 500,0 Z", (0, 0, 1000, 760), 0.74, 0.50),
    ("Olho (lente)", "M0,300 C250,-60 950,-60 1200,300 C950,660 250,660 0,300 Z", (0, 40, 1200, 520), 0.62, 0.50),
    ("Pílula", "M350,0 H950 A350,350 0 0 1 950,700 H350 A350,350 0 0 1 350,0 Z", (0, 0, 1300, 700), 0.62, 0.50),
    ("Folha", "M500,0 H940 Q1000,0 1000,60 V500 A500,500 0 0 1 500,1000 H60 Q0,1000 0,940 V500 A500,500 0 0 1 500,0 Z", (0, 0, 1000, 1000), 0.76, 0.50),
    ("Arco com onda", "M0,880 V500 A500,500 0 0 1 1000,500 V860 C860,930 720,820 520,870 C360,910 190,950 0,880 Z", (0, 0, 1000, 930), 0.80, 0.58),
]


def tile(ci, gi, cont_fill, glass_fill, size_w=None):
    name, d, (bx, by, bw, bh), fw, cy = CONT[ci]
    x0, y0, x1, y1 = GB[gi]
    gw, gh = x1 - x0, y1 - y0
    s = bw * fw / gw
    cxm = bx + bw / 2
    cym = by + bh * cy
    gl = (f'<g transform="translate({cxm:.1f},{cym:.1f}) scale({s:.4f}) translate({-(x0+x1)/2:.2f},{-(y0+y1)/2:.2f})">'
          f'<path d="{GL[gi]["d"]}" fill="{glass_fill}" fill-rule="evenodd"/></g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{bx} {by} {bw} {bh}"><defs><clipPath id="cp{ci}{gi}{abs(hash(cont_fill))%999}"><path d="{d}"/></clipPath></defs>'
            f'<path d="{d}" fill="{cont_fill}"/>{gl}</svg>')


def prem_h(gi, arch_bg, arch_fg, text, page_bg, pad=60):
    S = 100
    items, W = COR.shape("NOVA VISÃO", S, 0.14)
    cap = COR.cap * S
    ah = cap * 3.1
    aw = ah * GL[gi]["w"] / GL[gi]["h"]
    wx = aw + 54
    its, w5 = COR5.shape("ÓTICA", 25, 0.62)
    desc_off = 62
    block = cap + desc_off + 6
    base = ah / 2 - block / 2 + cap
    wm = f'<path d="{COR.path(items, S, wx, base)}" fill="{text}"/>'
    d5 = COR5.path(its, 25, wx + W / 2 - w5 / 2, base + desc_off)
    lw = (W - w5) / 2 - 25
    ly = base + desc_off - COR5.cap * 25 * 0.5
    rules = f'<path d="M{wx:.2f},{ly:.2f} H{wx+lw:.2f} M{wx+W-lw:.2f},{ly:.2f} H{wx+W:.2f}" stroke="{text}" stroke-width="1.8"/>'
    w, h = GL[gi]["w"], GL[gi]["h"]
    r = w / 2
    sym = (f'<svg x="0" y="0" width="{aw:.1f}" height="{ah:.1f}" viewBox="0 0 {w} {h}"><path d="M0,{h} V{r} A{r},{r} 0 0 1 {w},{r} V{h} Z" fill="{arch_bg}"/>'
           f'<path d="{GL[gi]["d"]}" fill="{arch_fg}" fill-rule="evenodd"/></svg>')
    TW = wx + W
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {TW+2*pad:.1f} {ah+2*pad:.1f}"><rect x="{-pad}" y="{-pad}" width="{TW+2*pad:.1f}" height="{ah+2*pad:.1f}" fill="{page_bg}"/>'
            f'{sym}{wm}<path d="{d5}" fill="{text}"/>{rules}</svg>')


if __name__ == "__main__":
    for gi, tag in ((0, "angulo1"), (2, "angulo2")):
        open(os.path.join(SD, f"premium-horizontal-laranja-{tag}.svg"), "w").write(prem_h(gi, ORANGE, WHITE, ORANGE, WHITE))
        open(os.path.join(SD, f"premium-horizontal-branco-sobre-laranja-{tag}.svg"), "w").write(prem_h(gi, WHITE, ORANGE, WHITE, ORANGE))
    css = """*{box-sizing:border-box;margin:0}body{background:#FAF6F1;color:#2B1A12;font:16px/1.45 'Inter',system-ui,sans-serif;padding:48px;width:1700px}
h1{font-size:40px;letter-spacing:-.02em;margin-bottom:6px}.sub{color:#6B5B52;font-size:19px;margin-bottom:22px;max-width:1250px}
h2{font-size:28px;margin:34px 0 4px}.hint{color:#6B5B52;margin-bottom:14px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}.card{background:#fff;border:1px solid #E6DDD3;border-radius:16px;padding:12px}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:8px}.pair .a svg,.pair .b svg{width:100%;height:170px;display:block}
.b{background:#FF5F00;border-radius:10px;padding:8px;display:grid;place-items:center}.a{padding:8px;display:grid;place-items:center}
.card b{display:block;margin:8px 0 2px;font-size:17px}.card span{color:#6B5B52;font-size:14px}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:16px}.lk svg{width:100%;display:block;border-radius:8px}"""
    notes = {"Arco": "Janela de vitrine. É o P4 atual.", "Círculo": "Selo. Elegante, mas muito comum.", "Quadrado arredondado": "Ícone de app. É o mesmo do popular.",
             "Oval": "Espelho. Macio e discreto.", "Olho (lente)": "Em forma de olho. Conceitual.", "Pílula": "Horizontal e moderna. Boa para rodapé.",
             "Folha": "Cantos opostos diferentes. Dá movimento.", "Arco com onda": "Topo de janela e base em onda, como o popular. Liga as duas versões."}
    cards = ""
    for ci, c in enumerate(CONT):
        a = tile(ci, 0, ORANGE, WHITE); b = tile(ci, 0, WHITE, ORANGE)
        cards += f'<div class="card"><div class="pair"><div class="a">{a}</div><div class="b">{b}</div></div><b>{c[0]}</b><span>{notes[c[0]]}</span></div>'
    html = (f'<!doctype html><meta charset="utf-8"><style>{css}</style><body><h1>Premium P4 · só branco e laranja</h1>'
            f'<p class="sub">O café saiu. Cada container aparece em laranja com o óculos branco e em branco com o óculos laranja, sobre o fundo laranja.</p>'
            f'<h2>Outros containers para o óculos</h2><p class="hint">O mesmo óculos do P4 dentro de 8 formas.</p><div class="grid">{cards}</div>'
            f'<h2>Logo principal horizontal, em duas cores</h2><p class="hint">Arco à esquerda, nome à direita. Em cima, no fundo branco; embaixo, no fundo laranja.</p>'
            f'<div class="g2 lk"><div class="card">{prem_h(0, ORANGE, WHITE, ORANGE, WHITE)}</div><div class="card">{prem_h(2, ORANGE, WHITE, ORANGE, WHITE)}</div>'
            f'<div class="card" style="background:#FF5F00">{prem_h(0, WHITE, ORANGE, WHITE, ORANGE)}</div><div class="card" style="background:#FF5F00">{prem_h(2, WHITE, ORANGE, WHITE, ORANGE)}</div></div></body>')
    open(os.path.join(OUT, "premium-containers.html"), "w").write(html)
    print("ok")
