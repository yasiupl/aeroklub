"""Embroidery version of the Aviava patch, ready for Ink/Stitch (Inkscape extension).
One layer per thread colour, in sewing order. Fills become tatami fill, dashed strokes become running stitch.
Units: viewBox 0..400 = 100 mm (1 unit = 0.25 mm at D = 100 mm)."""
import math
from shapely.geometry import Point, Polygon, LineString, MultiLineString
from shapely.ops import unary_union
from shapely import affinity
import logo, logo2 as L, lake_build, jeziorak_data as J, swans

NS = 'xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" xmlns:inkstitch="http://inkstitch.org/namespace"'


def star_poly(cx, cy, r):
    k = r * 0.32
    return Polygon([(cx, cy - r), (cx + k, cy - k), (cx + r, cy), (cx + k, cy + k), (cx, cy + r),
                    (cx - k, cy + k), (cx - r, cy), (cx - k, cy - k)])


def _split(g, minw):
    """Fill part (at least minw wide) and the thin remainder (for running stitch)."""
    fill = g.buffer(-minw / 2, 16).buffer(minw / 2, 16).intersection(g)
    thin = g.difference(fill.buffer(0.01))
    return fill, thin


def _gap_lines(full, closed, minlen):
    """Sides of the narrow gaps of `full` that `closed` fills (feather separations), as lines."""
    gaps = closed.difference(full)
    out = []
    for gp in (gaps.geoms if hasattr(gaps, "geoms") else [gaps]):
        if gp.is_empty or gp.geom_type != "Polygon":
            continue
        x0, y0, x1, y1 = gp.bounds
        if max(x1 - x0, y1 - y0) < minlen:
            continue
        side = gp.boundary.intersection(full.boundary.buffer(0.05))
        out.append(side)
    return unary_union(out) if out else LineString()


def geoms(D=100.0, minw=1.0, gap=0.8, dot_mm=3.0, merrow_mm=None, outline_mm=1.0):
    """Same shapes as the main logo. Parts at least minw wide are fills; thinner parts and narrow gaps
    are sewn with running stitch, so the detail of the main logo is kept. Islands: only Wielka Zulawa."""
    u = D / 400.0
    w, gp = minw / u, gap / u
    G = {"u": u}
    field_r = 143
    container = L._circle(200, 200, field_r)
    cx, cy, h = L.lake_fit_vertical(200, 200, field_r, 16)
    lake_full, _ = L.lake_placed(cx, cy, h)
    holes = sorted([Polygon(r) for r in lake_full.interiors], key=lambda hh: -hh.area)
    lake = Polygon(lake_full.exterior)
    mj = L.place_like_lake(lake_build.poly(J.MALY_JEZIORAK[0]), cx, cy, h)
    lake = lake.difference(mj.buffer(0.5 / u))
    lake = max(lake.geoms, key=lambda g: g.area) if lake.geom_type == "MultiPolygon" else lake
    if holes:
        lake = lake.difference(holes[0])          # Wielka Zulawa
    G["lake_fill"], G["lake_thin"] = _split(lake, w)
    G["lake_edge"] = lake.exterior
    G["dot"] = Point(mj.centroid.x, mj.centroid.y).buffer(dot_mm / u / 2, 32)
    # swan, exactly as in the main logo
    lake_fit_g, _ = L.lake_placed(cx, cy, h)
    sx, sy, k = L.flock(lake_fit_g, container, by_off=40)
    far_full, main_full = L.swan_placed(sx, sy, k, L.SWAN_ROT)
    o = outline_mm / u
    main_c = L._closing(main_full, gp / 2)
    far_vis_full = far_full.difference(main_full.buffer(o, 16))
    far_c = L._closing(far_full, gp / 2).difference(main_c.buffer(o, 16))
    # as in the main logo: white shrunk, outline grown around the shape (main logo: 2 units each way at 400)
    inset = 1.0
    main_w = main_c.buffer(-inset, 16)
    far_w = far_c.buffer(-inset, 16)
    G["swan_main"], G["swan_main_thin"] = _split(main_w, w)
    G["swan_far"], G["swan_far_thin"] = _split(far_w, w)
    G["swan_outline"] = unary_union([main_c, far_c]).buffer(o - inset, 16).difference(unary_union([main_w, far_w]))
    lines = unary_union([_gap_lines(main_full, main_c, 1.5 / u),
                         _gap_lines(far_vis_full, far_c, 1.5 / u).difference(main_c.buffer(o))])
    G["swan_detail"] = lines
    # gulls, exactly as in the main logo
    c = container.centroid
    A = L.SWAN_ANCHORS
    q = L._rot((A["head"][0] * k, A["head"][1] * k), L.SWAN_ROT)
    hy = sy + q[1]
    gl = []
    y0 = hy + 34
    for (dy, gw) in [(0, 25), (34, 21), (66, 17)]:
        y = y0 + dy
        row = lake_fit_g.buffer(2).intersection(LineString([(c.x - 400, y), (c.x + 400, y)]))
        edge = container.buffer(-4).intersection(LineString([(c.x, y), (c.x + 400, y)]))
        if row.is_empty or edge.is_empty:
            continue
        x = (row.bounds[2] + edge.bounds[2]) / 2
        g = swans.gull_side()
        gx0, gy0, gx1, gy1 = g.bounds
        sc = gw / (gx1 - gx0)
        g = affinity.translate(g, -(gx0 + gx1) / 2, -(gy0 + gy1) / 2)
        g = affinity.rotate(affinity.scale(g, sc, sc, origin=(0, 0)), L.SWAN_ROT, origin=(0, 0))
        gl.append(affinity.translate(g, x, y))
    gulls = unary_union(gl)
    G["gulls"], G["gulls_thin"] = gulls, Polygon()
    stars = unary_union([star_poly(c.x + dx, c.y + dy, rr * L.STAR_K) for (dx, dy, rr) in
                         [(-98, -60, 3.0), (-62, -100, 2.4), (62, -100, 2.4), (98, -60, 3.0)]])
    G["stars"], G["stars_thin"] = stars, Polygon()
    G["band_stars"] = unary_union([star_poly(x, 200, 10) for x in (200 - 165.6, 200 + 165.6)])
    merrow = L.RIM_W if merrow_mm is None else merrow_mm / u
    G["merrow"] = Point(200, 200).buffer(199, 256).difference(Point(200, 200).buffer(199 - merrow, 256))
    ring = L.RING_W
    G["ring"] = Point(200, 200).buffer(field_r + ring / 2, 256).difference(Point(200, 200).buffer(field_r - ring / 2, 256))
    G["band"] = Point(200, 200).buffer(199 - merrow + 0.3 / u, 256).difference(Point(200, 200).buffer(field_r, 256))
    white_all = unary_union([main_c, far_c, gulls, stars])
    # field fill leaves out only what is filled on top; thin parts are sewn as running stitch over the field
    filled = unary_union([G["lake_fill"], G["lake_thin"], G["swan_outline"], G["swan_main"], G["swan_far"],
                          G["swan_main_thin"], G["swan_far_thin"], G["gulls"], G["stars"], G["dot"]])
    G["field"] = container.difference(filled)
    for key in ("lake_fill", "lake_thin"):
        G[key] = G[key].difference(unary_union([main_c.buffer(o - inset), far_c.buffer(o - inset), gulls, stars, G["dot"]]))
    G["text_top"] = logo.text_arc("AVIAVA", 200, 200, 153, 153, 40, "#000", track=9, fname=L.FB)
    G["text_bot"] = logo.text_arc("IŁAWA", 200, 200, 181, 181, 40, "#000", track=9, bottom=True, fname=L.FB)
    return G


def _d(g):
    return L.geom_d(g) if not g.is_empty else ""


def _lines_d(g):
    if g.is_empty:
        return ""
    ls = [g] if g.geom_type == "LineString" else [x for x in getattr(g, "geoms", []) if x.geom_type == "LineString"]
    return "".join("M" + "L".join("%s,%s" % (L.r1(x), L.r1(y)) for x, y in l.coords) for l in ls if l.length > 2)


def _thin_d(g):
    """Thin parts as running-stitch lines: their outlines."""
    if g.is_empty:
        return ""
    polys = [x for x in getattr(g, "geoms", [g]) if x.geom_type == "Polygon" and x.area > 0.05]
    return _lines_d(unary_union([p.exterior for p in polys])) if polys else ""


def svg(p, D=100.0, inkstitch=True, details=True):
    G = geoms(D)
    u = G["u"]
    fill_attr = lambda ang: (' inkstitch:angle="%d" inkstitch:row_spacing_mm="0.25" inkstitch:max_stitch_length_mm="3.5"'
                             ' inkstitch:fill_underlay="true"' % ang) if inkstitch else ""
    run_attr = (' stroke-dasharray="1,0.5" inkstitch:stroke_method="running_stitch" inkstitch:running_stitch_length_mm="1.2"'
                ' inkstitch:bean_stitch_repeats="1"') if inkstitch else ""
    layers = []

    def layer(label, body):
        layers.append('<g inkscape:groupmode="layer" inkscape:label="%s">%s</g>' % (label, body))

    def fill(g, col, ang=45):
        return '<path fill="%s" fill-rule="evenodd"%s d="%s"/>' % (col, fill_attr(ang), _d(g)) if not g.is_empty else ""

    def run(dd, col):
        return ('<path fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round" stroke-linejoin="round"%s d="%s"/>'
                % (col, L.r1(0.35 / u), run_attr, dd)) if dd and details else ""

    layer("01 pole (%s)" % p["field"], fill(G["field"], p["field"], 45))
    layer("02 otok i obrys łabędzia (%s)" % p["band"], fill(G["band"], p["band"], 135) +
          fill(G["swan_outline"], p["line"], 90))
    thin_attr = ' inkscape:label="cienkie – satyna albo ścieg prosty"'
    def thinfill(g, col, ang):
        return fill(g, col, ang).replace("<path ", "<path" + thin_attr + " ", 1) if not g.is_empty else ""
    layer("03 woda (%s)" % p["water"], fill(G["lake_fill"], p["water"], 90) + thinfill(G["lake_thin"], p["water"], 90) +
          run(_lines_d(G["lake_edge"]), p["water"]))
    layer("04 łabędź, mewy, gwiazdy (%s)" % p["swan"],
          fill(G["swan_far"], p["swan"], 60) + fill(G["swan_main"], p["swan"], 120) + fill(G["gulls"], p["swan"], 30) +
          fill(G["stars"], p["swan"], 0) +
          thinfill(unary_union([G["swan_main_thin"], G["swan_far_thin"]]), p["swan"], 120))
    layer("05 pióra – ścieg prosty (%s)" % p["line"], run(_lines_d(G["swan_detail"]), p["line"]))
    layer("06 Iława (%s)" % p["town"], fill(G["dot"], p["town"], 0))
    layer("07 pierścień (%s)" % p["rim"], fill(G["ring"], p["rim"], 0))
    text = G["text_top"] + G["text_bot"]
    if inkstitch:
        text = text.replace('fill="#000"', 'fill="%s" inkstitch:angle="90" inkstitch:row_spacing_mm="0.22" inkstitch:expand_mm="0.2" inkstitch:fill_underlay="true"' % p["text"])
    else:
        text = text.replace('fill="#000"', 'fill="%s"' % p["text"])
    layer("08 napisy (%s)" % p["text"], text + fill(G["band_stars"], p["accent"], 0))
    layer("09 obrzeże – merrow (%s)" % p["rim"], fill(G["merrow"], p["rim"], 0))
    return ('<svg %s width="%gmm" height="%gmm" viewBox="0 0 400 400">'
            '<title>Aviava – wersja do haftu, średnica %g mm</title>%s</svg>' % (NS, D, D, D, "".join(layers)))
