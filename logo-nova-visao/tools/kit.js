// node tools/kit.js  -> gera ../kit-logo-nova-visao/ (SVG, PDF e PNG) a partir de sistema/*.svg
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'kit-logo-nova-visao');
const BIG = [2400, 800], MED = [1200, 400];
const items = [
  ['01-horizontal', 'horizontal_cor', '01-horizontal', BIG],
  ['01-horizontal', 'horizontal_fundo-escuro', '01-horizontal-fundo-escuro', BIG],
  ['01-horizontal', 'horizontal_sobre-laranja-ou-foto', '01-horizontal-sobre-laranja-ou-foto', BIG],
  ['01-horizontal', 'horizontal_uma-cor-cafe', '01-horizontal-uma-cor-cafe', BIG],
  ['01-horizontal', 'horizontal_uma-cor-creme_fundo-escuro', '01-horizontal-uma-cor-cafe-fundo-escuro', BIG],
  ['02-com-assinatura-otica', 'assinatura-embaixo_cor', '02-horizontal-assinatura-otica', BIG],
  ['02-com-assinatura-otica', 'linha-otica_cor', '02-horizontal-linha-otica', BIG],
  ['02-com-assinatura-otica', 'linha-otica_fundo-escuro', '02-horizontal-linha-otica-fundo-escuro', BIG],
  ['02-com-assinatura-otica', 'linha-otica_sobre-laranja', '02-horizontal-linha-otica-sobre-laranja', BIG],
  ['03-vertical', 'vertical_cor', '03-vertical', MED],
  ['03-vertical', 'vertical_fundo-escuro', '03-vertical-fundo-escuro', MED],
  ['03-vertical', 'vertical_sobre-laranja-ou-foto', '03-vertical-sobre-laranja-ou-foto', MED],
  ['03-vertical', 'vertical_uma-cor-cafe', '03-vertical-uma-cor-cafe', MED],
  ['04-simbolo', 'simbolo_cor', '04-simbolo', MED],
  ['04-simbolo', 'simbolo_branco', '04-simbolo-branco', MED],
  ['04-simbolo', 'simbolo_uma-cor-cafe', '04-simbolo-uma-cor-cafe', MED],
  ['04-simbolo', 'simbolo_tamanho-pequeno_cor', '04-simbolo-tamanho-pequeno', [400, 200, 96]],
  ['04-simbolo', 'simbolo_tamanho-pequeno_branco', '04-simbolo-tamanho-pequeno-branco', [400, 200, 96]],
  ['05-so-o-nome', 'nome_cor', '05-nome', BIG],
  ['05-so-o-nome', 'nome_branco', '05-nome-branco', BIG],
  ['05-so-o-nome', 'nome_cafe', '05-nome-cafe', BIG],
  ['06-avatar-icone-favicon', 'avatar-circular', '06-avatar-circulo', [1024, 400]],
  ['06-avatar-icone-favicon', 'icone-app_cantos-arredondados', '06-icone-app-quadrado', [1024, 512, 180]],
  ['06-avatar-icone-favicon', 'icone-app_sem-cantos-1024', '06-icone-app-sem-cantos', [1024]],
  ['06-avatar-icone-favicon', 'favicon', '06-favicon', [512, 192, 48, 32, 16]],
  ['07-selos', 'selo_laranja', '07-selo-laranja', MED],
  ['07-selos', 'selo_contorno', '07-selo-contorno', MED],
  ['07-selos', 'selo_cafe', '07-selo-cafe', MED],
];
(async () => {
  fs.rmSync(OUT, { recursive: true, force: true });
  const b = await chromium.launch();
  const p = await b.newPage();
  for (const [dir, name, src, sizes] of items) {
    const d = path.join(OUT, dir); fs.mkdirSync(d, { recursive: true });
    const svgPath = path.join(ROOT, 'sistema', src + '.svg');
    let svg = fs.readFileSync(svgPath, 'utf8');
    fs.writeFileSync(path.join(d, name + '.svg'), svg);
    const m = svg.match(/viewBox="0 0 ([\d.]+) ([\d.]+)"/); const vw = parseFloat(m[1]), vh = parseFloat(m[2]);
    // PDF vetorial
    const sc = 2;
    const inline = svg.replace('<svg ', `<svg width="${vw * sc}" height="${vh * sc}" `);
    await p.setContent(`<html><body style="margin:0">${inline}</body></html>`);
    await p.pdf({ path: path.join(d, name + '.pdf'), width: `${vw * sc}px`, height: `${vh * sc}px`, printBackground: true, pageRanges: '1' });
    // PNG transparente
    for (const w of sizes) {
      const h = Math.round(w * vh / vw);
      await p.setViewportSize({ width: w, height: h });
      const inl = svg.replace('<svg ', `<svg width="${w}" height="${h}" style="display:block" `);
      await p.setContent(`<html><body style="margin:0;background:transparent">${inl}</body></html>`);
      await p.waitForTimeout(120);
      await p.screenshot({ path: path.join(d, `${name}_${w}px.png`), omitBackground: true });
    }
  }
  await b.close();
  console.log('ok');
})();
