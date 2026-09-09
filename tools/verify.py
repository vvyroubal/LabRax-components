#!/usr/bin/env freecadcmd
"""Check the built bracket against the rack, the device, and the printer.

Everything here is measured off the solids the build produces, not off the
parameters, so a feature that silently does nothing is caught rather than
assumed away.

    make verify
"""

import math
import os
import sys

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

ROOT = os.environ.get("UCG_ROOT")
if not ROOT:
    try:
        ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "src"))

import FreeCAD as App  # noqa: E402
import Part  # noqa: E402
from FreeCAD import Vector  # noqa: E402

import params as P  # noqa: E402
import model  # noqa: E402

BED = 180.0  # Bambu Lab A1 mini
VOID = 1.0   # mm^3 -- below this an intersection is boolean noise

_fails = []
_checks = 0


def check(ok, what, detail=""):
    global _checks
    _checks += 1
    if not ok:
        _fails.append("%s%s" % (what, (" -- " + detail) if detail else ""))
    print("  %s  %s%s" % ("ok  " if ok else "FAIL", what,
                          ("   " + detail) if detail else ""))


def box(x0, x1, y0, y1, z0, z1):
    x0, x1 = sorted((x0, x1))
    y0, y1 = sorted((y0, y1))
    z0, z1 = sorted((z0, z1))
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, Vector(x0, y0, z0))


def vol(s):
    return 0.0 if s is None or not s.Solids else s.Volume


def hexnut(cx, cz, af, y0, y1):
    r = af / math.sqrt(3.0)
    pts = [Vector(cx + r * math.cos(math.radians(a)), y0,
                  cz + r * math.sin(math.radians(a)))
           for a in (0, 60, 120, 180, 240, 300)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(
        Vector(0, y1 - y0, 0))


def fits_bed(b):
    """A long thin part can go on the bed diagonally."""
    w, d = b.XLength, b.YLength
    if w <= BED and d <= BED:
        return True, "%.0f x %.0f" % (w, d)
    best = min(max(w * math.cos(t) + d * math.sin(t),
                   w * math.sin(t) + d * math.cos(t))
               for t in (math.radians(x) for x in range(0, 91)))
    return best <= BED, "%.0f x %.0f, %.0f rotated" % (w, d, best)


def main():
    doc = App.newDocument("verify")
    bodies = model.build(doc)
    doc.recompute()
    parts = {n: b.Shape for n, b in bodies.items()}
    names = list(parts)

    asm = parts[names[0]]
    for n in names[1:]:
        asm = asm.fuse(parts[n])
    asm = asm.removeSplitter()

    print("\n[parts]")
    for n, s in parts.items():
        check(s.isValid() and len(s.Solids) == 1,
              "%-10s is one valid solid" % n,
              "%d solids" % len(s.Solids))
        ok, how = fits_bed(s.BoundBox)
        check(ok, "%-10s fits the A1 mini bed" % n, how)
    for n, b in bodies.items():
        sketches = [o for o in b.Group if o.TypeId == "Sketcher::SketchObject"]
        solids = [o for o in b.Group
                  if o.TypeId in ("PartDesign::Pad", "PartDesign::Pocket")]
        check(len(sketches) > 0 and len(solids) > 0,
              "%-10s is sketches driving solids" % n,
              "%d sketches, %d pads/pockets" % (len(sketches), len(solids)))

    print("\n[no part overlaps another]")
    for i, a in enumerate(names):
        for b_ in names[i + 1:]:
            v = vol(parts[a].common(parts[b_]))
            check(v < VOID, "%-10s vs %-10s" % (a, b_), "%.3f mm3" % v)

    print("\n[rack envelope]")
    bb = asm.BoundBox
    check(abs(bb.XMin + P.FACE_HW) < 1e-6 and abs(bb.XMax - P.FACE_HW) < 1e-6,
          "spans the full 10 inch width", "%.2f .. %.2f" % (bb.XMin, bb.XMax))
    check(bb.ZMin >= -1e-6 and bb.ZMax <= P.RACK_U + 1e-6,
          "stays inside 1U", "Z %.2f .. %.2f" % (bb.ZMin, bb.ZMax))
    # Between the posts, only the clear opening is available.
    between = asm.common(box(-300, 300, 0.0, P.RACK_D, -10, 60))
    hw = max(abs(between.BoundBox.XMin), abs(between.BoundBox.XMax))
    check(hw <= P.POST_CLEAR_HW + 1e-6, "body passes between the posts",
          "half-width %.3f, limit %.3f" % (hw, P.POST_CLEAR_HW))

    print("\n[rack screws -- M6 from outside into the post's own nut]")
    for tag, y_out, into in (("front", -P.EAR_T, +1), ("rear", P.RACK_D + P.EAR_T, -1)):
        for sx in (-1, 1):
            for z in P.EIA_Z:
                x = sx * P.SCREW_X
                y0 = y_out
                y1 = y_out + into * (P.EAR_T + 1.0)
                shank = box(x - 3.2, x + 3.2, y0, y1, z - 3.2, z + 3.2)
                v = vol(asm.common(shank))
                check(v < VOID, "%s M6 clear at x=%+8.3f z=%6.3f" % (tag, x, z),
                      "%.3f mm3" % v)
    for sx in (-1, 1):
        head = box(sx * P.SCREW_X - 5.25, sx * P.SCREW_X + 5.25,
                   -P.EAR_T, -P.EAR_T + 1.0, P.EIA_Z[0] - 5.25, P.EIA_Z[0] + 5.25)
        check(vol(asm.common(head)) > VOID,
              "M6 head bears on the front ear at x=%+8.3f" % (sx * P.SCREW_X),
              "%.1f mm3" % vol(asm.common(head)))

    print("\n[top bar -- M6 through the ear into a nut facing rear]")
    for sx in (-1, 1):
        x = sx * P.BAR_SCREW_X
        z = P.BAR_SCREW_Z
        side = parts["side_l" if sx < 0 else "side_r"]
        bar = parts["top_bar_l" if sx < 0 else "top_bar_r"]
        shank = Part.makeCylinder(3.0, P.EAR_T + P.BAR_T - P.M6_HEX_D + 0.1,
                                  Vector(x, -P.EAR_T - 0.05, z), Vector(0, 1, 0))
        check(vol(asm.common(shank)) < VOID,
              "M6 passes the ear and the bar at x=%+7.2f" % x,
              "%.3f mm3" % vol(asm.common(shank)))
        n = hexnut(x, z, 10.0, P.BAR_T - P.M6_HEX_D + 0.05, P.BAR_T - 0.05)
        check(vol(asm.common(n)) < VOID, "M6 nut seats in the bar at x=%+7.2f" % x,
              "%.3f mm3" % vol(asm.common(n)))
        # The nut goes in before the bar is offered up, so only the bar has
        # to be out of the way.
        feed = hexnut(x, z, 10.0, P.BAR_T - P.M6_HEX_D + 0.05, P.BAR_T + 20.0)
        check(vol(bar.common(feed)) < VOID,
              "the nut can be fed in from the rear at x=%+7.2f" % x,
              "%.3f mm3" % vol(bar.common(feed)))
        # The bar must sit in the side's notch, not clash with it.
        check(vol(side.common(bar)) < VOID, "bar clears the side at x=%+7.2f" % x,
              "%.3f mm3" % vol(side.common(bar)))

    print("\n[device]")
    dev = box(-P.DEV_W / 2, P.DEV_W / 2, P.DEV_Y0, P.DEV_Y0 + P.DEV_D,
              P.DEV_Z0, P.DEV_Z1)
    check(vol(asm.common(dev)) < VOID, "device sits without interference",
          "%.3f mm3" % vol(asm.common(dev)))
    cradle = parts["side_l"].fuse(parts["side_r"])
    drop = box(-P.DEV_W / 2, P.DEV_W / 2, P.DEV_Y0, P.DEV_Y0 + P.DEV_D,
               P.DEV_Z0, 400)
    check(vol(cradle.common(drop)) < VOID, "drops in from above between the sides",
          "%.3f mm3" % vol(cradle.common(drop)))
    shelf = box(-P.DEV_W / 2, P.DEV_W / 2, P.DEV_Y0, P.DEV_Y0 + P.DEV_D,
                P.DEV_Z0 - 2.0, P.DEV_Z0)
    check(vol(cradle.common(shelf)) > 1000.0, "the shelf carries it",
          "%.0f mm3 under it" % vol(cradle.common(shelf)))
    fwd = box(-P.DEV_W / 2, P.DEV_W / 2, P.DEV_Y0 - P.BAR_T, P.DEV_Y0,
              P.DEV_Z0, P.DEV_Z1)
    check(vol(asm.common(fwd)) > 100.0, "stopped at the front",
          "%.0f mm3" % vol(asm.common(fwd)))
    back = box(-P.DEV_W / 2, P.DEV_W / 2, P.DEV_Y1, P.DEV_Y1 + P.STOP_T,
               P.DEV_Z0, P.DEV_Z1)
    check(vol(asm.common(back)) > 100.0, "stopped at the rear",
          "%.0f mm3" % vol(asm.common(back)))
    over = box(-P.DEV_W / 2, P.DEV_W / 2, P.DEV_Y0, P.DEV_Y0 + P.DEV_D,
               P.DEV_Z1, P.RACK_U)
    bars = parts["top_bar_l"].fuse(parts["top_bar_r"])
    check(vol(bars.common(over)) > 100.0, "top bar caps it once fitted",
          "%.0f mm3 over it" % vol(bars.common(over)))

    print("\n[clearances]")
    check(abs((P.POST_CLEAR_HW - P.BODY_HW) - 0.925) < 1e-9,
          "0.925 mm per side between rail and post")
    for nm, got, want in (("width", P.POCKET_W - P.DEV_W, P.CLR_W),
                          ("height", P.POCKET_TOP - P.DEV_Z1, P.CLR_H)):
        check(abs(got - want) < 1e-9, "%s clearance %.2f mm" % (nm, got))
    check(2 * P.EAR_X0 < P.DEV_W,
          "the ears overlap the device's ends, so it cannot slide out",
          "opening %.1f vs device %.1f" % (2 * P.EAR_X0, P.DEV_W))

    print("\n%d checks, %d failed" % (_checks, len(_fails)))
    for f in _fails:
        print("  FAIL %s" % f)
    sys.stdout.flush()
    if _fails:
        sys.exit(1)


main()
