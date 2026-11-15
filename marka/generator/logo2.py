"""Aviava logo generator, version 0.2.

Parts:
- lake: real outline of Jeziorak, Jezioro Plaskie and Maly Jeziorak (jeziorak_data.py),
  one water colour, no city boundary;
- swan: side view in flight, wings arched like the gulls of glider badges;
- texts: Brygada 1918, converted to curves (logo.text_arc, logo.text_straight);
- waves: ten wavy stripes, white and blue, as in the flag of Ilawa.
"""
import math
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union
from shapely import affinity

import logo
import lake_build
import jeziorak_data as J

FB = "Brygada1918-Bold"
FS = "Brygada1918-SemiBold"


def r1(v):
    return ("%.1f" % v).rstrip("0").rstrip(".")


def geom_d(g):
    polys = [g] if g.geom_type == "Polygon" else list(g.geoms)
    d = []
    for p in polys:
        for ring in [p.exterior] + list(p.interiors):
            c = list(ring.coords)[:-1]
            d.append("M" + "L".join("%s,%s" % (r1(x), r1(y)) for x, y in c) + "Z")
    return "".join(d)


# ---------------------------------------------------------------- lake
def lake_geom(min_island=1500, tol=1.6):
    shores = [lake_build.poly(J.JEZIORAK[1]), lake_build.poly(J.PLASKIE[0]),
              lake_build.poly(J.MALY_JEZIORAK[0]), lake_build.poly(J.ZATOKA[0])]
    water = unary_union(shores).buffer(0.6).buffer(-0.6)
    for r in [J.JEZIORAK[0]] + J.JEZIORAK[2:] + J.PLASKIE[1:]:
        isl = lake_build.poly(r)
        if isl.area >= min_island:
            water = water.difference(isl)
    # Fill the small islands that were dropped, then simplify.
    out = Polygon(water.exterior, [i for i in water.interiors if Polygon(i).area >= min_island])
    return out.simplify(tol, preserve_topology=True)


_LAKE = {}


def lake_placed(cx, cy, height, rot=0, tol=1.6):
    """Lake scaled to `height`, centred on (cx, cy). Returns (geometry, town point)."""
    key = (cx, cy, height, rot, tol)
    if key not in _LAKE:
        g = lake_geom(tol=tol)
        minx, miny, maxx, maxy = g.bounds
        s = height / (maxy - miny)
        mx, my = (minx + maxx) / 2, (miny + maxy) / 2
        g = affinity.translate(g, -mx, -my)
        g = affinity.scale(g, s, s, origin=(0, 0))
        g = affinity.rotate(g, rot, origin=(0, 0))
        g = affinity.translate(g, cx, cy)
        town = Point((166.0 - mx) * s, (1068.0 - my) * s)  # Ilawa centre, south of Maly Jeziorak
        town = affinity.translate(affinity.rotate(town, rot, origin=(0, 0)), cx, cy)
        _LAKE[key] = (g, (town.x, town.y))
        _LAKE_T[key] = (mx, my, s, rot, cx, cy)
    return _LAKE[key]


_LAKE_T = {}


def place_like_lake(geom, cx, cy, height, rot=0, tol=1.6):
    lake_placed(cx, cy, height, rot, tol)
    mx, my, s, rot, cx, cy = _LAKE_T[(cx, cy, height, rot, tol)]
    g = affinity.translate(geom, -mx, -my)
    g = affinity.scale(g, s, s, origin=(0, 0))
    g = affinity.rotate(g, rot, origin=(0, 0))
    return affinity.translate(g, cx, cy)


# ---------------------------------------------------------------- swan
def _taper(pts, w0, w1):
    parts = []
    n = len(pts) - 1
    for i in range(n):
        a = w0 + (w1 - w0) * i / n
        b = w0 + (w1 - w0) * (i + 1) / n
        parts.append(unary_union([Point(pts[i]).buffer(a / 2), Point(pts[i + 1]).buffer(b / 2)]).convex_hull)
    return unary_union(parts)


def swan_geom():
    """Mute swan in flight, side view, heading right. Unit box about 210 x 120."""
    body = affinity.rotate(affinity.scale(Point(0, 0).buffer(1, 64), 34, 12.5), -4, origin=(0, 0))
    neck = _taper([(20, -4), (42, -8), (62, -11), (80, -13), (90, -13.5)], 11, 7)
    head = affinity.rotate(affinity.scale(Point(94, -13.5).buffer(1, 48), 7.6, 5.2), 8, origin=(94, -13.5))
    knob = Point(100.5, -15.6).buffer(2.2)
    bill = Polygon([(98.5, -17.4), (113, -11.6), (112.6, -10.0), (98.5, -10.2)])
    tail = Polygon([(-28, -5), (-46, -6), (-43, -1), (-46, 4), (-28, 6)])
    # near wing, upstroke: arm rises from the back, hand sweeps back, five primaries
    arm = Polygon([(14, -8), (12, -30), (6, -52), (-4, -70), (-14, -82), (-24, -86),
                   (-30, -74), (-30, -56), (-26, -36), (-20, -16), (-10, -8)])
    hand = Polygon([(-14, -82), (-24, -86), (-42, -88), (-62, -86), (-86, -80), (-106, -72),
                    (-58, -60), (-36, -50), (-26, -40)])
    feathers = []
    for k, (tx, ty) in enumerate([(-112, -70), (-106, -60), (-96, -50), (-84, -41), (-70, -33)]):
        bx = -58 + 9 * k
        by = -72 + 8 * k
        feathers.append(_taper([(bx, by), (tx, ty)], 9, 4))
    secondaries = Polygon([(-26, -40), (-36, -50), (-58, -60), (-62, -40), (-52, -24), (-38, -12),
                           (-24, -6)])
    wing = unary_union([arm, hand, secondaries] + feathers).buffer(2.5).buffer(-2.5)
    g = unary_union([body, neck, head, knob, bill, tail, wing])
    g = g.buffer(1.0).buffer(-1.0)
    return affinity.translate(g, 4, 30)


_SWAN = None
SWAN_VARIANT = "I"


def swan_geom_v():
    import swans
    fn = dict((k, f) for k, _, f in swans.VARIANTS)[SWAN_VARIANT]
    g = fn()
    x0, y0, x1, y1 = g.bounds
    s = 227 / (x1 - x0)
    g = affinity.translate(g, -(x0 + x1) / 2, -(y0 + y1) / 2)
    return affinity.translate(affinity.scale(g, s, s, origin=(0, 0)), 3.5, -7.6)


def swan_d():
    global _SWAN
    if _SWAN is None:
        _SWAN = geom_d(swan_geom_v().simplify(0.25))
    return _SWAN


GAP_MIN = 5.6   # normalized swan units ~ 1.1 mm at a 100 mm patch


def open_gaps(g, gap=GAP_MIN, near=None, radius=55):
    """Widen every narrow notch (feather separations, wing/body notch) to at least `gap`, so the graphic
    and the embroidered versions show the same notches."""
    closed = g.buffer(gap / 2, 16).buffer(-gap / 2, 16)
    notches = closed.difference(g)
    parts = [n for n in getattr(notches, "geoms", [notches]) if n.geom_type == "Polygon" and n.area > 1.0
             and (near is None or n.centroid.distance(near) < radius)]
    if not parts:
        return g
    cut = unary_union(parts).buffer(gap * 0.32, 16)
    return g.difference(cut).buffer(0.4, 16).buffer(-0.4, 16)


def _swan_layers():
    import swans
    far, main = swans.swan_i_parts() if SWAN_VARIANT == "I" else (None, swan_geom_v())
    whole = unary_union([g for g in (far, main) if g is not None])
    x0, y0, x1, y1 = whole.bounds
    s = 227 / (x1 - x0)
    def norm(g):
        g = affinity.translate(g, -(x0 + x1) / 2, -(y0 + y1) / 2)
        return affinity.translate(affinity.scale(g, s, s, origin=(0, 0)), 3.5, -7.6)
    global SWAN_ANCHORS
    SWAN_ANCHORS = {k: norm(Point(*v)).coords[0] for k, v in dict(body=(0, 0), chest=(28, 0), head=(118, -12)).items()}
    global SWAN_GEOMS
    body_pt = norm(Point(0, 0))
    SWAN_GEOMS = [open_gaps(norm(g), near=body_pt) for g in (far, main) if g is not None]
    return [geom_d(g.simplify(0.25)) for g in SWAN_GEOMS]


_SL = None


def _swan_layers_cached():
    global _SL
    if _SL is None:
        _SL = _swan_layers()
    return _SL


def swan(cx, cy, scale, rot, fill, stroke=None, sw=0):
    """Swan drawn with an explicit outline: the outline is the shape grown by sw/2 and the white is the
    shape shrunk by sw/2, so the look does not depend on SVG paint-order support."""
    scale = float(scale)
    _swan_layers_cached()
    tr = 'transform="translate(%s,%s) rotate(%s) scale(%s)"' % (r1(cx), r1(cy), rot, r1(scale))
    out = []
    for g in SWAN_GEOMS:
        if stroke and stroke != "none" and sw:
            h = sw / scale / 2
            out.append('<path %s fill="%s" d="%s"/>' % (tr, stroke, geom_d(g.buffer(h, 16).simplify(0.25))))
            out.append('<path %s fill="%s" d="%s"/>' % (tr, fill, geom_d(g.buffer(-h, 16).simplify(0.25))))
        else:
            out.append('<path %s fill="%s" d="%s"/>' % (tr, fill, geom_d(g.simplify(0.25))))
    return "".join(out)


def _swan_old(cx, cy, scale, rot, fill, stroke=None, sw=0):
    s = ""
    if stroke:
        s = ' stroke="%s" stroke-width="%s" stroke-linejoin="round" paint-order="stroke"' % (stroke, r1(sw / scale))
    return '<path transform="translate(%s,%s) rotate(%s) scale(%s)" fill="%s"%s d="%s"/>' % (
        r1(cx), r1(cy), rot, scale, fill, s, swan_d())


def gull(cx, cy, w, fill):
    """Small gull, front view, as on glider badges (own drawing, not a copy)."""
    h = w * 0.28
    d = ("M{a},{b}Q{c},{d} {e},{f}Q{g},{h1} {i},{j}Q{k},{l} {m},{n}Q{o},{p} {q},{r}Q{s},{t} {u},{v}"
         "Q{w1},{x} {a},{b}Z").format(
        a=r1(cx - w / 2), b=r1(cy + h * 0.15), c=r1(cx - w * 0.3), d=r1(cy - h), e=r1(cx), f=r1(cy + h * 0.25),
        g=r1(cx + w * 0.3), h1=r1(cy - h), i=r1(cx + w / 2), j=r1(cy + h * 0.15),
        k=r1(cx + w * 0.3), l=r1(cy - h * 0.55), m=r1(cx + w * 0.03), n=r1(cy + h * 0.65),
        o=r1(cx), p=r1(cy + h * 0.75), q=r1(cx - w * 0.03), r=r1(cy + h * 0.65),
        s=r1(cx - w * 0.15), t=r1(cy + h * 0.2), u=r1(cx - w * 0.3), v=r1(cy - h * 0.55),
        w1=r1(cx - w * 0.4), x=r1(cy - h * 0.3))
    return '<path fill="%s" d="%s"/>' % (fill, d)


def star(cx, cy, r, fill):
    return logo.star(cx, cy, r, fill)


def waves(x, y, w, h, n=10, c1="#FFFFFF", c2="#2E6DB4", amp=None, periods=3, clip=None):
    """n wavy horizontal stripes, alternating c1 and c2, top stripe c1 (flag of Ilawa)."""
    sh = h / n
    amp = amp if amp is not None else sh * 0.32
    out = ['<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (r1(x), r1(y), r1(w), r1(h), c1)]
    seg = w / (periods * 2)
    for i in range(1, n, 2):
        y0, y1 = y + i * sh, y + (i + 1) * sh

        def wave(yy, rev=False):
            pts = []
            for k in range(periods * 2):
                xa = x + k * seg
                sgn = -1 if k % 2 == 0 else 1
                pts.append("Q%s,%s %s,%s" % (r1(xa + seg / 2), r1(yy + sgn * amp * 2), r1(xa + seg), r1(yy)))
            return pts
        top = "M%s,%s" % (r1(x - 1), r1(y0)) + "L%s,%s" % (r1(x), r1(y0)) + "".join(wave(y0))
        bot_pts = []
        for k in range(periods * 2 - 1, -1, -1):
            xa = x + k * seg
            sgn = -1 if k % 2 == 0 else 1
            bot_pts.append("Q%s,%s %s,%s" % (r1(xa + seg / 2), r1(y1 + sgn * amp * 2), r1(xa), r1(y1)))
        if i == n - 1:
            d = top + "L%s,%s" % (r1(x + w + 1), r1(y1 + 1)) + "L%s,%s" % (r1(x - 1), r1(y1 + 1)) + "Z"
        else:
            d = top + "L%s,%s" % (r1(x + w), r1(y1)) + "".join(bot_pts) + "Z"
        out.append('<path fill="%s" d="%s"/>' % (c2, d))
    g = "".join(out)
    if clip:
        logo._uid[0] += 1
        cid = "w%d" % logo._uid[0]
        g = '<clipPath id="%s">%s</clipPath><g clip-path="url(#%s)">%s</g>' % (cid, clip, cid, g)
    return g


# ---------------------------------------------------------------- palettes
PAL = {
    "szybowcowa": dict(name="Odznaka szybowcowa", rim="#C9CED6", band="#0F2A57", text="#FFFFFF",
                       field="#1F4E9C", water="#BFD6F2", swan="#FFFFFF", line="#0F2A57", accent="#C9CED6",
                       town="#E0A526"),
    "zlota": dict(name="Złota odznaka", rim="#D9A62E", band="#0F2A57", text="#F2D27A",
                  field="#1F4E9C", water="#BFD6F2", swan="#FFFFFF", line="#0F2A57", accent="#D9A62E",
                  town="#D9A62E"),
    "nocna": dict(name="Nocny Jeziorak", rim="#C9A227", band="#070F1C", text="#E6C65C",
                  field="#0E1A2B", water="#E0A526", swan="#FFFFFF", line="#0E1A2B", accent="#E6C65C",
                  town="#FFFFFF"),
    "brama": dict(name="Brama", rim="#D9A62E", band="#0F2A57", text="#F2D27A",
                  field="#2E6DB4", water="#0F2A57", swan="#FFFFFF", line="#0F2A57", accent="#D9A62E",
                  town="#D9A62E"),
    "mono": dict(name="Jednobarwna", rim="#111111", band="#111111", text="#FFFFFF",
                 field="#FFFFFF", water="#111111", swan="#FFFFFF", line="#111111", accent="#111111",
                 town="#FFFFFF"),
}


def _clip(shape):
    logo._uid[0] += 1
    cid = "k%d" % logo._uid[0]
    return cid, '<clipPath id="%s">%s</clipPath>' % (cid, shape)


def lake_fit_circle(ccx, ccy, r, margin=8, tol=1.6):
    """Lake (with the town dot) inscribed in a circle: its minimum enclosing circle is made concentric
    with the field and its radius set to r - margin, so the margin is equal at every touching point.
    Returns (cx, cy, height) in lake_placed's convention."""
    import shapely
    g = lake_geom(tol=tol)
    minx, miny, maxx, maxy = g.bounds
    mec = shapely.minimum_bounding_circle(g)
    mc = mec.centroid
    mr = math.sqrt(mec.area / math.pi)
    s = (r - margin) / mr
    bx, by = (minx + maxx) / 2, (miny + maxy) / 2
    return ccx + (bx - mc.x) * s, ccy + (by - mc.y) * s, (maxy - miny) * s


def lake_fit_vertical(ccx, ccy, r, margin=10, nudge_x=16, tol=1.6):
    """Keep the horizontal position of the optical fit (nudged right), then set height and vertical
    position so that the top and bottom clearances to the circle are equal and no side is closer."""
    cx0, _, h0 = lake_fit(Point(ccx, ccy).buffer(r, 256), margin, nudge=(nudge_x, 0))
    dx = cx0 - ccx

    def clear(cy, h):
        g, t = lake_placed(ccx + dx, cy, h, tol=tol)
        pts = [p for ring in [g.exterior] for p in ring.coords]
        top = min(r - math.hypot(x - ccx, y - ccy) for x, y in pts if y <= ccy)
        bot = min(r - math.hypot(x - ccx, y - ccy) for x, y in pts if y > ccy)
        return top, bot

    def level(h):
        lo, hi = ccy - 60, ccy + 60
        for _ in range(40):
            m = (lo + hi) / 2
            t, b = clear(m, h)
            if t < b:
                lo = m
            else:
                hi = m
        return (lo + hi) / 2

    lo, hi = h0 * 0.8, h0 * 1.4
    for _ in range(25):
        h = (lo + hi) / 2
        cy = level(h)
        t, b = clear(cy, h)
        if min(t, b) >= margin:
            lo = h
        else:
            hi = h
    return ccx + dx, level(lo), lo


def lake_fit(container, margin=7, rot=0, tol=1.6, nudge=(0, 0)):
    """Largest lake that fits in `container` (shapely polygon) with `margin`, with its optical centre
    (half bounding-box centre, half area centroid) on the container's centroid. Returns (cx, cy, height)."""
    g = lake_geom(tol=tol)
    minx, miny, maxx, maxy = g.bounds
    bx, by = (minx + maxx) / 2, (miny + maxy) / 2
    ax, ay = g.centroid.x, g.centroid.y
    ox, oy = (bx + ax) / 2, (by + ay) / 2
    c = container.centroid
    tx, ty = c.x + nudge[0], c.y + nudge[1]
    inner = container.buffer(-margin)
    lo, hi = 50.0, 600.0
    for _ in range(30):
        h = (lo + hi) / 2
        s = h / (maxy - miny)
        t = affinity.scale(affinity.translate(g, -ox, -oy), s, s, origin=(0, 0))
        t = affinity.rotate(t, rot, origin=(0, 0))
        t = affinity.translate(t, tx, ty)
        if inner.contains(t):
            lo = h
        else:
            hi = h
    s = lo / (maxy - miny)
    # convert to lake_placed's convention (bbox centre)
    dx, dy = (bx - ox) * s, (by - oy) * s
    return tx + dx, ty + dy, lo


def _lake_svg(p, cx, cy, height, rot=0, town=True, tol=1.6):
    g, _ = lake_placed(cx, cy, height, rot, tol)
    o = '<path fill="%s" fill-rule="evenodd" d="%s"/>' % (p["water"], geom_d(g))
    if town:
        # Ilawa: Maly Jeziorak painted in the town colour (graphic versions only, not embroidery)
        mj = place_like_lake(lake_build.poly(J.MALY_JEZIORAK[0]).buffer(0.6).simplify(tol), cx, cy, height, rot, tol)
        o += '<path fill="%s" d="%s"/>' % (p["town"], geom_d(mj))
    return o


# ---------------------------------------------------------------- shared field content
def gull_svg(cx, cy, size, rot, fill):
    import swans
    g = swans.gull_side()
    x0, y0, x1, y1 = g.bounds
    s = size / (x1 - x0)
    g = affinity.translate(g, -(x0 + x1) / 2, -(y0 + y1) / 2)
    g = affinity.rotate(affinity.scale(g, s, s, origin=(0, 0)), rot, origin=(0, 0))
    return '<path fill="%s" d="%s"/>' % (fill, geom_d(affinity.translate(g, cx, cy)))


SWAN_ROT = -12


def _rot(pt, deg):
    a = math.radians(deg)
    return (pt[0] * math.cos(a) - pt[1] * math.sin(a), pt[0] * math.sin(a) + pt[1] * math.cos(a))


def flock(lake_g, container, by_off=26, gap=16, reach=34, kmin=0.78):
    """Swan with its body left of the lake and its neck across it; returns (cx, cy, scale)."""
    _swan_layers_cached()
    c = container.centroid
    by = c.y + by_off
    row = lake_g.intersection(LineString([(c.x - 400, by), (c.x + 400, by)]))
    xl, _, xr, _ = row.bounds
    A = SWAN_ANCHORS
    rot = SWAN_ROT
    ch = _rot(A["chest"], rot)
    hd = _rot(A["head"], rot)
    bd = _rot(A["body"], rot)
    # head beyond right shore + reach; chest at left shore - gap
    k = max(kmin, ((xr + reach) - (xl - gap)) / (hd[0] - ch[0]))
    cx = (xl - gap) - ch[0] * k
    cy = by - bd[1] * k
    return cx, cy, k


def field(p, container, clip_svg, gulls=False, stars=False, margin=8, by_off=26, gull_k=1.0, nudge=(0, 0), circle=None, town=True):
    """Lake fitted and optically centred in the container; swan leading a V of gulls (klucz)."""
    if circle:
        cx, cy, h = lake_fit_vertical(circle[0], circle[1], circle[2], margin)
    else:
        cx, cy, h = lake_fit(container, margin, nudge=nudge)
    lake_g, _ = lake_placed(cx, cy, h)
    cid, cl = _clip(clip_svg)
    o = [cl + '<g clip-path="url(#%s)">' % cid, clip_svg.replace("/>", ' fill="%s"/>' % p["field"])]
    if stars:
        c = container.centroid
        for (dx, dy, r) in [(-98, -60, 3.0), (-62, -100, 2.4), (62, -100, 2.4), (98, -60, 3.0)]:
            if container.buffer(-10).contains(Point(c.x + dx, c.y + dy)):
                o.append(star(c.x + dx, c.y + dy, r * STAR_K, p["text"]))
    o.append(_lake_svg(p, cx, cy, h, town=town))
    sx, sy, k = flock(lake_g, container, by_off=by_off)
    if gulls:
        # three gulls in one line along the east shore, halfway between the shore and the edge
        c = container.centroid
        A = SWAN_ANCHORS
        hx, hy = _rot((A["head"][0] * k, A["head"][1] * k), SWAN_ROT)
        y0 = sy + hy + 34
        for i, (dy, w) in enumerate([(0, 25), (34, 21), (66, 17)]):
            y = y0 + dy
            row = lake_g.buffer(2).intersection(LineString([(c.x - 400, y), (c.x + 400, y)]))
            edge = container.buffer(-4).intersection(LineString([(c.x, y), (c.x + 400, y)]))
            if row.is_empty or edge.is_empty:
                continue
            x = (row.bounds[2] + edge.bounds[2]) / 2
            if container.buffer(-12).contains(Point(x, y)):
                o.append(gull_svg(x, y, w * gull_k, SWAN_ROT, p["swan"]))
    o.append(swan(sx, sy, k, SWAN_ROT, p["swan"], p["line"], 4))
    o.append('</g>')
    return "".join(o)


def _circle(cx, cy, r):
    return Point(cx, cy).buffer(r, 128)


# ---------------------------------------------------------------- 1. round patch
RIM_W = 12          # rim = merrow border: 3 mm at 100 mm
RING_W = 5.2        # line between field and band: 1.3 mm at 100 mm
STAR_K = 2.0        # field stars: radius factor (arms at least 1 mm wide at 100 mm)


def round_patch(p, gulls=True, stars=True, town=True):
    o = ['<circle cx="200" cy="200" r="199" fill="%s"/>' % p["rim"],
         '<circle cx="200" cy="200" r="%s" fill="%s"/>' % (199 - RIM_W, p["band"])]
    o.append(field(p, _circle(200, 200, 143), '<circle cx="200" cy="200" r="143"/>', gulls=gulls, stars=stars,
                   by_off=40, circle=(200, 200, 143), margin=16, town=town))
    o.append('<circle cx="200" cy="200" r="143" fill="none" stroke="%s" stroke-width="%s"/>' % (p["rim"], RING_W))
    o.append(logo.text_arc("AVIAVA", 200, 200, 153, 153, 40, p["text"], track=9, fname=FB))
    o.append(logo.text_arc("IŁAWA", 200, 200, 181, 181, 40, p["text"], track=9, bottom=True, fname=FB))
    o.append(star(200 - 165.6, 200, 10, p["accent"]))
    o.append(star(200 + 165.6, 200, 10, p["accent"]))
    return "".join(o), (400, 400)


# ---------------------------------------------------------------- 2. gate (gothic arch)
def _arch(x0, x1, ybase, ytop, ystart):
    w = x1 - x0
    h = ystart - ytop
    rr = max((w * w + 4 * h * h) / (4 * w), w / 2)
    return "M%s,%sV%sA%s,%s 0 0 1 %s,%sA%s,%s 0 0 1 %s,%sV%sZ" % (
        r1(x0), r1(ybase), r1(ystart), r1(rr), r1(rr), r1((x0 + x1) / 2), r1(ytop),
        r1(rr), r1(rr), r1(x1), r1(ystart), r1(ybase))


def _arch_poly(x0, x1, ybase, ytop, ystart, n=60):
    w = x1 - x0
    h = ystart - ytop
    rr = max((w * w + 4 * h * h) / (4 * w), w / 2)
    lc, rc = (x0 + rr, ystart), (x1 - rr, ystart)
    a_end = math.atan2(ytop - ystart, (x0 + x1) / 2 - lc[0])
    pts = [(x0, ybase), (x0, ystart)]
    for i in range(1, n + 1):
        a = math.pi + (a_end + 2 * math.pi - math.pi) * i / n if a_end < 0 else math.pi
        pts.append((lc[0] + rr * math.cos(a), lc[1] + rr * math.sin(a)))
    for p in reversed(pts[2:]):
        pts.append((x0 + x1 - p[0], p[1]))
    pts.append((x1, ybase))
    return Polygon(pts).buffer(0)


def gate_patch(p):
    W, H = 360, 470
    outer = _arch(6, 354, 464, 6, 190)
    inner = _arch(16, 344, 454, 20, 194)
    win = _arch(70, 290, 382, 92, 222)
    o = ['<path d="%s" fill="%s"/>' % (outer, p["rim"]), '<path d="%s" fill="%s"/>' % (inner, p["band"])]
    o.append(field(p, _arch_poly(70, 290, 382, 92, 222), '<path d="%s"/>' % win, margin=9, by_off=40))
    o.append('<path d="%s" fill="none" stroke="%s" stroke-width="9"/>' % (win, p["rim"]))
    o.append('<path d="M60,382H300" stroke="%s" stroke-width="9"/>' % p["rim"])
    o.append(logo.text_straight("AVIAVA", 180, 438, 52, p["text"], track=9, fname=FB)[0])
    o.append(logo.text_arc("IŁAWA", 180, 232, 133, 165, 30, p["text"], track=8, fname=FB))
    return "".join(o), (W, H)


# ---------------------------------------------------------------- 3. rhombus
def rhomb_patch(p):
    o = ['<path d="M200,4L396,200L200,396L4,200Z" fill="%s"/>' % p["rim"],
         '<path d="M200,17L383,200L200,383L17,200Z" fill="%s"/>' % p["band"]]
    fieldd = "M200,64L336,200L200,336L64,200Z"
    o.append(field(p, Polygon([(200, 64), (336, 200), (200, 336), (64, 200)]), '<path d="%s"/>' % fieldd, margin=8, by_off=22))
    o.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.5"/>' % (fieldd, p["rim"]))
    o.append(_edge_text("AVIAVA", (60, 180.5), (180.5, 60), 30, p["text"]))
    o.append(_edge_text("IŁAWA", (219.5, 60), (339.5, 180.5), 30, p["text"]))
    o.append(star(200, 360, 9, p["accent"]))
    o.append(star(40, 200, 7, p["accent"]))
    o.append(star(360, 200, 7, p["accent"]))
    return "".join(o), (400, 400)


def _text_on_line(text, a, b, size, fill, flip=False, whole=None):
    if whole:  # lower edges: write IŁAWA along the bottom-left and bottom-right edges as one word, split
        o = _edge_text("IŁA", (52, 236), (178, 362), size, fill)
        o += _edge_text("WA", (222, 362), (348, 236), size, fill)
        return o
    return _edge_text(text, a, b, size, fill)


def _edge_text(text, a, b, size, fill):
    (x0, y0), (x1, y1) = a, b
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    t, _ = logo.text_straight(text, 0, size * 0.36, size, fill, track=8, fname=FB)
    return '<g transform="translate(%s,%s) rotate(%s)">%s</g>' % (r1(cx), r1(cy), r1(ang), t)


# ---------------------------------------------------------------- applications with waves
def flag(p):
    """Flag 5:8 — the ten waves of the flag of Ilawa, patch in the hoist."""
    W, H = 640, 400
    o = [waves(0, 0, W, H, 10, "#FFFFFF", "#2E6DB4", periods=4)]
    body, _ = round_patch(p, gulls=True)
    o.append('<g transform="translate(40,40) scale(0.8)">%s</g>' % body)
    return "".join(o), (W, H)


def pennant(p):
    """Triangular pennant: patch at the hoist, waves running to the tip."""
    W, H = 640, 300
    tri = "M0,0L640,150L0,300Z"
    o = [waves(0, 0, W, H, 10, "#FFFFFF", "#2E6DB4", periods=4, clip='<path d="%s"/>' % tri)]
    o.append('<path d="M0,0V300" stroke="%s" stroke-width="14"/>' % p["band"])
    body, _ = round_patch(p, gulls=True)
    o.append('<g transform="translate(26,40) scale(0.55)">%s</g>' % body)
    return "".join(o), (W, H)


def pin_badge(p):
    """Enamel pin: round mark over a plain ribbon (the waves are reserved for flags)."""
    W, H = 420, 470
    o = []
    rib = "M14,330C80,300 340,300 406,330L380,404L406,456C340,430 80,430 14,456L40,404Z"
    o.append('<path d="%s" fill="%s" transform="translate(0,4)"/>' % (rib, p["rim"]))
    o.append('<path d="%s" fill="%s" stroke="%s" stroke-width="5"/>' % (rib, p["band"], p["rim"]))
    body, _ = round_patch(p)
    o.append('<g transform="translate(40,10) scale(0.85)">%s</g>' % body)
    return "".join(o), (W, H)


def field_content(p):
    """The patch field exactly as in the patch (lake, Ilawa, stars, swan, klucz of gulls), without the
    circular clip, in patch units (field centre 200,200, radius 143)."""
    import re
    g = field(p, _circle(200, 200, 143), '<circle cx="200" cy="200" r="143"/>', gulls=True, stars=True,
              by_off=40, circle=(200, 200, 143), margin=16, town=True)
    g = re.sub(r'<clipPath id="[^"]+">.*?</clipPath>', "", g, count=1)
    g = re.sub(r' clip-path="url\(#[^)]+\)"', "", g, count=1)
    return g


def sygnet(p):
    """Swan alone, optically centred in the circle."""
    import swans
    o = ['<circle cx="200" cy="200" r="197" fill="%s"/>' % p["rim"],
         '<circle cx="200" cy="200" r="178" fill="%s"/>' % p["field"]]
    _swan_layers_cached()
    # normalised swan geometry, as drawn by swan(): measure it after rotation
    far, main = swans.swan_i_parts()
    whole = unary_union([far, main])
    x0, y0, x1, y1 = whole.bounds
    s0 = 227 / (x1 - x0)
    g = affinity.translate(whole, -(x0 + x1) / 2, -(y0 + y1) / 2)
    g = affinity.translate(affinity.scale(g, s0, s0, origin=(0, 0)), 3.5, -7.6)
    g = affinity.rotate(g, SWAN_ROT, origin=(0, 0))
    gx0, gy0, gx1, gy1 = g.bounds
    k = 1.0
    for _ in range(30):
        t = affinity.scale(g, k, k, origin=(0, 0))
        bx, by = (gx0 + gx1) / 2 * k, (gy0 + gy1) / 2 * k
        # optical centre: halfway between bbox centre and area centroid
        ox, oy = (bx + t.centroid.x) / 2, (by + t.centroid.y) / 2
        t = affinity.translate(t, 200 - ox, 200 - oy)
        if Point(200, 200).buffer(178 - 22).contains(t):
            k *= 1.03
        else:
            k /= 1.03
            break
    t = affinity.scale(g, k, k, origin=(0, 0))
    bx, by = (gx0 + gx1) / 2 * k, (gy0 + gy1) / 2 * k
    ox, oy = (bx + t.centroid.x) / 2, (by + t.centroid.y) / 2
    o.append(swan(200 - ox, 200 - oy, k, SWAN_ROT, p["swan"], p["field"], 6))
    return "".join(o), (400, 400)


def wordmark(fill, sub):
    a, tw = logo.text_straight("AVIAVA", 0, 150, 180, fill, track=12, anchor="start", fname=FB)
    b, _ = logo.text_straight("IŁAWA", 4, 212, 46, sub, track=26, anchor="start", fname=FS)
    return a + b, (math.ceil(tw) + 4, 230)


def svg(body_wh, label="Logo Aviava", width=None):
    body, (w, h) = body_wh
    wa = ' width="%s" height="%s"' % (width, r1(width * h / w)) if width else ""
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d"%s role="img" aria-label="%s">%s</svg>'
            % (w, h, wa, label, body))


# ---------------------------------------------------------------- embroidery version
def swan_placed(cx, cy, scale, rot):
    _swan_layers_cached()
    out = []
    for g in SWAN_GEOMS:
        g = affinity.scale(g, scale, scale, origin=(0, 0))
        g = affinity.rotate(g, rot, origin=(0, 0))
        out.append(affinity.translate(g, cx, cy))
    return out


def _closing(g, r):
    return g.buffer(r, 16).buffer(-r, 16)


def _opening(g, r):
    return g.buffer(-r, 16).buffer(r, 16)


def haft_patch(p, D=100.0, minw_mm=1.3, gap_mm=1.3, dot_mm=3.0, merrow_mm=3.0):
    """Embroidery version for a patch of diameter D mm. Detail below the embroidery limits is removed:
    no islands, no gulls, no stars in the field, Maly Jeziorak as a dot, closed narrow gaps,
    outlines and rings at least minw wide, a merrow border instead of the thin rim."""
    u = D / 400.0                     # mm per unit
    w, gp = minw_mm / u, gap_mm / u   # in units
    merrow = merrow_mm / u
    o = ['<circle cx="200" cy="200" r="199" fill="%s"/>' % p["rim"],
         '<circle cx="200" cy="200" r="%s" fill="%s"/>' % (r1(199 - merrow), p["band"])]
    field_r = 143
    container = _circle(200, 200, field_r)
    cx, cy, h = lake_fit_vertical(200, 200, field_r, 16)
    lake_g, _ = lake_placed(cx, cy, h)
    # islands out, Maly Jeziorak and its canal out, narrow bays closed, thin parts thickened
    lake = Polygon(lake_g.exterior)
    mj = place_like_lake(lake_build.poly(J.MALY_JEZIORAK[0]), cx, cy, h)
    lake = lake.difference(mj.buffer(gp))
    lake = _closing(lake, gp / 2)
    lake = lake.buffer(w * 0.18, 16)
    parts = [g for g in (lake.geoms if lake.geom_type == "MultiPolygon" else [lake]) if g.area > (2 * w) ** 2]
    lake = unary_union(parts).simplify(0.5)
    lake = Polygon(lake.exterior) if lake.geom_type == "Polygon" else lake
    dot = Point(mj.centroid.x, mj.centroid.y).buffer(dot_mm / u / 2, 32)
    cid, cl = _clip('<circle cx="200" cy="200" r="%s"/>' % field_r)
    o.append(cl + '<g clip-path="url(#%s)">' % cid)
    o.append('<circle cx="200" cy="200" r="%s" fill="%s"/>' % (field_r, p["field"]))
    o.append('<path fill="%s" d="%s"/>' % (p["water"], geom_d(lake)))
    o.append('<path fill="%s" d="%s"/>' % (p["town"], geom_d(dot)))
    # stars in the field (kept), thickened
    c = container.centroid
    for (dx, dy, rr) in [(-98, -60, 3.0), (-62, -100, 2.4), (62, -100, 2.4), (98, -60, 3.0)]:
        o.append('<g stroke="%s" stroke-width="%s" stroke-linejoin="round">%s</g>' % (
            p["swan"], r1(0.5 / u), star(c.x + dx, c.y + dy, rr * 1.6 + 0.6 / u, p["swan"])))
    # swan: same placement as the full version; gaps under the limit closed, thin parts thickened
    sx, sy, k = flock(lake_g, container, by_off=40)
    far, main = swan_placed(sx, sy, k, SWAN_ROT)
    thick = 0.3 / u
    gclose = 1.0 / u
    main = _closing(main, gclose / 2).buffer(thick, 16)
    far = _closing(far, gclose / 2).buffer(thick, 16)
    # neck and head: at least the minimum width all the way to the bill
    A = SWAN_ANCHORS
    def pt(a):
        q = _rot((A[a][0] * k, A[a][1] * k), SWAN_ROT)
        return (sx + q[0], sy + q[1])
    neck = LineString([pt("chest"), pt("head")]).buffer(w / 2 + thick * 0.5, 16)
    main = unary_union([main, neck.intersection(main.buffer(w, 16))])
    # gulls (kept): same line along the east shore, thickened
    import swans
    A = SWAN_ANCHORS
    hx, hy = _rot((A["head"][0] * k, A["head"][1] * k), SWAN_ROT)
    y0 = sy + hy + 34
    for (dy, gw) in [(0, 25), (34, 21), (66, 17)]:
        y = y0 + dy
        row = lake_g.buffer(2).intersection(LineString([(c.x - 400, y), (c.x + 400, y)]))
        edge = container.buffer(-4).intersection(LineString([(c.x, y), (c.x + 400, y)]))
        if row.is_empty or edge.is_empty:
            continue
        x = (row.bounds[2] + edge.bounds[2]) / 2
        g = swans.gull_side()
        gx0, gy0, gx1, gy1 = g.bounds
        sc = gw / (gx1 - gx0)
        g = affinity.translate(g, -(gx0 + gx1) / 2, -(gy0 + gy1) / 2)
        g = affinity.rotate(affinity.scale(g, sc, sc, origin=(0, 0)), SWAN_ROT, origin=(0, 0))
        g = affinity.translate(g, x, y).buffer(thick * 0.8, 16)
        o.append('<path fill="%s" d="%s"/>' % (p["swan"], geom_d(g.simplify(0.2))))
    for g in (far, main):
        o.append('<path fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round" paint-order="stroke" d="%s"/>'
                 % (p["swan"], p["line"], r1(2 * 1.1 / u), geom_d(g.simplify(0.3))))
    o.append('</g>')
    ring = 1.5 / u
    o.append('<circle cx="200" cy="200" r="%s" fill="none" stroke="%s" stroke-width="%s"/>' % (field_r, p["rim"], r1(ring)))
    tstroke = ' stroke="%s" stroke-width="%s" stroke-linejoin="round"' % (p["text"], r1(0.55 / u))
    o.append(logo.text_arc("AVIAVA", 200, 200, 153, 153, 40, p["text"], track=9, fname=FB).replace("<path ", "<path" + tstroke + " ", 1))
    o.append(logo.text_arc("IŁAWA", 200, 200, 181 - merrow + 7, 181 - merrow + 7, 38, p["text"], track=9, bottom=True, fname=FB).replace("<path ", "<path" + tstroke + " ", 1))
    for sxs in (200 - 165.6, 200 + 165.6):
        o.append('<g stroke="%s" stroke-width="%s" stroke-linejoin="round">%s</g>' % (p["accent"], r1(0.5 / u), star(sxs, 200, 10, p["accent"])))
    return "".join(o), (400, 400)
