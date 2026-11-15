"""Aviava with aviation wings: proposals."""
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from shapely import affinity
import logo, logo2 as L, swans


def band(x0, x1, y, h, lift, tip):
    """One feather band of the right wing: from x0 (under the badge) to x1, rising by `lift` at the tip,
    tip cut back diagonally by `tip`."""
    return Polygon([(x0, y), (x1 - tip * 0.3, y - lift), (x1, y - lift - h * 0.15),
                    (x1 - tip, y + h - lift * 0.85), (x0, y + h)])


def wing_right(cx, cy, r, n=4, span=330, h=24, gap=7, style="bands"):
    parts = []
    for i in range(n):
        y = cy - r * 0.55 + i * (h + gap)
        x1 = cx + r + span - i * span * 0.2
        lift = 34 - i * 7
        if style == "feathers":
            # primaries: separate long feathers fanning from the badge, like the swan's fingers
            pass
        parts.append(band(cx + r * 0.4, x1, y, h, lift, 26 + i * 4))
    return unary_union(parts)


def wing_feathers(cx, cy, r, n=6, span=330):
    """Wing built from swan-like primaries: rounded-tip feathers, longest on top, fanned slightly."""
    parts = []
    for i in range(n):
        y = cy - r * 0.45 + i * 17
        length = span * (1 - 0.13 * i)
        ang = -9 + i * 2.2
        f = swans.feather((cx + r * 0.5, y), ang, length + r * 0.5, 22 - i, pointed=True)
        parts.append(f)
    return unary_union(parts).buffer(0)


def compose(p, style="bands", center="patch", W=1000, H=440, ribbon=False):
    cx, cy, r = W / 2, H / 2 - (20 if ribbon else 0), 150
    rw = wing_right(cx, cy, r) if style == "bands" else wing_feathers(cx, cy, r)
    lw = affinity.scale(rw, -1, 1, origin=(cx, cy))
    wings = unary_union([rw, lw])
    o = ['<path fill="%s" d="%s"/>' % (p["band"], L.geom_d(wings.buffer(5, 16))),
         '<path fill="%s" d="%s"/>' % (p["rim"], L.geom_d(wings))]
    # inner line on every band for depth (darker inset)
    o.append('<path fill="none" stroke="%s" stroke-width="2.5" d="%s"/>' % (p["band"], L.geom_d(wings.buffer(-7, 16))))
    s = r / 197
    body, _ = (L.round_patch(p) if center == "patch" else L.sygnet(p))
    o.append('<g transform="translate(%s,%s) scale(%s)">%s</g>' % (L.r1(cx - 200 * s), L.r1(cy - 200 * s), L.r1(s), body))
    if ribbon:
        y = cy + r + 34
        rib = "M%d,%dH%dL%d,%dL%d,%dH%dL%d,%dZ" % (cx - 200, y - 26, cx + 200, cx + 180, y, cx + 200, y + 26, cx - 200, cx - 180, y)
        o.append('<path fill="%s" d="%s"/>' % (p["band"], rib))
        o.append(logo.text_straight("AEROKLUB IŁAWA", cx, y + 10, 28, p["text"], track=6, fname=L.FB)[0])
    return "".join(o), (W, H + (40 if ribbon else 0))
