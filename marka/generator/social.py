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


def cover_photo(p, name):
    """Same layout as the home page hero: the whole photo of Iława from a glider on the left (full height),
    a short gradient joins its right edge to the field colour, the patch on the photo east of Jeziorak
    (66 % of the photo width), the name on the right. Everything important is in the band that Facebook
    shows on desktop (y 150..774) and on phones (x 180..1460); the profile picture covers the bottom-left corner."""
    import base64
    W, H = 1640, 924
    pw = H * 4 / 3                                   # whole photo, scaled to the cover height
    img = base64.b64encode(open(PHOTO, "rb").read()).decode()
    o = ['<defs><linearGradient id="fade" x1="0" x2="1" y1="0" y2="0">'
         '<stop offset="0.78" stop-color="%s" stop-opacity="0"/><stop offset="0.89" stop-color="%s" stop-opacity="0.45"/>'
         '<stop offset="1" stop-color="%s"/></linearGradient></defs>' % (p["field"], p["field"], p["field"])]
    o.append('<rect width="%d" height="%d" fill="%s"/>' % (W, H, p["field"]))
    o.append('<image x="0" y="0" width="%s" height="%d" preserveAspectRatio="xMidYMid meet" href="data:image/jpeg;base64,%s"/>' % (L.r1(pw), H, img))
    o.append('<rect x="0" y="0" width="%s" height="%d" fill="url(#fade)"/>' % (L.r1(pw), H))
    o.append(patch(p, 0.66 * pw, 462, 470))
    x = 1090
    o.append(text("AVIAVA", x, 450, 84, p["text"], track=8, anchor="start"))
    o.append(text("GRUPA LOTNICZA", x + 2, 510, 30, p["text"], track=6, face=L.FS, anchor="start"))
    o.append('<rect x="%d" y="535" width="300" height="4" fill="%s"/>' % (x + 2, p["rim"]))
    o.append(text("IŁAWA", x + 2, 585, 30, p["text"], track=6, face=L.FS, anchor="start"))
    save("facebook-tlo-zdjecie-%s" % name, "".join(o), W, H)


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
