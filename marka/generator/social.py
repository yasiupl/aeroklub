"""Social media graphics for Aviava: profile pictures, Facebook cover, story background, post frames."""
import os, cairosvg
from shapely import affinity
import logo, logo2 as L

P = L.PAL
OUT = "social"
os.makedirs(OUT, exist_ok=True)


def save(name, body, w, h):
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">%s</svg>' % (w, h, w, h, body)
    open("%s/%s.svg" % (OUT, name), "w").write(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to="%s/%s.png" % (OUT, name), output_width=w, output_height=h)


def patch(p, cx, cy, d):
    body, _ = L.round_patch(p)
    s = d / 400
    return '<g transform="translate(%s,%s) scale(%s)">%s</g>' % (L.r1(cx - d / 2), L.r1(cy - d / 2), L.r1(s), body)


def sygnet(p, cx, cy, d):
    body, _ = L.sygnet(p)
    s = d / 400
    return '<g transform="translate(%s,%s) scale(%s)">%s</g>' % (L.r1(cx - d / 2), L.r1(cy - d / 2), L.r1(s), body)


def lake(p, cx, cy, h, fill):
    g, _ = L.lake_placed(cx, cy, h)
    return '<path fill="%s" fill-rule="evenodd" d="%s"/>' % (fill, L.geom_d(g)), g


def waves(x, y, w, h, n=10, periods=4):
    return L.waves(x, y, w, h, n, "#FFFFFF", "#2E6DB4", periods=periods)


def text(t, x, y, size, fill, track=0, face=None, anchor="middle"):
    return logo.text_straight(t, x, y, size, fill, track=track, fname=face or L.FB, anchor=anchor)[0]


# ---------------------------------------------------------------- profile pictures (circle crop)
def profile():
    for name, p in [("jasna", P["szybowcowa"]), ("ciemna", P["nocna"])]:
        save("profilowe-naszywka-%s" % name, '<rect width="1080" height="1080" fill="%s"/>' % p["band"] + patch(p, 540, 540, 1040), 1080, 1080)
        save("profilowe-sygnet-%s" % name, '<rect width="1080" height="1080" fill="%s"/>' % p["field"] + sygnet(p, 540, 540, 1080), 1080, 1080)


def fieldgroup(p, cx, cy, d):
    """Patch field composition scaled so the field circle (286 units) has diameter d, centred at cx, cy."""
    s = d / 286
    return '<g transform="translate(%s,%s) scale(%s)">%s</g>' % (L.r1(cx - 200 * s), L.r1(cy - 200 * s), L.r1(s), L.field_content(p))


# ---------------------------------------------------------------- Facebook cover 1640 x 924
def cover(p, name):
    W, H = 1640, 924
    o = ['<rect width="%d" height="%d" fill="%s"/>' % (W, H, p["field"])]
    # the patch field exactly as in the patch, in the desktop-safe band (y 150..774), right of centre
    o.append(fieldgroup(p, 1130, 462, 600))
    # band with the name, as on the patch band
    o.append(text("AVIAVA", 470, 430, 140, p["text"], track=18))
    o.append('<rect x="210" y="462" width="520" height="5" fill="%s"/>' % p["rim"])
    o.append(text("IŁAWA", 470, 540, 54, p["text"], track=14))
    save("facebook-tlo-%s" % name, "".join(o), W, H)


# ---------------------------------------------------------------- Facebook cover with the photo, 1640 x 924
PHOTO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "zdjecia", "ilawa-z-szybowca.jpg")


def cover_photo(p, name, off=300):
    """Facebook cover with the photo of Iława from a glider on the whole background (no gradient), for the
    current Facebook Page layout. The cover is shallow there: about 2.7:1 on desktop and about 2.45:1 in the app,
    and the profile picture is under the cover, not on it. The canvas is 1640 x 640 (2.56:1), between both:
    desktop cuts about 16 px at the top and bottom, the app about 35 px on each side. Everything important is
    in the centre, at least 80 px from the left and right edges and 40 px from the top and bottom.
    Left, as on the original cover: AVIAVA, a line in the rim colour and the slogan. The patch on the right,
    symmetric to the text block and in line with it. A soft shadow under the text keeps it readable on the photo.
    off: how many pixels of the scaled photo (1640 x 1230) are cut at the top; 300 shows the sky with clouds, Jeziorak, Wielka Żuława
    and the town."""
    import base64, io
    from PIL import Image, ImageFilter
    W, H = 1640, 640
    s = W / 1600
    ph = 1200 * s
    img = base64.b64encode(open(PHOTO, "rb").read()).decode()
    photo = '<image x="0" y="%s" width="%d" height="%s" href="data:image/jpeg;base64,%s"/>' % (L.r1(-off), W, L.r1(ph), img)
    t = [text("AVIAVA", 470, 285, 140, "#FFFFFF", track=18),
         '<rect x="210" y="317" width="520" height="5" fill="%s"/>' % p["rim"],
         text("Pojezierze znasz z żaglówki.", 470, 385, 44, "#FFFFFF", face=L.FS),
         text("Zobacz je z góry.", 470, 441, 44, "#FFFFFF", face=L.FS)]
    badge = patch(p, W - 470, 313, 380)   # mirror of the text block (centred at x 470): symmetric on the right, in line with the text
    # SVG: the shadow is an SVG filter
    shadow = ('<defs><filter id="sh" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur in="SourceAlpha" stdDeviation="9"/>'
              '<feComponentTransfer><feFuncA type="linear" slope="0.55"/></feComponentTransfer><feMerge><feMergeNode/>'
              '<feMergeNode in="SourceGraphic"/></feMerge></filter></defs>')
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">%s%s<g filter="url(#sh)">%s%s</g></svg>' % (
        W, H, W, H, shadow, photo, "".join(t), badge)
    open("%s/facebook-tlo-zdjecie-%s.svg" % (OUT, name), "w").write(svg)
    # PNG: the same shadow made with Pillow (cairosvg does not draw SVG filters)
    def layer(body):
        doc = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">%s</svg>' % (W, H, W, H, body)
        return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=doc.encode(), output_width=W, output_height=H))).convert("RGBA")
    base = layer(photo)
    top = layer("".join(t) + badge)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.putalpha(top.getchannel("A").filter(ImageFilter.GaussianBlur(9)).point(lambda a: int(a * 0.55)))
    out = Image.alpha_composite(Image.alpha_composite(base, sh), top).convert("RGB")
    out.save("%s/facebook-tlo-zdjecie-%s.png" % (OUT, name), optimize=True)


# ---------------------------------------------------------------- story / tło 1080 x 1920
def story(p, name):
    W, H = 1080, 1920
    o = ['<rect width="%d" height="%d" fill="%s"/>' % (W, H, p["field"])]
    o.append(fieldgroup(p, 540, 980, 1000))
    o.append(text("AVIAVA", 540, 380, 140, p["text"], track=20))
    o.append('<rect x="0" y="1560" width="%d" height="360" fill="%s"/>' % (W, p["band"]))
    o.append('<rect x="0" y="1560" width="%d" height="12" fill="%s"/>' % (W, p["rim"]))
    o.append(text("IŁAWA", 540, 1690, 72, p["text"], track=16))
    save("instagram-relacja-tlo-%s" % name, "".join(o), W, H)


# ---------------------------------------------------------------- post frames (transparent centre)
def frame(p, name, W, H):
    t = 18                      # rim
    b = 10                      # band inside the rim
    bottom = 130
    o = ['<path fill="%s" fill-rule="evenodd" d="M0,0H%dV%dH0Z M%d,%dH%dV%dH%dZ"/>' % (p["rim"], W, H, t, t, W - t, H - bottom, t)]
    o.append('<path fill="%s" fill-rule="evenodd" d="M%d,%dH%dV%dH%dZ M%d,%dH%dV%dH%dZ"/>' % (
        p["band"], t, t, W - t, H - bottom, t, t + b, t + b, W - t - b, H - bottom, t + b))
    o.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>' % (t, H - bottom, W - 2 * t, bottom - t, p["band"]))
    o.append(text("AVIAVA · IŁAWA", 60, H - bottom + 80, 46, p["text"], track=6, anchor="start"))
    o.append(patch(p, W - 150, H - 150, 250))
    save("ramka-%s-%dx%d" % (name, W, H), "".join(o), W, H)


if __name__ == "__main__":
    profile()
    for name, p in [("jasna", P["szybowcowa"]), ("ciemna", P["nocna"])]:
        cover(p, name)
        cover_photo(p, name)
        story(p, name)
        frame(p, name, 1080, 1350)
        frame(p, name, 1080, 1080)
    print(sorted(os.listdir(OUT)))
