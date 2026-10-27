import json
from PIL import Image
from trace import trace
U="/root/.claude/uploads/e19f6b0b-622f-5ee1-a4a5-f14c5bc9806b/"
im = Image.open(U+"1cce830b-image.jpg")
wm_box=(150,140,1150,306)
ds_box=(150,80,400,140)
d1,w1,h1 = trace(im, wm_box)
d2,w2,h2 = trace(im, ds_box)
json.dump(dict(wordmark=dict(d=d1,w=w1,h=h1), descriptor=dict(d=d2,w=w2,h=h2)), open("traced_A.json","w"))
open("prev_A.svg","w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 250"><rect width="1000" height="250" fill="#fff"/><path d="{d2}" transform="translate(0,0)" fill="#FF5F00" fill-rule="evenodd"/><path d="{d1}" transform="translate(0,60)" fill="#FF5F00" fill-rule="evenodd"/></svg>')
print(w1,h1,w2,h2, len(d1), len(d2))
