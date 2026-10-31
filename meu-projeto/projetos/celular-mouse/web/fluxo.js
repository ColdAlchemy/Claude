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
    this.temPrev = false;
  }

  Fluxo.prototype.reiniciar = function () { this.temPrev = false; };

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
    var res = { ok: false, dx: 0, dy: 0, brilho: media, contraste: dp, err: 9 };
    if (dp < 1.2) { this.temPrev = false; return res; }          // sem textura (ou sem luz)

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

  Fluxo.prototype._estimar = function (res) {
    var dx = 0, dy = 0, err = 9, minEig = 0, x, y;
    for (var l = this.n - 1; l >= 0; l--) {
      var w = this.ws[l], h = this.hs[l], P = this.prev[l], C = this.cur[l], GX = this.gx[l], GY = this.gy[l];
      for (y = 1; y < h - 1; y++) {
        for (x = 1; x < w - 1; x++) {
          var q = y * w + x;
          GX[q] = (P[q + 1] - P[q - 1]) * 0.5;
          GY[q] = (P[q + w] - P[q - w]) * 0.5;
        }
      }
      if (l < this.n - 1) { dx *= 2; dy *= 2; }
      var iters = l === 0 ? 3 : 4;
      for (var it = 0; it < iters; it++) {
        var mx = Math.ceil(Math.abs(dx)) + 2, my = Math.ceil(Math.abs(dy)) + 2;
        if (w - 2 * mx < 6 || h - 2 * my < 6) return;
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
        err = ee / cnt;
        if (det < 1e-9 * cnt * cnt) return;
        var ddx = (gyy * bx - gxy * by) / det, ddy = (gxx * by - gxy * bx) / det;
        dx += ddx; dy += ddy;
        if (Math.abs(dx) > w * 0.45 || Math.abs(dy) > h * 0.45) return;
        if (Math.abs(ddx) < 0.005 && Math.abs(ddy) < 0.005) break;
      }
    }
    res.dx = dx; res.dy = dy; res.err = err;
    res.ok = err < 0.5 && minEig > 1e-4;
  };

  if (typeof module !== 'undefined' && module.exports) module.exports = Fluxo;
  else raiz.Fluxo = Fluxo;
})(typeof window !== 'undefined' ? window : this);
