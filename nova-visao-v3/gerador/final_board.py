D = "/home/user/Claude/nova-visao-v3/"
css = """*{box-sizing:border-box;margin:0}body{background:#FAF6F1;color:#2B1A12;font:16px/1.45 'Inter',system-ui,sans-serif;padding:48px;width:1700px}
h1{font-size:40px;letter-spacing:-.02em;margin-bottom:6px}.sub{color:#6B5B52;font-size:19px;margin-bottom:22px;max-width:1250px}
h2{font-size:26px;margin:30px 0 4px}.hint{color:#6B5B52;margin-bottom:12px}
.grid{display:grid;gap:16px}.g4{grid-template-columns:repeat(4,1fr)}.g3{grid-template-columns:repeat(3,1fr)}
.card{background:#fff;border:1px solid #E6DDD3;border-radius:16px;padding:14px}.card img{width:100%;display:block;border-radius:8px}
.card b{display:block;margin-top:8px;font-size:17px}.card span{color:#6B5B52;font-size:14px}
.tag{display:inline-block;background:#FF5F00;color:#fff;border-radius:8px;padding:1px 9px;font-size:13px;margin-right:6px;vertical-align:1px}"""
def card(src, title, note, tag):
    return f'<div class="card"><img src="file://{D}{src}"><b><span class="tag">{tag}</span>{title}</b><span>{note}</span></div>'
pop = "".join([
    card("svg-p2-nariz/nariz-var1-laranja.svg", "Silhueta do óculos · variação 1", "P2 com o nariz corrigido. Proporção equilibrada.", "P2"),
    card("svg-p2-nariz/nariz-var3-laranja.svg", "Silhueta do óculos · variação 3", "P2 com o nariz corrigido. Mais larga.", "P2"),
    card("svg-p2-explorar/v7-laranja.svg", "Silhueta reconstruída · combinação", "Cantos macios, ponte em arco e nome grande. Meu favorito entre os vetores limpos.", "P2"),
    card("svg-popular-gpt/var4-horizontal-laranja.svg", "Símbolo diagonal + letras", "P1 do ChatGPT, vetorizado. Container com onda.", "P1"),
])
pop2 = "".join([
    card("svg-perspectiva/B-wave-simbolo-laranja.svg", "Óculos em perspectiva 3/4 (3D)", "Construído por mim. Só o símbolo, sem logo completa.", "3D"),
    card("svg-perspectiva/A-plain-simbolo-laranja.svg", "Perspectiva suave (3D)", "Variante com container reto.", "3D"),
    card("svg-p3/p3-1-laranja.svg", "Haste sob o nome", "Proposta minha para o P3. Fraca, guardada como alternativa.", "P3"),
])
prem = "".join(card(f"svg-p4-gpt/p4gpt-{i}.svg", t, n, "P4") for i, t, n in [
    (1, "Arco laranja · óculos marfim", "Ângulo 1.", ), (2, "Arco café · óculos laranja", "Ângulo 1.", ),
    (3, "Arco laranja · óculos marfim", "Ângulo 2.", ), (4, "Arco café · óculos laranja", "Ângulo 2.", )] ) if False else "".join(
    card(f"svg-p4-gpt/p4gpt-{i}.svg", t, n, "P4") for i, t, n in [
    (1, "Arco laranja · óculos marfim", "Ângulo 1."), (2, "Arco café · óculos laranja", "Ângulo 1."),
    (3, "Arco laranja · óculos marfim", "Ângulo 2."), (4, "Arco café · óculos laranja", "Ângulo 2.")])
html = (f'<!doctype html><meta charset="utf-8"><style>{css}</style><body><h1>O que sobrou</h1>'
        f'<p class="sub">As opções guardadas que valem a pena, separadas por versão. Ficaram de fora o P6 e o P7 (fracos), o P5 (você ainda não mandou o resultado) e as primeiras rodadas minhas.</p>'
        f'<h2>Popular</h2><p class="hint">O principal é o P2, com a silhueta do óculos como logo.</p><div class="grid g4">{pop}</div><div class="grid g3" style="margin-top:16px">{pop2}</div>'
        f'<h2>Premium</h2><p class="hint">O P4 é a direção: arco de vitrine, óculos em perspectiva e serifa.</p><div class="grid g4">{prem}</div></body>')
open(D + "o-que-sobrou.html", "w").write(html)
