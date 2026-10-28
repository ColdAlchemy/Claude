// node render.js out.png width height file1.svg [file2.svg ...]  -> contact sheet com fundos claro/escuro
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [out, w, h, bg, ...files] = process.argv.slice(2);
  const cells = files.map(f => {
    const abs = require('path').resolve(f);
    return `<div class="c"><img src="file://${abs}" style="height:${h}px;display:block"><span>${f.split('/').slice(-2).join('/')}</span></div>`;
  }).join('');
  const html = `<html><body style="margin:0;background:${bg};font:11px sans-serif">
  <style>.c{display:inline-block;margin:14px;vertical-align:top}.c svg{display:block;height:${h}px;width:auto}
  .c span{display:block;margin-top:4px;color:#888}</style>${cells}</body></html>`;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: +w, height: 400 }, deviceScaleFactor: 2 });
  require('fs').writeFileSync('/tmp/_sheet.html', html); await p.goto('file:///tmp/_sheet.html');
  await p.screenshot({ path: out, fullPage: true });
  await b.close();
})();
