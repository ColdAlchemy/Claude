# Nova Visão · como rodar os prompts + 2 prompts novos

## Como rodar (resumo)
- **Chat novo para cada prompt.** Assim o ChatGPT não se contamina com os resultados parecidos com a Diniz.
- **Anexe só 1 imagem:** `referencias-3-para-chatgpt.png` (10 marcas rotuladas de A a J). Ela já contém as suas duas tipografias (G e H). Não precisa anexar os arquivos das mensagens anteriores.
- **Cole o prompt inteiro** (de `prompts-chatgpt-2.md` ou deste arquivo). As letras A a J dos prompts correspondem à imagem.
- **Depois de gerar, continue no mesmo chat** para refinar a opção que você escolheu, com o "prompt de iteração" abaixo. É aí que o ChatGPT mantém a continuidade.

## Quais prompts rodar agora
Os símbolos premium eu já testei nos containers (arco, selo, lente). Então o ChatGPT é mais útil agora na versão **popular**:
1. **P1** (Diniz × Zeiss): do arquivo `prompts-chatgpt-2.md`.
2. **P2** (Specsavers × Diniz): do arquivo `prompts-chatgpt-2.md`.
3. **P3** (Persol × sua tipografia): do arquivo `prompts-chatgpt-2.md`.
4. **P6** (Chilli Beans × Warby Parker): neste arquivo.

P4 e P5 do arquivo anterior só se você quiser que o ChatGPT desenhe novos containers premium. O **P7** abaixo é a versão premium só com as letras.

---

## P6 · Popular · o óculos vive dentro do nome (Chilli Beans × Warby Parker)

```
The attached board shows labeled brand logos (A to J). Use them as references only. Do not copy.
From I (Chilli Beans): the idea that one proprietary object lives inside the name, interrupting the letters, so the object becomes the brand's character.
From J (Warby Parker): confident restraint and clean spacing.
From G: keep this exact lettering style (heavy, wide, rounded, hand-drawn tilde). Write "nova visão" exactly.
Do NOT carry over: I's italic black letters and pepper, J's thin capitals.

Create an original logo for "Nova Visão", a friendly Brazilian optical store, in a horizontal layout.
Orange (#FF5F00) lettering "nova visão" in the style of G. Between the two words, a small bold pair of glasses in orange, slightly tilted, with the same stroke weight as the lettering, sits in the space like an object that belongs to the name. Very small spaced capitals "ÓTICA" above.
Flat vector, no gradients, no shadows, no watermark. White background, generous padding. 4 variations of the glasses' size and angle.
```

## P7 · Premium · só as letras, com contenção (Warby Parker × Persol)

```
The attached board shows labeled brand logos (A to J). Use them as references only. Do not copy.
From J (Warby Parker): clean, widely spaced capitals and confident restraint.
From E (Persol): one hand-drawn gesture that carries the brand.
From H: the serif mood.
Do NOT carry over: J's sans-serif, E's script.

Create an original premium wordmark for "Nova Visão", an upscale Brazilian optical boutique, with no symbol.
Custom-drawn high-contrast serif capitals "NOVA VISÃO", wide letterspacing, orange (#FF5F00). One single drawn gesture: the hairline of the "V" extends and curves like a glasses temple arm that hooks over the Ã's tilde as a thin calligraphic wave. "ÓTICA" small between two thin rules below.
Flat vector, no gradients, no shadows, no watermark. Ivory background, generous padding. 4 variations of the gesture.
```

---

## Prompt de iteração
```
Keep everything identical, including the symbol shape, the lettering, the colors, the background and the composition. Change only: [uma coisa só].
```

Exemplo para o premium: `make the line weight 40% thicker so it holds up when knocked out inside a solid container`.
