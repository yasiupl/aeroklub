import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jeziorak_data as J
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.validation import make_valid
def ring(s): return [tuple(int(v)/10 for v in p.split(',')) for p in s.split()]
def poly(r): return make_valid(Polygon(ring(r)))
def lake():
    shores=[poly(J.JEZIORAK[1]),poly(J.PLASKIE[0]),poly(J.MALY_JEZIORAK[0]),poly(J.ZATOKA[0])]
    water=unary_union(shores).buffer(0.6).buffer(-0.6)
    isl=[J.JEZIORAK[0]]+J.JEZIORAK[2:]+J.PLASKIE[1:]
    for r in isl:
        water=water.difference(poly(r))
    return water
if __name__=='__main__':
    g=lake(); print(g.geom_type,g.bounds,g.area, len(getattr(g,'geoms',[g])))
    for p in getattr(g,'geoms',[g]): print(' part',round(p.area),len(p.interiors))
