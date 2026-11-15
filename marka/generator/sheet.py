import logo2 as L, cairosvg
P=L.PAL
items=[L.round_patch(P["szybowcowa"],gulls=True,stars=True), L.round_patch(P["nocna"],gulls=True,stars=True), L.sygnet(P["szybowcowa"]),
       L.flag(P["szybowcowa"]), L.pennant(P["szybowcowa"]), L.pin_badge(P["szybowcowa"])]
cells=[];x=20;y=20;rowh=0
for body,(w,h) in items:
    s=380/max(w,h)*(1 if w<500 else 1.5)
    if x+w*s>1500: x=20;y+=rowh+30;rowh=0
    cells.append('<g transform="translate(%d,%d) scale(%.3f)">%s</g>'%(x,y,s,body)); x+=w*s+30; rowh=max(rowh,h*s)
doc='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1540 %d" width="1540"><rect width="100%%" height="100%%" fill="#d9d9d4"/>%s</svg>'%(y+rowh+20,"".join(cells))
cairosvg.svg2png(bytestring=doc.encode(),write_to="sheet.png")
# swan alone big
sw='<svg xmlns="http://www.w3.org/2000/svg" viewBox="-100 -80 240 110" width="960"><rect x="-100" y="-80" width="240" height="110" fill="#1F4E9C"/><path fill="#fff" d="%s"/></svg>'%L.swan_d()
cairosvg.svg2png(bytestring=sw.encode(),write_to="swan.png")
