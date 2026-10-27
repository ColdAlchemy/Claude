import os
from gen2 import *

css = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "css.txt")).read().replace("{{", "{").replace("}}", "}")
A_main = a_stacked(ORANGE, WHITE)
A_main_inv = a_stacked(WHITE, ORANGE, box=WHITE, glass=ORANGE)
A_hor = a_horizontal(ORANGE, WHITE)
A_hor_inv = a_horizontal(WHITE, ORANGE, box=WHITE, glass=ORANGE)
A_sym = a_symbol_svg(ORANGE, WHITE)
B_main = b_stacked(ORANGE, WHITE)
B_main_cafe = b_stacked(CAFE, WHITE, accent=ORANGE)
B_main_inv = b_stacked(WHITE, ORANGE)
B_hor = b_horizontal(ORANGE, WHITE)
B_hor_cafe = b_horizontal(CAFE, WHITE, accent=ORANGE)
B_icon = b_icon(ORANGE, WHITE)
B_glasses = b_glasses_svg(ORANGE, WHITE)


def sizes(svg_str):
    cells = "".join(f'<figure><div style="width:{p}px">{svg_str}</div><figcaption>{p}px</figcaption></figure>' for p in (128, 64, 32, 16))
    return f'<div class="sizes">{cells}</div>'


html = f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Nova Visão · rodada 13</title>
{css}
</head>
<body>
<main>
  <p class="eyebrow">Ótica Nova Visão · rodada 13</p>
  <h1>As suas versões, com óculos realista</h1>
  <p class="lede">Voltei para o que você anexou. A tipografia da A é a sua, vetorizada da imagem sem alterar as letras. A B usa a Cormorant da serifa original. O que refiz foi o símbolo, que agora é um óculos de verdade, com peças reais e não um ícone.</p>

  <section>
    <p class="eyebrow">Direção A · popular</p>
    <h2>Nova Visão, com armação de acetato</h2>
    <div class="grid g2" style="margin-top:20px">
      <div class="card">{A_main}<div class="cap">Principal · laranja sobre branco</div></div>
      <div class="card" style="background:#FF5F00">{A_main_inv}<div class="cap" style="background:#fff">Principal · branco sobre laranja</div></div>
    </div>
    <div class="grid g2" style="margin-top:12px">
      <div class="card">{A_hor}<div class="cap">Horizontal</div></div>
      <div class="card" style="background:#FF5F00">{A_hor_inv}<div class="cap" style="background:#fff">Horizontal · fachada</div></div>
    </div>
    <h3>Símbolo em tamanho real</h3>
    {sizes(A_sym)}
    <h3>O que o símbolo tem de óculos de verdade</h3>
    <ul class="change">
      <li><span class="n">1</span><div><b>Aro de acetato com espessura variável:</b> mais grosso em cima, mais fino embaixo, como numa armação real.</div></li>
      <li><span class="n">2</span><div><b>Lente em formato de óculos,</b> um quadrado arredondado de topo reto, e não um círculo.</div></li>
      <li><span class="n">3</span><div><b>Ponte em arco</b> entre as lentes e <b>ponteiras com rebite</b>, que são as peças que fazem alguém reconhecer uma armação.</div></li>
      <li><span class="n">4</span><div><b>Reflexo nas lentes:</b> duas faixas diagonais que dão a sensação de vidro. Podem sair em tamanhos muito pequenos.</div></li>
      <li><span class="n">5</span><div><b>Contêiner arredondado,</b> a lição que você tirou da Diniz, para a marca funcionar em avatar, favicon e haste.</div></li>
    </ul>
  </section>

  <section>
    <p class="eyebrow">Direção B · premium</p>
    <h2>Serifa e fio, com óculos de fio realista</h2>
    <div class="grid g2" style="margin-top:20px">
      <div class="card">{B_main}<div class="cap">Principal · laranja</div></div>
      <div class="card">{B_main_cafe}<div class="cap">Principal · café com laranja de acento</div></div>
    </div>
    <div class="grid g2" style="margin-top:12px">
      <div class="card" style="background:#FF5F00">{B_main_inv}<div class="cap" style="background:#fff">Branco sobre laranja</div></div>
      <div class="card">{B_hor}{B_hor_cafe}<div class="cap">Horizontal · laranja e café com laranja</div></div>
    </div>
    <h3>O óculos sozinho e o ícone reduzido</h3>
    <div class="grid g2">
      <div class="card">{B_glasses}<div class="cap">O óculos de fio em detalhe</div></div>
      <div>{sizes(B_icon)}</div>
    </div>
    <h3>O que o símbolo tem de óculos de verdade</h3>
    <ul class="change">
      <li><span class="n">1</span><div><b>Aros de fio, ponte em arco e plaquetas de nariz</b> dentro das lentes, como num óculos panto.</div></li>
      <li><span class="n">2</span><div><b>Ponteiras com dobradiça</b> e hastes com a ponta curvada atrás da orelha.</div></li>
      <li><span class="n">3</span><div><b>Reflexo em arco</b> no canto de cada lente, que dá volume ao vidro.</div></li>
      <li><span class="n">4</span><div><b>Mais largo e com mais presença</b> que na versão original, para ter peso ao lado do nome.</div></li>
      <li><span class="n">5</span><div><b>Versão café com laranja:</b> o nome em tinta escura e o laranja só no óculos. Resolve o laranja fino que vibra no fundo branco.</div></li>
    </ul>
  </section>

  <section>
    <p class="eyebrow">Observações</p>
    <p class="risk"><b>A tipografia da A</b> foi vetorizada do seu JPG. Ela serve como base, mas antes de produzir vale ter o arquivo original das letras, para que as curvas saiam limpas. <b>O til e a ponte</b> estão como traço e precisam ser convertidos em contorno. <b>A Cormorant</b> é uma fonte pronta. Se quiser, o próximo passo é desenhar à mão detalhes nas letras da B, como o "V" ou o "Ã".</p>
  </section>
</main>
</body>
</html>
'''
open(os.path.join(OUT, "index.html"), "w").write(html)
print("ok")
