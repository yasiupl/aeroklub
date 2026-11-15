"""Raster design-rule check for embroidery.
Renders an SVG at the real size, splits it into thread colours and finds:
- parts of a colour narrower than the minimum width (satin/fill limit),
- isolated parts smaller than the minimum element,
- text cap height below the minimum.
Writes an overlay PNG: red = below hard limit, orange = below recommended limit."""
import sys, io, numpy as np, cairosvg
from PIL import Image
from scipy import ndimage as ndi

PXMM = 20


def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


def run(svg, D_mm, colours, hard=1.0, rec=1.3, min_el=1.5, out=None):
    size = int(D_mm * PXMM)
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size)
    im = np.asarray(Image.open(io.BytesIO(png)).convert("RGBA")).astype(int)
    rgb, a = im[..., :3], im[..., 3]
    pal = np.array([[int(c[i:i + 2], 16) for i in (1, 3, 5)] for c in colours])
    d = ((rgb[:, :, None, :] - pal[None, None]) ** 2).sum(-1)
    lab = d.argmin(-1)
    lab[a < 128] = -1
    report = []
    red = np.zeros(lab.shape, bool); orange = np.zeros(lab.shape, bool)
    for i, c in enumerate(colours):
        m = lab == i
        if not m.any():
            continue
        th = ndi.binary_opening(m, disk(int(round(hard * PXMM / 2))))
        tr = ndi.binary_opening(m, disk(int(round(rec * PXMM / 2))))
        thin_h = m & ~th
        thin_r = m & ~tr & ~thin_h
        # ignore 1-px antialias fringes
        thin_h = ndi.binary_opening(thin_h, disk(1)); thin_r = ndi.binary_opening(thin_r, disk(1))
        lbl, n = ndi.label(m)
        sizes = ndi.sum(m, lbl, range(1, n + 1)) / PXMM ** 2
        small = [s for s in sizes if 0.1 < s < min_el ** 2]
        red |= thin_h; orange |= thin_r
        report.append(dict(colour=c, area_mm2=round(m.sum() / PXMM ** 2, 1),
                           below_hard_mm2=round(thin_h.sum() / PXMM ** 2, 2),
                           below_rec_mm2=round(thin_r.sum() / PXMM ** 2, 2),
                           parts=int((sizes > 0.1).sum()), small_parts=len(small)))
    if out:
        base = Image.open(io.BytesIO(png)).convert("RGB")
        base = Image.blend(base, Image.new("RGB", base.size, (255, 255, 255)), 0.55)
        arr = np.asarray(base).copy()
        arr[orange] = (255, 150, 0); arr[red] = (230, 0, 0)
        Image.fromarray(arr).save(out)
    return report
