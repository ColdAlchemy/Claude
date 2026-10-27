import numpy as np, potrace
from PIL import Image, ImageFilter

def trace(img, box, up=4, thr=190, alpha=1.0):
    """Vetoriza um recorte (orange sobre branco). Retorna (path d, w, h) em coordenadas do recorte original."""
    im = img.crop(box).convert("L")
    w, h = im.size
    im = im.resize((w*up, h*up), Image.LANCZOS).filter(ImageFilter.GaussianBlur(up*0.45))
    arr = np.array(im) < thr
    bm = potrace.Bitmap(~arr)
    pl = bm.trace(turdsize=30, turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY, alphamax=alpha, opticurve=True, opttolerance=0.3)
    s = 1.0/up
    f = lambda p: f"{p.x*s:.2f},{p.y*s:.2f}"
    d = []
    for c in pl:
        d.append("M"+f(c.start_point))
        for seg in c.segments:
            if seg.is_corner:
                d.append("L"+f(seg.c)+" L"+f(seg.end_point))
            else:
                d.append("C"+f(seg.c1)+" "+f(seg.c2)+" "+f(seg.end_point))
        d.append("Z")
    return " ".join(d), w, h

if __name__ == "__main__":
    U="/root/.claude/uploads/e19f6b0b-622f-5ee1-a4a5-f14c5bc9806b/"
    im = Image.open(U+"1cce830b-image.jpg")
    # bbox do logotipo e do descritor
    arr = np.array(im.convert("L")) < 190
    ys = np.where(arr.any(axis=1))[0]; xs = np.where(arr.any(axis=0))[0]
    print("bbox", xs.min(), xs.max(), ys.min(), ys.max())
    rows = arr.any(axis=1)
    # separar blocos por linhas vazias
    blocks=[]; start=None
    for y,v in enumerate(rows):
        if v and start is None: start=y
        if not v and start is not None: blocks.append((start,y)); start=None
    print(blocks)
