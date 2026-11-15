"""Swan silhouette variants for the Aviava mark. All heading right, centre near (0, 0)."""
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union
from shapely import affinity


def cubic(p0, p1, p2, p3, n=24):
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        out.append((u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
                    u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]))
    return out


def path(*segs):
    """segs: lists of points; joined in order into one ring."""
    pts = []
    for s in segs:
        pts.extend(s if not pts else s[1:])
    return Polygon(pts).buffer(0)


def taper(pts, w0, w1):
    parts = []
    n = len(pts) - 1
    for i in range(n):
        a = w0 + (w1 - w0) * i / n
        b = w0 + (w1 - w0) * (i + 1) / n
        parts.append(unary_union([Point(pts[i]).buffer(a / 2, 32), Point(pts[i + 1]).buffer(b / 2, 32)]).convex_hull)
    return unary_union(parts)


def head_neck(x0=24, y0=-3, x1=96, y1=-9, w0=12, w1=6.4, head=(7.4, 5.0), bill=15):
    neck = taper(cubic((x0, y0), (x0 + 25, y0 - 4), (x1 - 25, y1 - 1), (x1, y1), 12), w0, w1)
    hx, hy = x1 + 4, y1 + 0.3
    hd = affinity.rotate(affinity.scale(Point(hx, hy).buffer(1, 48), head[0], head[1]), 6, origin=(hx, hy))
    knob = Point(hx + 5.6, hy - 2.6).buffer(2.3, 32)
    bl = Polygon([(hx + 4, hy - 3.4), (hx + 4 + bill, hy + 1.6), (hx + 3.6 + bill, hy + 3.4), (hx + 4, hy + 3.2)])
    return unary_union([neck, hd, knob, bl])


def body(rx=33, ry=12, tilt=-3):
    b = affinity.rotate(affinity.scale(Point(0, 0).buffer(1, 64), rx, ry), tilt, origin=(0, 0))
    tail = Polygon([(-26, -5), (-44, -5), (-41, 0), (-44, 5), (-26, 7)])
    feet = taper([(-30, 5), (-48, 7)], 4.5, 3)
    return unary_union([b, tail, feet])


def soften(g, r=1.2):
    return g.buffer(r, 32).buffer(-r, 32)


# A. upstroke, side view, smooth pointed wing (no fingered primaries: swans have none)
def swan_a():
    wing = path(cubic((16, -6), (18, -44), (-18, -82), (-84, -100)),
                cubic((-84, -100), (-70, -84), (-56, -60), (-50, -34)),
                cubic((-50, -34), (-46, -20), (-36, -8), (-22, -4)),
                [(-22, -4), (16, -6)])
    far = path(cubic((22, -8), (34, -40), (20, -72), (-22, -98)),
               cubic((-22, -98), (-6, -76), (4, -46), (4, -8)), [(4, -8), (22, -8)])
    return soften(unary_union([body(), head_neck(), wing, far]))


# B. glide, three-quarter view from above: near wing down-back, far wing up-back (dart, like a glider)
def swan_b():
    near = path(cubic((14, 2), (4, 26), (-30, 50), (-82, 62)),
                cubic((-82, 62), (-60, 48), (-44, 30), (-34, 10)), [(-34, 10), (14, 2)])
    far = path(cubic((12, -8), (4, -30), (-26, -50), (-74, -60)),
               cubic((-74, -60), (-52, -44), (-40, -28), (-30, -8)), [(-30, -8), (12, -8)])
    return soften(unary_union([body(rx=32, ry=10.5, tilt=0), head_neck(y0=-2, y1=-6), near, far]))


# C. view from below, wings spread with the gull bend of glider badges
def swan_c():
    def wing(sign):
        s = sign
        return path(cubic((14, 6 * s), (20, 34 * s), (16, 56 * s), (8, 66 * s)),
                    cubic((8, 66 * s), (2, 82 * s), (-18, 98 * s), (-40, 108 * s)),
                    cubic((-40, 108 * s), (-28, 88 * s), (-26, 76 * s), (-30, 64 * s)),
                    cubic((-30, 64 * s), (-24, 50 * s), (-18, 28 * s), (-14, 6 * s)), [(-14, 6 * s), (14, 6 * s)])
    b = affinity.scale(Point(0, 0).buffer(1, 64), 30, 9.5)
    tail = Polygon([(-24, -6), (-42, -8), (-46, 0), (-42, 8), (-24, 6)])
    hn = head_neck(x0=24, y0=0, x1=94, y1=0, w0=14, w1=7.5, head=(7.6, 5), bill=14)
    hn = affinity.scale(hn, 1, 0.85, origin=(0, 0))
    return soften(unary_union([b, tail, hn, wing(1), wing(-1)]))


# D. flat planes (method of Gronowski's crane, own drawing): wing, body, neck split by gaps
def swan_d():
    wing = path(cubic((16, -8), (10, -48), (-24, -84), (-86, -94)),
                [(-86, -94), (-30, -8)], [(-30, -8), (16, -8)])
    bd = path(cubic((-44, -2), (-30, -10), (10, -12), (30, -6)),
              cubic((30, -6), (20, 12), (-20, 14), (-44, -2)))
    hn = head_neck(x0=30, y0=-6, x1=98, y1=-12, w0=9, w1=5.6, head=(6.8, 4.8), bill=14)
    g = unary_union([wing, bd, hn])
    gap1 = LineString([(-40, -6), (24, -10)]).buffer(1.6)
    gap2 = LineString([(-60, -60), (-24, -16)]).buffer(1.2)
    return g.difference(unary_union([gap1, gap2]))


VARIANTS = [("A", "Wznoszenie", swan_a), ("B", "Szybowanie", swan_b),
            ("C", "Mewa", swan_c), ("D", "Płaszczyzny", swan_d)]


# E. view from above, neutral mute swan in flight: straight neck, broad wings, short wedge tail
def swan_e():
    def wing(s):
        return path(cubic((16, 10 * s), (19, 34 * s), (18, 60 * s), (14, 80 * s)),
                    cubic((14, 80 * s), (10, 96 * s), (2, 110 * s), (-8, 120 * s)),
                    cubic((-8, 120 * s), (-14, 124 * s), (-20, 120 * s), (-20, 112 * s)),
                    cubic((-20, 112 * s), (-24, 96 * s), (-28, 82 * s), (-28, 64 * s)),
                    cubic((-28, 64 * s), (-28, 44 * s), (-22, 24 * s), (-16, 10 * s)),
                    [(-16, 10 * s), (16, 10 * s)])
    b = affinity.scale(Point(0, 0).buffer(1, 64), 31, 13)
    tail = path(cubic((-24, -9), (-36, -9), (-44, -5), (-50, 0)), cubic((-50, 0), (-44, 5), (-36, 9), (-24, 9)))
    neck = taper(cubic((24, 0), (44, 0), (66, 0), (84, 0), 12), 12, 7.6)
    head = affinity.scale(Point(89, 0).buffer(1, 48), 7.4, 5.4)
    bill = path(cubic((93, -3.6), (100, -3.4), (106, -2.4), (108, 0)), cubic((108, 0), (106, 2.4), (100, 3.4), (93, 3.6)))
    return soften(unary_union([b, tail, neck, head, bill, wing(1), wing(-1)]), 1.0)


VARIANTS.append(("E", "Z góry", swan_e))


def scallop(pts, amp=1.6, every=9):
    """Add small feather notches along a polyline (alternating offsets)."""
    out = [pts[0]]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
        n = max(1, int(L / every))
        nx, ny = (y1 - y0) / L, -(x1 - x0) / L
        for i in range(1, n + 1):
            t = i / n
            k = amp if i % 2 else 0
            out.append((x0 + (x1 - x0) * t + nx * k, y0 + (y1 - y0) * t + ny * k))
    return out


# F. view from above, after photos of mute swans (Wikimedia Commons): plump body, thick neck,
#    long wings swept back at the wrist, pointed hand with separated primaries, notched trailing edge
def swan_f():
    def wing(s):
        lead = cubic((18, 12), (24, 30), (27, 50), (25, 66)) + cubic((25, 66), (22, 90), (8, 114), (-12, 132))[1:]
        tip = [(-12, 132), (-14, 123), (-22, 128), (-22, 118), (-31, 121), (-29, 110), (-38, 108)]
        trail = scallop([(-38, 108), (-38, 90), (-36, 70), (-33, 50), (-29, 30), (-24, 12)], amp=1.1, every=9)
        pts = lead + tip[1:] + trail[1:] + [(18, 12)]
        return Polygon([(x, y * s) for x, y in pts]).buffer(0)
    b = affinity.scale(Point(0, 0).buffer(1, 64), 33, 16.5)
    tail = path(cubic((-24, -12), (-38, -11), (-46, -6), (-52, 0)), cubic((-52, 0), (-46, 6), (-38, 11), (-24, 12)))
    neck = taper(cubic((22, 0), (40, 0), (58, 0), (78, 0), 12), 21, 11)
    head = affinity.scale(Point(84, 0).buffer(1, 48), 9.5, 6.8)
    bill = path([(88, -4.8), (104, -2), (105.5, 0), (104, 2), (88, 4.8)])
    return soften(unary_union([b, tail, neck, head, bill, wing(1), wing(-1)]), 1.2)


VARIANTS.append(("F", "Z góry (wg zdjęć)", swan_f))


# ---------------------------------------------------------------- feathered wing
import math


def feather(base, ang, length, w, pointed=True):
    """One feather from base along angle (deg; x=cos, y=sin). Rounded or pointed tip."""
    bx, by = base
    dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    nx, ny = -dy, dx
    tx, ty = bx + dx * length, by + dy * length
    if pointed:
        pts = [(bx + nx * w / 2, by + ny * w / 2),
               (bx + dx * length * 0.7 + nx * w * 0.42, by + dy * length * 0.7 + ny * w * 0.42),
               (tx, ty),
               (bx + dx * length * 0.7 - nx * w * 0.42, by + dy * length * 0.7 - ny * w * 0.42),
               (bx - nx * w / 2, by - ny * w / 2)]
        return Polygon(pts).buffer(0.5)
    return taper([(bx, by), (tx - dx * w * 0.4, ty - dy * w * 0.4)], w, w * 0.9)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def wing_planform(bend=1.0, finger=1.0):
    """Right wing, planform. x forward, y outward. A short hand bone carries a fan of long primaries;
    the leading edge breaks at the wrist; outer primaries separate at the tips."""
    S, W = (16, 12), (21, 58)
    H = (21 - 12 * bend, 78)
    parts = []
    # secondaries: rounded tips, along the arm, pointing back
    sec_bases = [lerp((S[0] - 14, S[1] + 1), (W[0] - 12, W[1] - 2), (i + 0.5) / 11) for i in range(11)]
    for i, bse in enumerate(sec_bases):
        t = i / 10
        parts.append(feather(bse, 178 - 8 * t, 31 - 2 * t, 9.5, pointed=False))
    # primaries: fan from the wrist (inner, pointing back) to the hand tip (outer, pointing out)
    n = 10
    for i in range(n):
        t = i / (n - 1)
        bse = lerp((W[0] - 9, W[1] - 1), (H[0] - 2, H[1] - 2), t)
        ang = [166, 160, 154, 148, 142, 135, 124, 115, 106, 98][i]
        length = [38, 40, 42, 44, 47, 50, 54, 56, 55, 50][i]
        width = [13, 13, 13, 13, 13, 12.5, 10, 9, 8.5, 8][i] if finger else 12
        parts.append(feather(bse, ang, length, width, pointed=True))
    # coverts and the leading edge (break at the wrist)
    lead = cubic(S, (22, 26), (24, 44), W) + cubic(W, (19, 66), (16, 72), H)[1:]
    back = [(H[0] - 8, H[1] - 6), (W[0] - 14, W[1] - 4), (S[0] - 18, S[1] + 2), (S[0] - 18, S[1])]
    parts.append(Polygon(lead + back).buffer(0))
    return unary_union(parts)


def swan_g():
    """View from below/above: plump body, broad straight wings with fingered tips,
    short feathered tail, webbed feet splayed behind (after photos, not traced)."""
    def wing(sg):
        g = wing_planform(bend=0.55)
        g = affinity.scale(g, 1.0, 1.12, origin=(0, 0))
        return g if sg > 0 else affinity.scale(g, 1, -1, origin=(0, 0))
    b = affinity.scale(Point(0, 0).buffer(1, 64), 34, 17)
    tail = tail_fan((-28, 0), n=7, spread=46, length=(16, 20), w=6, ang0=180)
    neck = taper(cubic((22, 0), (36, 0), (52, 0), (66, 0), 12), 22, 11)
    head = affinity.scale(Point(72, 0).buffer(1, 48), 9.6, 6.8)
    bill = path([(76, -4.8), (92, -2.2), (93.5, 0), (92, 2.2), (76, 4.8)])
    feet = unary_union([foot((-26, 10), 158, 26, spread=40), foot((-26, -10), 202, 26, spread=40)])
    return unary_union([soften(unary_union([b, tail, neck, head, bill]), 1.2), feet, wing(1), wing(-1)])


def swan_h():
    """Side view, upstroke (variant A) with feathered wing: planform sheared up and back."""
    w = wing_planform(bend=1.0)
    # outward axis y -> up (-y) and back (-x); foreshorten
    w = affinity.affine_transform(w, [1, -0.38, 0, -0.86, 0, 0])
    w = affinity.translate(w, -4, 2)
    base = unary_union([body(), head_neck()])
    return unary_union([soften(base), w])


VARIANTS.append(("G", "Z góry, pióra", swan_g))
VARIANTS.append(("H", "Wznoszenie, pióra", swan_h))


def gull_side():
    """Small gull, three-quarter side view, wings in the gull bend, heading right."""
    b = affinity.rotate(affinity.scale(Point(0, 0).buffer(1, 48), 12, 4), -6, origin=(0, 0))
    head = Point(12, -2.4).buffer(3.3, 32)
    bill = Polygon([(14, -3.6), (19.5, -2.2), (14, -1.0)])
    tail = Polygon([(-10, -2), (-19, -2.6), (-19, 1.6), (-10, 2.4)])
    near = path(cubic((4, -2), (2, -9), (-1, -14), (-6, -17)),
                cubic((-6, -17), (-12, -15), (-19, -12), (-27, -9)),
                cubic((-27, -9), (-19, -8), (-13, -7), (-9, -4)),
                [(-9, -4), (-4, 0), (4, -2)])
    far = path(cubic((7, -3), (8, -9), (8, -13), (5, -17)),
               cubic((5, -17), (2, -20), (-2, -22), (-6, -24)),
               cubic((-6, -24), (-2, -19), (0, -15), (1, -10)),
               [(1, -10), (2, -3), (7, -3)])
    return soften(unary_union([b, head, bill, tail, near, far]), 0.6)


# ---------------------------------------------------------------- side view with tail fan and feet
def tail_fan(base=(-30, -3), n=7, spread=26, length=(18, 24), w=5.5, ang0=182):
    parts = []
    for i in range(n):
        t = i / (n - 1)
        a = ang0 - spread / 2 + spread * t
        L = length[0] + (length[1] - length[0]) * (1 - abs(t - 0.5) * 2)
        parts.append(feather(base, a, L, w, pointed=True))
    return unary_union(parts)


def foot(heel, ang, length=16, toes=3, spread=26):
    """Webbed foot trailing back: shank + web with pointed toes."""
    hx, hy = heel
    parts = [taper([(hx, hy), (hx + length * 0.45 * math.cos(math.radians(ang)),
                               hy + length * 0.45 * math.sin(math.radians(ang)))], 3.2, 2.6)]
    base = (hx + length * 0.4 * math.cos(math.radians(ang)), hy + length * 0.4 * math.sin(math.radians(ang)))
    tips = []
    for i in range(toes):
        a = math.radians(ang - spread / 2 + spread * i / (toes - 1))
        tips.append((base[0] + length * 0.62 * math.cos(a), base[1] + length * 0.62 * math.sin(a)))
    parts.append(Polygon([base] + tips).buffer(0.6))
    return unary_union(parts)


def body_side():
    """Body: round chest, flat belly, rear rising into the tail."""
    top = cubic((26, -4), (20, -15), (-6, -15), (-30, -8))
    rear = cubic((-30, -8), (-36, -6), (-38, -2), (-34, 2))
    belly = cubic((-34, 2), (-20, 12), (6, 13), (22, 8))
    chest = cubic((22, 8), (30, 5), (31, -1), (26, -4))
    b = Polygon(top + rear[1:] + belly[1:] + chest[1:]).buffer(0)
    return unary_union([b, tail_fan((-32, -1), n=7, spread=34, length=(26, 34), w=5.6, ang0=182)])


def feet_side():
    return unary_union([foot((-20, 7), 174, 30, spread=24), foot((-17, 9), 168, 28, spread=24)])


def neck_head_side(angle=-6):
    """Long straight neck, slightly raised; head with a down-sloping bill and knob."""
    L = 78
    a = math.radians(angle)
    x1, y1 = 24 + L * math.cos(a), -2 + L * math.sin(a)
    neck = taper(cubic((22, -1), (40, -3), (60, y1 + 2), (x1, y1), 12), 13, 6.2)
    hd = affinity.rotate(affinity.scale(Point(x1 + 4, y1).buffer(1, 48), 7.6, 5.0), 10, origin=(x1 + 4, y1))
    knob = Point(x1 + 9, y1 - 2.4).buffer(2.2, 32)
    bill = Polygon([(x1 + 8.5, y1 - 3.8), (x1 + 22, y1 + 2.6), (x1 + 21, y1 + 4.2), (x1 + 8.5, y1 + 3.4)])
    return unary_union([neck, hd, knob, bill])


def swan_i_parts():
    """Side view, upstroke. Returns (far_wing, main) so the far wing can sit behind with an outline."""
    near = wing_planform(bend=1.0)
    near = affinity.translate(affinity.affine_transform(near, [1, -0.38, 0, -0.86, 0, 0]), -6, 0)
    far = wing_planform(bend=1.0)
    far = affinity.affine_transform(far, [0.55, 0.06, 0, -0.52, 0, 0])
    far = affinity.translate(far, 18, -9)
    from shapely.geometry import box
    fx0, fy0, fx1, fy1 = far.bounds
    root = far.intersection(box(fx0, fy1 - 10, fx1, fy1))
    far = unary_union([far, unary_union([root, Point(8, 2).buffer(6)]).convex_hull])
    main = unary_union([soften(unary_union([body_side(), neck_head_side()]), 0.8), near])
    return far, main


def swan_i():
    f, m = swan_i_parts()
    return unary_union([f, m])


VARIANTS.append(("I", "Wznoszenie, ogon i nogi", swan_i))
