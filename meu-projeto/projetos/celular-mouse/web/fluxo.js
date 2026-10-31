// Fluxo optico: mede quanto a superficie (textura da mesa) andou entre dois quadros da camera.
// E' o mesmo principio de um mouse optico. Estimativa global de translacao por
// Lucas-Kanade em piramide (4 niveis), com precisao de fracao de pixel.
//
// Uso:  var f = new Fluxo(128, 96);  var r = f.processar(rgba);
//   r.ok  -> medida confiavel;  r.dx, r.dy -> deslocamento do CONTEUDO da imagem (px, y para baixo)
//   r.brilho (0..255), r.contraste, r.err (qualidade; menor = melhor)
(function (raiz) {
  'use strict';

  function Fluxo(w, h, niveis) {
    this.w = w; this.h = h; this.n = niveis || 4;
    this.cur = []; this.prev = []; this.gx = []; this.gy = []; this.ws = []; this.hs = [];
    var lw = w, lh = h;
    for (var l = 0; l < this.n; l++) {
      this.ws.push(lw); this.hs.push(lh);
      this.cur.push(new Float32Array(lw * lh)); this.prev.push(new Float32Array(lw * lh));
      this.gx.push(new Float32Array(lw * lh)); this.gy.push(new Float32Array(lw * lh));
      lw >>= 1; lh >>= 1;
    }
    this.temPrev = false; this.vx = 0; this.vy = 0;
    this.limErr = 0.25;      // qualidade minima (menor = mais exigente)
  }

  Fluxo.prototype.reiniciar = function () { this.temPrev = false; this.vx = 0; this.vy = 0; };

  Fluxo.prototype.processar = function (rgba) {
    var w = this.w, h = this.h, N = w * h, L0 = this.cur[0], i, j;
    var soma = 0;
    for (i = 0, j = 0; i < N; i++, j += 4) {
      var g = (rgba[j] * 77 + rgba[j + 1] * 150 + rgba[j + 2] * 29) >> 8;
      L0[i] = g; soma += g;
    }
    var media = soma / N, v = 0;
    for (i = 0; i < N; i++) { var d = L0[i] - media; v += d * d; }
    var dp = Math.sqrt(v / N);
    var res = { ok: false, dx: 0, dy: 0, brilho: media, contraste: dp, err: 9, aniso: 0 };
    if (dp < 1.2) { this.temPrev = false; this.vx = 0; this.vy = 0; return res; }          // sem textura (ou sem luz)

    var inv = 1 / dp;
    for (i = 0; i < N; i++) L0[i] = (L0[i] - media) * inv;       // tira brilho e contraste
    for (var l = 1; l < this.n; l++) {                           // piramide: media 2x2
      var A = this.cur[l - 1], B = this.cur[l], aw = this.ws[l - 1], bw = this.ws[l], bh = this.hs[l];
      for (var y = 0; y < bh; y++) {
        for (var x = 0; x < bw; x++) {
          var p = 2 * y * aw + 2 * x;
          B[y * bw + x] = (A[p] + A[p + 1] + A[p + aw] + A[p + aw + 1]) * 0.25;
        }
      }
    }
    if (this.temPrev) this._estimar(res);
    var t = this.cur; this.cur = this.prev; this.prev = t;       // este quadro vira o "anterior"
    this.temPrev = true;
    return res;
  };

  // Estima o deslocamento tentando primeiro o "palpite" (velocidade do quadro anterior) e,
  // se nao ficar bom, de novo a partir do zero. Fica com a melhor das duas.
  Fluxo.prototype._estimar = function (res) {
    var l, x, y;
    for (l = 0; l < this.n; l++) {                     // gradientes do quadro anterior (1 vez so)
      var w = this.ws[l], h = this.hs[l], P = this.prev[l], GX = this.gx[l], GY = this.gy[l];
      for (y = 1; y < h - 1; y++) {
        for (x = 1; x < w - 1; x++) {
          var q = y * w + x;
          GX[q] = (P[q + 1] - P[q - 1]) * 0.5;
          GY[q] = (P[q + w] - P[q - w]) * 0.5;
        }
      }
    }
    var cands = [[this.vx, this.vy]];
    if (Math.abs(this.vx) + Math.abs(this.vy) > 1) cands.push([0, 0]);
    var melhor = null;
    for (var c = 0; c < cands.length; c++) {
      var r = this._resolver(cands[c][0], cands[c][1]);
      if (r && (!melhor || r.err < melhor.err)) melhor = r;
      if (melhor && melhor.err < 0.2) break;
    }
    if (!melhor) { this.vx *= 0.8; this.vy *= 0.8; return; }
    res.dx = melhor.dx; res.dy = melhor.dy; res.err = melhor.err; res.aniso = melhor.aniso;
    // aceita so medidas de boa qualidade; e rejeita "pulos" que fogem muito da previsao
    var pred = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
    var pulo = Math.sqrt((melhor.dx - this.vx) * (melhor.dx - this.vx) + (melhor.dy - this.vy) * (melhor.dy - this.vy));
    res.ok = melhor.err < this.limErr && melhor.minEig > 1e-4 && !(pulo > 0.6 * pred + 8 && melhor.err > 0.12);
    if (res.ok) { this.vx = melhor.dx; this.vy = melhor.dy; } else { this.vx *= 0.8; this.vy *= 0.8; }
  };

  Fluxo.prototype._resolver = function (gx, gy) {
    var dx = gx / Math.pow(2, this.n - 1), dy = gy / Math.pow(2, this.n - 1), err = 9, minEig = 0, aniso = 0, x, y;
    for (var l = this.n - 1; l >= 0; l--) {
      var w = this.ws[l], h = this.hs[l], P = this.prev[l], C = this.cur[l], GX = this.gx[l], GY = this.gy[l];
      if (l < this.n - 1) { dx *= 2; dy *= 2; }
      var iters = l === 0 ? 3 : 4;
      for (var it = 0; it < iters; it++) {
        var mx = Math.ceil(Math.abs(dx)) + 2, my = Math.ceil(Math.abs(dy)) + 2;
        if (w - 2 * mx < 6 || h - 2 * my < 6) { if (l === 0) return null; break; }   // sem area neste nivel: pula (o palpite ja cobre)
        var gxx = 0, gxy = 0, gyy = 0, bx = 0, by = 0, ee = 0, cnt = 0;
        for (y = my; y < h - my; y++) {
          for (x = mx; x < w - mx; x++) {
            var p = y * w + x, sx = x + dx, sy = y + dy;
            var x0 = Math.floor(sx), y0 = Math.floor(sy), fx = sx - x0, fy = sy - y0, k = y0 * w + x0;
            var i2 = (C[k] * (1 - fx) + C[k + 1] * fx) * (1 - fy) + (C[k + w] * (1 - fx) + C[k + w + 1] * fx) * fy;
            var e = P[p] - i2, ix = GX[p], iy = GY[p];
            gxx += ix * ix; gxy += ix * iy; gyy += iy * iy; bx += ix * e; by += iy * e; ee += e * e; cnt++;
          }
        }
        var det = gxx * gyy - gxy * gxy;
        var tr = gxx + gyy, disc = Math.sqrt(Math.max(tr * tr / 4 - det, 0));
        minEig = (tr / 2 - disc) / cnt;
        aniso = (tr / 2 + disc) > 0 ? (tr / 2 - disc) / (tr / 2 + disc) : 0;   // 1 = igual em todas as direcoes; ~0 = so uma direcao (ex.: veio da madeira)
        err = ee / cnt;
        if (det < 1e-9 * cnt * cnt) return null;
        var ddx = (gyy * bx - gxy * by) / det, ddy = (gxx * by - gxy * bx) / det;
        dx += ddx; dy += ddy;
        if (Math.abs(dx) > w * 0.45 || Math.abs(dy) > h * 0.45) return null;
        if (Math.abs(ddx) < 0.005 && Math.abs(ddy) < 0.005) break;
      }
    }
    return { dx: dx, dy: dy, err: err, minEig: minEig, aniso: aniso };
  };

  // Calibracao: recebe o que a imagem andou ao deslizar "para a frente" (cf) e "para a direita" (cr)
  // e devolve a matriz 2x2 [m00,m01,m10,m11] imagem -> cursor (em contagens, a 800 DPI para 10 cm).
  // A camera e' fixa no celular, entao a matriz so pode ser uma troca de eixos com sinais
  // (8 possibilidades) vezes uma escala. Escolher a melhor das 8 elimina qualquer "torto" dos deslizes.
  Fluxo.calibrar = function (cf, cr, cmReferencia, dpi) {
    var nf = Math.hypot(cf[0], cf[1]), nr = Math.hypot(cr[0], cr[1]);
    if (nf < 1e-6 || nr < 1e-6) return null;
    var Ps = [];
    [1, -1].forEach(function (a) { [1, -1].forEach(function (b) {
      Ps.push([a, 0, 0, b]);   // sem trocar eixos
      Ps.push([0, a, b, 0]);   // trocando eixos
    }); });
    var res = [];
    Ps.forEach(function (P) {
      var fx = (P[0] * cf[0] + P[1] * cf[1]) / nf, fy = (P[2] * cf[0] + P[3] * cf[1]) / nf;   // frente deve virar (0,-1)
      var rx = (P[0] * cr[0] + P[1] * cr[1]) / nr, ry = (P[2] * cr[0] + P[3] * cr[1]) / nr;   // direita deve virar (1,0)
      res.push({ P: P, score: -fy + rx });                                                    // 2 = perfeito
    });
    res.sort(function (a, b) { return b.score - a.score; });
    var R = (cmReferencia || 10) * (dpi || 800) / 2.54, esc = R / ((nf + nr) / 2), P = res[0].P;
    return { mat: [P[0] * esc, P[1] * esc, P[2] * esc, P[3] * esc], score: res[0].score, segundo: res[1].score, nf: nf, nr: nr };
  };

  if (typeof module !== 'undefined' && module.exports) module.exports = Fluxo;
  else raiz.Fluxo = Fluxo;
})(typeof window !== 'undefined' ? window : this);
