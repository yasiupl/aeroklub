import os, logo2 as L, cairosvg, zipfile, shutil
P = L.PAL
out = "export"
shutil.rmtree(out, ignore_errors=True); os.makedirs(out + "/svg"); os.makedirs(out + "/png")
items = {
    "aviava-naszywka-jasna": (L.round_patch, P["szybowcowa"], {}),
    "aviava-naszywka-ciemna": (L.round_patch, P["nocna"], {}),
    "aviava-sygnet": (L.sygnet, P["szybowcowa"], {}),
    "aviava-sygnet-ciemny": (L.sygnet, P["nocna"], {}),
    "aviava-flaga": (L.flag, P["szybowcowa"], {}),
    "aviava-proporczyk": (L.pennant, P["szybowcowa"], {}),
    "aviava-odznaka": (L.pin_badge, P["szybowcowa"], {}),
}
for name, (fn, pal, kw) in items.items():
    body, (w, h) = fn(pal, **kw)
    doc = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" '
           'aria-label="Aviava – %s"><title>Aviava</title><desc>Obrys jezior: Mapa Jeziora Jeziorak, Marcin n, '
           'Wikimedia Commons, CC BY-SA 2.5. Krój: Brygada 1918, SIL OFL 1.1.</desc>%s</svg>') % (w, h, w, h, name, body)
    open("%s/svg/%s.svg" % (out, name), "w").write(doc)
    for px in (512, 2048):
        cairosvg.svg2png(bytestring=doc.encode(), write_to="%s/png/%s-%d.png" % (out, name, px), output_width=px)
print(sorted(os.listdir(out + "/svg")))

import haft
for name, pal in [("aviava-haft-jasna", P["szybowcowa"]), ("aviava-haft-ciemna", P["nocna"])]:
    open("%s/svg/%s-inkstitch.svg" % (out, name), "w").write(haft.svg(pal))
    prev = haft.svg(pal, inkstitch=False)
    for px in (512, 2048):
        cairosvg.svg2png(bytestring=prev.encode(), write_to="%s/png/%s-%d.png" % (out, name, px), output_width=px)
print(sorted(os.listdir(out + "/svg")))
