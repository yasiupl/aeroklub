"""Aviava logo generator: SVG fragments with outlined text."""
import math
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union
from shapely import affinity

import os
FONT_DIR = os.environ.get("AVIAVA_FONT_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")) + "/"
_fonts = {}


FACE = "BarlowCondensed-Bold"
KSIZE = 1.0
KTRACK = 1.0


def font(name=None):
    name = name or FACE
    if name not in _fonts:
        f = TTFont(FONT_DIR + name + ".ttf")
        _fonts[name] = (f, f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm)
    return _fonts[name]


def r1(v):
    return ("%.1f" % v).rstrip("0").rstrip(".")


def glyph_path(ch, matrix, fname):
    f, gs, cmap, upm = font(fname)
    g = gs[cmap[ord(ch)]]
    pen = SVGPathPen(gs, ntos=lambda v: ("%.2f" % v).rstrip("0").rstrip("."))
    g.draw(TransformPen(pen, matrix))
    return pen.getCommands(), g.width


_HB = {}
OPTICAL = {"VI": -40, "IA": -20, "IŁ": 0}


def _hb_advances(text, fname):
    """Advances in font units with the font's kerning (GPOS 'kern'), via HarfBuzz."""
    import uharfbuzz as hb
    if fname not in _HB:
        blob = hb.Blob.from_file_path(FONT_DIR + fname + ".ttf")
        _HB[fname] = hb.Font(hb.Face(blob))
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(_HB[fname], buf, {"kern": True, "liga": False})
    pos = buf.glyph_positions
    if len(pos) != len(text):
        return None
    return [p.x_advance for p in pos]


def advances(text, size, track, fname):
    if fname is None:
        size, track = size * KSIZE, track * KTRACK
    f, gs, cmap, upm = font(fname)
    s = size / upm
    try:
        kerned = _hb_advances(text, fname or FACE)
    except Exception:
        kerned = None
    adv = [a * s for a in kerned] if kerned else [gs[cmap[ord(c)]].width * s for c in text]
    # optical spacing for wide-tracked capitals: straight I next to diagonal V/A needs less room
    for i in range(len(text) - 1):
        adv[i] += OPTICAL.get(text[i:i + 2], 0) * s
    total = sum(adv) + track * (len(text) - 1)
    return adv, total, s


def text_straight(text, x, y, size, fill, track=0, anchor="middle", fname=None):
    adv, total, s = advances(text, size, track, fname)
    x0 = x - total / 2 if anchor == "middle" else x
    d = []
    for c, a in zip(text, adv):
        p, _ = glyph_path(c, (s, 0, 0, -s, x0, y), fname)
        d.append(p)
        x0 += a + track
    return '<path fill="%s" d="%s"/>' % (fill, "".join(d)), total


def text_arc(text, cx, cy, rx, ry, size, fill, track=0, bottom=False, fname=None):
    """Text on an ellipse arc, centred at top (or bottom)."""
    adv, total, s = advances(text, size, track, fname)
    N = 4000
    sgn = 1 if bottom else -1

    def pt(t):
        return (cx + rx * math.sin(t), cy + sgn * ry * math.cos(t))

    ts = [-math.pi / 2 + math.pi * i / N for i in range(N + 1)]
    pts = [pt(t) for t in ts]
    cum = [0.0]
    for i in range(1, len(pts)):
        cum.append(cum[-1] + math.dist(pts[i], pts[i - 1]))
    mid = cum[N // 2]

    def at(sv):
        target = mid + sv
        lo, hi = 0, N
        while hi - lo > 1:
            m = (lo + hi) // 2
            if cum[m] < target:
                lo = m
            else:
                hi = m
        (x0, y0), (x1, y1) = pts[lo], pts[hi]
        return (x0 + x1) / 2, (y0 + y1) / 2, math.atan2(y1 - y0, x1 - x0)

    d = []
    pos = -total / 2
    for c, a in zip(text, adv):
        x, y, ang = at(pos + a / 2)
        ca, sa = math.cos(ang), math.sin(ang)
        # glyph (u, v up) -> centred, scaled, y flipped, rotated by ang
        m = (s * ca, s * sa, s * sa, -s * ca, x - (a / 2) * ca, y - (a / 2) * sa)
        p, _ = glyph_path(c, m, fname)
        d.append(p)
        pos += a + track
    return '<path fill="%s" d="%s"/>' % (fill, "".join(d))


# ---------------------------------------------------------------- lake
def _branch(pts):
    parts = []
    for (x0, y0, w0), (x1, y1, w1) in zip(pts, pts[1:]):
        parts.append(unary_union([Point(x0, y0).buffer(w0), Point(x1, y1).buffer(w1)]).convex_hull)
    return unary_union(parts)


def lake_geom():
    trunk = [(226, 324, 3.5), (223, 308, 6), (216, 291, 10.5), (211, 272, 9), (205, 254, 5.5),
             (203, 238, 6.5), (197, 221, 8), (191, 205, 6.5), (187, 189, 8.5), (181, 173, 12),
             (175, 157, 13), (168, 141, 10), (161, 125, 7.5), (155, 109, 7), (150, 95, 5), (145, 84, 3)]
    kraga = [(185, 182, 6), (194, 166, 5), (203, 148, 5.2), (211, 130, 4.2), (219, 112, 4.4),
             (225, 96, 3.2), (229, 83, 2.2)]
    widlagi = [(213, 282, 5), (226, 272, 4), (238, 263, 3.2), (247, 252, 2.2)]
    bays = [
        [(191, 205, 5), (179, 209, 3.8), (169, 205, 2.2)],
        [(171, 149, 6), (158, 153, 4), (150, 161, 2.2)],
        [(206, 247, 4), (195, 251, 3), (187, 259, 2)],
        [(198, 223, 4), (210, 217, 3), (218, 209, 2)],
        [(160, 122, 4), (171, 116, 3), (178, 108, 2)],
        [(220, 300, 4), (209, 306, 3), (203, 314, 2)],
    ]
    g = unary_union([_branch(b) for b in [trunk, kraga, widlagi] + bays])
    g = g.buffer(2.2).buffer(-2.2)
    isl = [affinity.rotate(affinity.scale(Point(215, 289).buffer(1), 3.6, 8.2), 18),
           Point(178, 166).buffer(2.6),
           affinity.scale(Point(173, 151).buffer(1), 2.0, 3.4),
           Point(186, 190).buffer(1.8)]
    g = g.difference(unary_union(isl))
    return g.simplify(0.25)


def _ring(coords):
    c = list(coords)[:-1]
    return "M" + "L".join("%s,%s" % (r1(x), r1(y)) for x, y in c) + "Z"


_LAKE = None


def lake_d():
    global _LAKE
    if _LAKE is None:
        g = lake_geom()
        polys = [g] if isinstance(g, Polygon) else list(g.geoms)
        d = ""
        for p in polys:
            d += _ring(p.exterior.coords)
            for i in p.interiors:
                d += _ring(i.coords)
        _LAKE = d
    return _LAKE


ILAWA = (227, 329)  # town marker at the south end

# ---------------------------------------------------------------- swan (plan view, heading up)
_SWAN_HALF = [
    ((1.6, -111), (3.4, -108), (4.4, -103)),
    ((5.4, -98), (4.6, -93), (3.6, -89)),
    ((3.0, -70), (3.2, -50), (4.4, -36)),
    ((5.4, -27), (8.5, -21), (14, -18)),
    ((26, -19), (42, -27), (56, -27)),
    ((80, -27), (108, -12), (127, 9)),
    ((122, 8.5), (117, 8.5), (113, 9.5)),
    ((116, 12), (118, 15), (119, 19)),
    ((114, 16.5), (109, 15.5), (104, 15.5)),
    ((106, 18.5), (107, 22), (107, 26)),
    ((103, 23), (98, 21), (93, 20.5)),
    ((94, 23), (94, 26), (93, 30)),
    ((84, 24), (72, 21), (60, 20.5)),
    ((44, 20), (30, 20), (20, 24)),
    ((15, 26), (12.5, 30), (12, 35)),
    ((11.5, 44), (9, 52), (7, 57)),
    ((5, 61), (2, 62), (0, 62)),
]


def swan_d():
    start = (0, -112)
    d = "M0,-112"
    for c1, c2, e in _SWAN_HALF:
        d += "C%s,%s %s,%s %s,%s" % tuple(r1(v) for v in (*c1, *c2, *e))
    # mirror: walk back
    pts = [start] + [seg[2] for seg in _SWAN_HALF]
    for i in range(len(_SWAN_HALF) - 1, -1, -1):
        c1, c2, e = _SWAN_HALF[i]
        prev = pts[i]
        d += "C%s,%s %s,%s %s,%s" % tuple(r1(v) for v in (-c2[0], c2[1], -c1[0], c1[1], -prev[0], prev[1]))
    return d + "Z"


def star(cx, cy, r, fill):
    k = r * 0.32
    return ('<path fill="%s" d="M%s,%sL%s,%sL%s,%sL%s,%sL%s,%sL%s,%sL%s,%sL%s,%sZ"/>' % (
        fill, *[r1(v) for v in (cx, cy - r, cx + k, cy - k, cx + r, cy, cx + k, cy + k,
                                cx, cy + r, cx - k, cy + k, cx - r, cy, cx - k, cy - k)]))


# ---------------------------------------------------------------- palettes
PALETTES = {
    "jezioro": dict(name="Jezioro i las", border="#8CCBE6", band="#12382E", text="#F4F1E6", land="#2F6B4F",
                    water="#8CCBE6", grid="#4C8468", swan="#FFFFFF", line="#12382E", accent="#F4C542",
                    landtext="#F4F1E6"),
    "polska": dict(name="Biało-czerwona", border="#C8102E", band="#FFFFFF", text="#14213D", land="#14213D",
                   water="#5B7DB8", grid="#2B3C63", swan="#FFFFFF", line="#14213D", accent="#C8102E",
                   landtext="#FFFFFF"),
    "zloto": dict(name="Granat i złoto", border="#C9A227", band="#0F1E3D", text="#E6C65C", land="#1A2D57",
                  water="#6F92CC", grid="#2E4577", swan="#FFFFFF", line="#0F1E3D", accent="#E6C65C",
                  landtext="#E6C65C"),
    "retro": dict(name="Retro", border="#D9722E", band="#343D20", text="#EAD9B0", land="#6F7B45",
                  water="#EAD9B0", grid="#828E57", swan="#FFFBF0", line="#343D20", accent="#D9722E",
                  landtext="#EAD9B0"),
    "mono": dict(name="Jednobarwna", border="#111111", band="#111111", text="#FFFFFF", land="#FFFFFF",
                 water="#111111", grid="none", swan="#FFFFFF", line="#111111", accent="#111111",
                 landtext="#111111"),
    "kontra": dict(name="Kontra", border="#FFFFFF", band="#FFFFFF", text="#111111", land="#111111",
                   water="#FFFFFF", grid="none", swan="#111111", line="#FFFFFF", accent="#FFFFFF",
                   landtext="#FFFFFF"),
}

_uid = [0]


def _field(p, clip_shape, lake_tf, swan_tf, grid_lines, swan_stroke=3.2):
    """Map field: land, graticule, lake, town marker, swan — clipped to clip_shape."""
    _uid[0] += 1
    cid = "c%d" % _uid[0]
    o = ['<clipPath id="%s">%s</clipPath><g clip-path="url(#%s)">' % (cid, clip_shape, cid)]
    o.append(clip_shape.replace("/>", ' fill="%s"/>' % p["land"]))
    if p["grid"] != "none":
        o.append('<g fill="none" stroke="%s" stroke-width="1.4">%s</g>' % (p["grid"], grid_lines))
    sx, tx, ty = lake_tf
    o.append('<g transform="translate(%s,%s) scale(%s)">' % (r1(tx), r1(ty), sx))
    o.append('<path fill="%s" fill-rule="evenodd" d="%s"/>' % (p["water"], lake_d()))
    o.append('<circle cx="%s" cy="%s" r="5.2" fill="%s" stroke="%s" stroke-width="2.2"/>' % (
        ILAWA[0], ILAWA[1], p["accent"], p["line"] if p["accent"] != p["line"] else p["land"]))
    o.append("</g>")
    cx, cy, sc, rot = swan_tf
    o.append('<path transform="translate(%s,%s) rotate(%s) scale(%s)" fill="%s" stroke="%s" stroke-width="%s" '
             'stroke-linejoin="round" paint-order="stroke" d="%s"/>' % (
                 r1(cx), r1(cy), rot, sc, p["swan"], p["line"], r1(swan_stroke / sc), swan_d()))
    o.append("</g>")
    return "".join(o)


def round_patch(p):
    c = 200
    grid = ('<path d="M40,150Q200,128 360,150M40,262Q200,240 360,262M128,40Q120,200 128,360'
            'M272,40Q280,200 272,360"/>')
    o = ['<circle cx="200" cy="200" r="196" fill="%s"/>' % p["border"],
         '<circle cx="200" cy="200" r="187" fill="%s"/>' % p["band"]]
    o.append(_field(p, '<circle cx="200" cy="200" r="145"/>', (0.98, -42, -1), (240, 216, 0.68, 30), grid))
    o.append('<circle cx="200" cy="200" r="145" fill="none" stroke="%s" stroke-width="3"/>' % p["border"])
    o.append(text_arc("AVIAVA", c, c, 154.5, 154.5, 37, p["text"], track=7))
    o.append(text_arc("IŁAWA", c, c, 180.5, 180.5, 37, p["text"], track=7, bottom=True))
    o.append(star(34, 200, 9, p["accent"] if p["accent"] != p["band"] else p["text"]))
    o.append(star(366, 200, 9, p["accent"] if p["accent"] != p["band"] else p["text"]))
    return "".join(o), (400, 400)


SHIELD = "M16,16H384V246C384,352 292,420 200,450C108,420 16,352 16,246Z"
SHIELD_IN = "M25,25H375V246C375,345 288,411 200,440.5C112,411 25,345 25,246Z"


def shield_patch(p):
    grid = ('<path d="M20,200Q200,178 380,200M20,320Q200,298 380,320M130,90Q122,260 130,450'
            'M270,90Q278,260 270,450"/>')
    o = ['<path d="%s" fill="%s"/>' % (SHIELD, p["border"]),
         '<path d="%s" fill="%s"/>' % (SHIELD_IN, p["band"])]
    field_shape = '<path d="M25,104H375V246C375,345 288,411 200,440.5C112,411 25,345 25,246Z"/>'
    o.append(_field(p, field_shape, (1.0, -52, 44), (266, 262, 0.80, 30), grid))
    o.append('<path d="M25,104H375" fill="none" stroke="%s" stroke-width="3"/>' % p["border"])
    o.append(text_straight("AVIAVA", 200, 85, 66, p["text"], track=10)[0])
    o.append(text_straight("IŁAWA", 200, 404, 26, p["landtext"], track=5)[0])
    return "".join(o), (400, 466)


def oval_patch(p):
    cx, cy = 170, 220
    grid = ('<path d="M20,160Q170,140 320,160M20,290Q170,270 320,290M112,30Q104,220 112,410'
            'M232,30Q240,220 232,410"/>')
    o = ['<ellipse cx="170" cy="220" rx="166" ry="216" fill="%s"/>' % p["border"],
         '<ellipse cx="170" cy="220" rx="157" ry="207" fill="%s"/>' % p["band"]]
    o.append(_field(p, '<ellipse cx="170" cy="220" rx="116" ry="166"/>', (1.08, -62, 2),
                    (206, 262, 0.60, 30), grid))
    o.append('<ellipse cx="170" cy="220" rx="116" ry="166" fill="none" stroke="%s" stroke-width="3"/>' % p["border"])
    o.append(text_arc("AVIAVA", cx, cy, 125.5, 175.5, 36, p["text"], track=8))
    o.append(text_arc("IŁAWA", cx, cy, 150.5, 200.5, 36, p["text"], track=8, bottom=True))
    st = p["accent"] if p["accent"] != p["band"] else p["text"]
    o.append(star(33.5, 220, 8, st))
    o.append(star(306.5, 220, 8, st))
    return "".join(o), (340, 440)


def sygnet(p):
    """Small-size mark: swan only, no text."""
    o = ['<circle cx="200" cy="200" r="196" fill="%s"/>' % p["border"],
         '<circle cx="200" cy="200" r="172" fill="%s"/>' % p["land"]]
    sw = p["swan"] if p["swan"] != p["land"] else p["line"]
    o.append('<path transform="translate(196,222) rotate(30) scale(1.22)" fill="%s" d="%s"/>' % (sw, swan_d()))
    return "".join(o), (400, 400)


def wordmark(fill, sub_fill, w=560):
    a, tw = text_straight("AVIAVA", 0, 150, 190, fill, track=14, anchor="start")
    b, _ = text_straight("IŁAWA", 3, 214, 44, sub_fill, track=22, anchor="start", fname="BarlowCondensed-SemiBold")
    return a + b, (math.ceil(tw) + 4, 230)


SHAPES = {"round": round_patch, "shield": shield_patch, "oval": oval_patch, "sygnet": sygnet}


def svg(shape, pal, width=None, label=None, extra=""):
    body, (w, h) = SHAPES[shape](PALETTES[pal])
    wa = ' width="%s" height="%s"' % (width, r1(width * h / w)) if width else ""
    lab = label or "Logo Aviava"
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d"%s role="img" aria-label="%s"%s>%s</svg>'
            % (w, h, wa, lab, extra, body))


if __name__ == "__main__":
    import cairosvg, sys
    cells = []
    x = 0
    for sh, pal in [("round", "jezioro"), ("shield", "polska"), ("oval", "zloto"), ("round", "retro"),
                    ("round", "mono"), ("round", "kontra"), ("sygnet", "jezioro")]:
        body, (w, h) = SHAPES[sh](PALETTES[pal])
        cells.append('<g transform="translate(%d,%d)">%s</g>' % (x % 1720, 20 + (x // 1720) * 500, body))
        x += 430
    wm, (ww, wh) = wordmark("#12382E", "#2F6B4F")
    cells.append('<g transform="translate(1300,560)">%s</g>' % wm)
    doc = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1900 1020" width="1900" height="1020">'
           '<rect width="1900" height="1020" fill="#cfcfcf"/>%s</svg>' % "".join(cells))
    open("export/preview.svg", "w").write(doc)
    cairosvg.svg2png(bytestring=doc.encode(), write_to="export/preview.png")
    print(len(lake_d()), len(swan_d()))
