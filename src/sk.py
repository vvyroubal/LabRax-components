"""Thin helpers for building PartDesign bodies from scripted sketches.

Everything in this project is modelled the way it would be by hand: a Body per
part, a Sketch for each feature, and a Pad or Pocket driven by it. These are
the bits of boilerplate that would otherwise drown the model.

A sketch is placed by naming its two in-plane axes. `plane(origin, u, v)` maps
the sketch's local X to `u` and local Y to `v`, so a pad grows along u x v.
"""

import FreeCAD as App
import Part
import Sketcher
from FreeCAD import Vector

X = Vector(1, 0, 0)
Y = Vector(0, 1, 0)
Z = Vector(0, 0, 1)


def plane(origin, u, v):
    """Placement whose local X is `u`, local Y is `v`; pads grow along u x v."""
    w = u.cross(v)
    return App.Placement(App.Matrix(u.x, v.x, w.x, origin.x,
                                    u.y, v.y, w.y, origin.y,
                                    u.z, v.z, w.z, origin.z,
                                    0.0, 0.0, 0.0, 1.0))


def body(doc, name):
    return doc.addObject("PartDesign::Body", name)


def sketch(doc, bd, name, placement):
    sk = doc.addObject("Sketcher::SketchObject", name)
    bd.addObject(sk)
    sk.Placement = placement
    return sk


def polygon(sk, pts):
    """Add a closed polyline and constrain it shut."""
    n = len(sk.Geometry)
    k = len(pts)
    for i in range(k):
        a, b = pts[i], pts[(i + 1) % k]
        sk.addGeometry(Part.LineSegment(Vector(a[0], a[1], 0),
                                        Vector(b[0], b[1], 0)), False)
    for i in range(k):
        sk.addConstraint(Sketcher.Constraint("Coincident",
                                             n + i, 2, n + (i + 1) % k, 1))
    return sk


def rect(sk, u0, v0, u1, v1):
    return polygon(sk, [(u0, v0), (u1, v0), (u1, v1), (u0, v1)])


def circle(sk, cu, cv, d):
    sk.addGeometry(Part.Circle(Vector(cu, cv, 0), Vector(0, 0, 1), d / 2.0),
                   False)
    return sk


def hexagon(sk, cu, cv, af):
    """Hexagon `af` across the flats, flats top and bottom."""
    import math
    r = af / math.sqrt(3.0)
    pts = [(cu + r * math.cos(math.radians(a)), cv + r * math.sin(math.radians(a)))
           for a in (0, 60, 120, 180, 240, 300)]
    return polygon(sk, pts)


def slot(sk, cu, cv, w, h):
    """Slot with semicircular ends, `w` long and `h` across.

    Built as one counter-clockwise loop -- bottom line, right arc, top line,
    left arc -- so that each segment's end really is the next one's start. Get
    that ordering wrong and the coincidence constraints pull the geometry into
    a different shape on each side of the model.
    """
    import math
    r = h / 2.0
    a, b = cu - (w - h) / 2.0, cu + (w - h) / 2.0
    n = len(sk.Geometry)
    sk.addGeometry(Part.LineSegment(Vector(a, cv - r, 0),
                                    Vector(b, cv - r, 0)), False)
    sk.addGeometry(Part.ArcOfCircle(
        Part.Circle(Vector(b, cv, 0), Vector(0, 0, 1), r),
        -math.pi / 2, math.pi / 2), False)
    sk.addGeometry(Part.LineSegment(Vector(b, cv + r, 0),
                                    Vector(a, cv + r, 0)), False)
    sk.addGeometry(Part.ArcOfCircle(
        Part.Circle(Vector(a, cv, 0), Vector(0, 0, 1), r),
        math.pi / 2, 3 * math.pi / 2), False)
    for i in range(4):
        sk.addConstraint(Sketcher.Constraint("Coincident",
                                             n + i, 2, n + (i + 1) % 4, 1))
    return sk


def pad(doc, bd, sk, length, reversed_=False, name=None):
    p = doc.addObject("PartDesign::Pad", name or ("Pad_" + sk.Name))
    bd.addObject(p)
    p.Profile = sk
    p.Length = length
    p.Reversed = reversed_
    doc.recompute()
    return p


def pocket(doc, bd, sk, length, reversed_=None, name=None):
    """Cut `length` into the body. Direction is worked out by trying it.

    Which way a Pocket travels depends on the sketch's normal, and getting it
    wrong is silent -- the feature just removes nothing. Rather than reason
    about the sign at every call site, cut and check the volume actually fell.
    """
    before = bd.Shape.Volume if bd.Shape.Solids else 0.0
    p = doc.addObject("PartDesign::Pocket", name or ("Pocket_" + sk.Name))
    bd.addObject(p)
    p.Profile = sk
    p.Length = length
    p.Reversed = bool(reversed_) if reversed_ is not None else False
    ok = _recompute(doc, bd, before)
    if not ok and reversed_ is None:
        p.Reversed = True
        ok = _recompute(doc, bd, before)
    if not ok:
        raise RuntimeError("pocket %s removed nothing" % p.Name)
    return p


def _recompute(doc, bd, before):
    try:
        doc.recompute()
    except Exception:
        return False
    if not bd.Shape.Solids:
        return False
    return (before - bd.Shape.Volume) > 1e-6
