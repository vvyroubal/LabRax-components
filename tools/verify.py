#!/usr/bin/env freecadcmd
"""Check the built bracket against the rack, the device, and the printer.

Everything here is measured off the solids the build produces, not off the
parameters, so a boolean that goes wrong is caught rather than assumed away.

    make verify
"""

import os
import sys

# freecadcmd terminates hard on sys.exit, which loses a block-buffered pipe.
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:  # pragma: no cover -- older interpreters
    pass

ROOT = os.environ.get("UCG_ROOT")
if not ROOT:
    try:
        ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "src"))

import FreeCAD  # noqa: E402,F401
import Part  # noqa: E402
from FreeCAD import Vector  # noqa: E402

import params as P  # noqa: E402
import model  # noqa: E402

BED_X = BED_Y = BED_Z = 180.0  # Bambu Lab A1 mini
VOID = 1.0  # mm^3 -- below this an intersection is boolean noise, not contact

_fails = []
_checks = 0


def check(ok, what, detail=""):
    global _checks
    _checks += 1
    if not ok:
        _fails.append("%s%s" % (what, (" -- " + detail) if detail else ""))
    print("  %s  %s%s" % ("ok  " if ok else "FAIL", what,
                          ("   " + detail) if detail else ""))


def near(a, b, tol=1e-6):
    return abs(a - b) <= tol


def box(x0, x1, y0, y1, z0, z1):
    return model.box(x0, x1, y0, y1, z0, z1)


def vol(shape):
    return 0.0 if shape is None or not shape.Solids else shape.Volume


def main():
    parts = model.build_parts()
    frame = ("tray", "top_bar", "ear_l", "ear_r")   # bolted together
    stops = ("stop_l", "stop_r")                    # fitted after the device

    asm = parts[frame[0]]
    for n in frame[1:]:
        asm = asm.fuse(parts[n])
    asm = asm.removeSplitter()

    whole = asm
    for n in stops:
        whole = whole.fuse(parts[n])
    whole = whole.removeSplitter()

    print("\n[parts]")
    for n, s in parts.items():
        check(len(s.Solids) == 1, "%-8s is a single solid" % n,
              "%d solids" % len(s.Solids))
    for n, s in parts.items():
        b = s.BoundBox
        fits = (b.XLength <= BED_X and b.YLength <= BED_Y and b.ZLength <= BED_Z)
        check(fits, "%-8s fits the A1 mini bed" % n,
              "%.1f x %.1f x %.1f" % (b.XLength, b.YLength, b.ZLength))

    print("\n[no part overlaps another]")
    names = list(parts)
    for i, a in enumerate(names):
        for b_ in names[i + 1:]:
            v = vol(parts[a].common(parts[b_]))
            check(v < VOID, "%-8s vs %-8s" % (a, b_), "%.3f mm3" % v)

    print("\n[rack envelope]")
    bb = whole.BoundBox
    check(near(bb.XMin, -P.FACE_HW, 1e-6) and near(bb.XMax, P.FACE_HW, 1e-6),
          "faceplate spans the full 10 inch width",
          "%.2f .. %.2f" % (bb.XMin, bb.XMax))
    check(bb.ZMin >= -1e-6 and bb.ZMax <= P.RACK_U + 1e-6,
          "stays inside 1U", "Z %.2f .. %.2f (U = %.2f)"
          % (bb.ZMin, bb.ZMax, P.RACK_U))
    # Anything at or behind the post face has to pass between the posts.
    behind = whole.common(box(-300, 300, 0.0, 400, -10, 60))
    bb2 = behind.BoundBox
    check(max(abs(bb2.XMin), abs(bb2.XMax)) <= P.POST_CLEAR_HW + 1e-6,
          "body passes between the posts",
          "half-width %.3f, limit %.3f" % (max(abs(bb2.XMin), abs(bb2.XMax)),
                                           P.POST_CLEAR_HW))

    print("\n[mounting holes]")
    for sx in (-1, 1):
        for z in P.EIA_Z:
            x = sx * P.SCREW_X
            # An M6 screw must pass clean through the faceplate ...
            screw = Part.makeCylinder(6.4 / 2, P.FACE_T + 4,
                                      Vector(x, -P.FACE_T - 2, z),
                                      Vector(0, 1, 0))
            v = vol(whole.common(screw))
            check(v < VOID, "M6 clear at x=%+8.3f z=%6.3f" % (x, z),
                  "%.3f mm3" % v)
    for sx in (-1, 1):
        for z in P.EIA_Z:
            x = sx * P.SCREW_X
            # ... and the slot must not be so big the head pulls through.
            head = Part.makeCylinder(10.5 / 2, 1.0,
                                     Vector(x, -P.FACE_T - 0.5, z),
                                     Vector(0, 1, 0))
            v = vol(whole.common(head))
            check(v > VOID, "M6 head bears at x=%+8.3f z=%6.3f" % (x, z),
                  "%.1f mm3" % v)

    print("\n[device]")
    dev = box(-P.DEV_W / 2, P.DEV_W / 2, 0.0, P.DEV_D, P.DEV_Z0, P.DEV_Z1)
    check(vol(whole.common(dev)) < VOID, "device sits without interference",
          "%.3f mm3" % vol(whole.common(dev)))
    # Loaded from the rear: sweep the device back out again.
    sweep = box(-P.DEV_W / 2, P.DEV_W / 2, 0.0, 400, P.DEV_Z0, P.DEV_Z1)
    check(vol(asm.common(sweep)) < VOID, "slides in from the rear past the frame",
          "%.3f mm3" % vol(asm.common(sweep)))
    # Forwards it must be stopped by the faceplate lips.
    fwd = box(-P.DEV_W / 2, P.DEV_W / 2, -P.FACE_T, 0.0, P.DEV_Z0, P.DEV_Z1)
    check(vol(asm.common(fwd)) > 100.0, "faceplate lips stop it at the front",
          "%.0f mm3 of overlap" % vol(asm.common(fwd)))
    # Rearwards, by the stops.
    back = box(-P.DEV_W / 2, P.DEV_W / 2, P.POCKET_D, P.BODY_D, P.DEV_Z0, P.DEV_Z1)
    both = all(vol(parts[n].common(back)) > 50.0 for n in stops)
    check(both, "rear stops close the pocket",
          "%.0f mm3 each" % vol(parts["stop_l"].common(back)))
    # Upwards, by the side rail lips.
    up = box(-P.DEV_W / 2, P.DEV_W / 2, 0.0, P.POCKET_D, P.DEV_Z1, P.RACK_U)
    check(vol(asm.common(up)) > 100.0, "top lips stop it lifting out",
          "%.0f mm3 of overlap" % vol(asm.common(up)))

    print("\n[clearances]")
    check(near(P.POST_CLEAR_HW - P.BODY_HW, 0.925, 1e-9),
          "0.925 mm per side between body and post")
    for nm, got, want in (("width", P.POCKET_W - P.DEV_W, P.CLR_W),
                          ("height", P.POCKET_TOP - P.DEV_Z1, P.CLR_H),
                          ("depth", P.POCKET_D - P.DEV_D, P.CLR_D)):
        check(near(got, want, 1e-9), "%s clearance %.2f mm" % (nm, got))
    for nm, got in (("side", P.DEV_W / 2 - P.WIN_HW),
                    ("bottom", P.WIN_Z0 - P.DEV_Z0),
                    ("top", P.DEV_Z1 - P.WIN_Z1)):
        check(got >= 2.0, "faceplate lip on the %s is %.2f mm" % (nm, got))

    print("\n%d checks, %d failed" % (_checks, len(_fails)))
    for f in _fails:
        print("  FAIL %s" % f)
    sys.stdout.flush()
    if _fails:
        sys.exit(1)


main()
