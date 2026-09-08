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

import math  # noqa: E402

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


def nut(xc, zc, af, y0, y1):
    """A real hex nut as a solid, flats top and bottom, axis along Y."""
    r = af / math.sqrt(3.0)
    pts = [Vector(xc + r * math.cos(math.radians(a)), y0,
                  zc + r * math.sin(math.radians(a)))
           for a in (0, 60, 120, 180, 240, 300)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(
        Vector(0.0, y1 - y0, 0.0))


def vnut(xc, yc, af, z0, z1):
    """The same, axis along Z."""
    r = af / math.sqrt(3.0)
    pts = [Vector(xc + r * math.cos(math.radians(a)),
                  yc + r * math.sin(math.radians(a)), z0)
           for a in (0, 60, 120, 180, 240, 300)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(
        Vector(0.0, 0.0, z1 - z0))


def main():
    parts = model.build_parts()
    frame = ("tray", "top_bar", "ear_l", "ear_r")

    asm = parts[frame[0]]
    for n in frame[1:]:
        asm = asm.fuse(parts[n])
    asm = asm.removeSplitter()

    whole = asm

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
    # Lowered in from above, before the top bar and the stops go on.
    cradle = parts["tray"].fuse(parts["ear_l"]).fuse(parts["ear_r"])
    drop = box(-P.DEV_W / 2, P.DEV_W / 2, 0.0, P.DEV_D, P.DEV_Z0, 400)
    check(vol(cradle.common(drop)) < VOID, "drops in from above into the cradle",
          "%.3f mm3" % vol(cradle.common(drop)))
    # Forwards it must be stopped by the faceplate lips.
    fwd = box(-P.DEV_W / 2, P.DEV_W / 2, -P.FACE_T, 0.0, P.DEV_Z0, P.DEV_Z1)
    check(vol(asm.common(fwd)) > 100.0, "faceplate lips stop it at the front",
          "%.0f mm3 of overlap" % vol(asm.common(fwd)))
    # Rearwards, by the ear's rear beam where it runs forward to the device.
    back = box(-P.DEV_W / 2, P.DEV_W / 2, P.POCKET_D, P.BODY_D, P.DEV_Z0, P.DEV_Z1)
    each = min(vol(parts[n].common(back)) for n in ("ear_l", "ear_r"))
    check(each > 500.0, "the ear's rear beam stops the device",
          "%.0f mm3 of overlap each" % each)
    # Upwards: the top bar's flange at the front, the stops at the back.
    over = box(-P.DEV_W / 2, P.DEV_W / 2, 0.0, P.DEV_D, P.DEV_Z1, P.RACK_U)
    vf = vol(parts["top_bar"].common(over))
    check(vf > 100.0, "top bar holds the device down at the front",
          "%.0f mm3 over it" % vf)
    # And the top bar must go on after the device, not before.
    check(vol(parts["top_bar"].common(drop)) > 100.0,
          "top bar is fitted after the device", "it overhangs the drop path")

    print("\n[faceplate joints -- M3 through the lap into a trapped nut]")
    NUT3_AF, NUT3_T = 5.5, 2.4
    for sx in (-1, 1):
        for x in P.JOINT_SCREW_X:
            for z in P.JOINT_SCREW_Z:
                xc = sx * x
                shank = Part.makeCylinder(
                    3.0 / 2, P.FACE_T, Vector(xc, -P.FACE_T - 0.05, z),
                    Vector(0, 1, 0))
                v = vol(asm.common(shank))
                check(v < VOID, "M3 shank clear at x=%+7.2f z=%5.2f" % (xc, z),
                      "%.3f mm3" % v)
    for sx in (-1, 1):
        for x in P.JOINT_SCREW_X:
            for z in P.JOINT_SCREW_Z:
                xc = sx * x
                n = nut(xc, z, NUT3_AF, -P.FACE_T / 2 + 0.05,
                        -P.FACE_T / 2 + 0.05 + NUT3_T)
                v = vol(asm.common(n))
                check(v < VOID, "M3 nut seats at x=%+7.2f z=%5.2f" % (xc, z),
                      "%.3f mm3" % v)
                # ... and can be dropped in from the nearest outside face.
                to = 0.0 if z < P.WIN_Z1 else P.RACK_U
                path = box(xc - NUT3_AF / 2, xc + NUT3_AF / 2,
                           -P.FACE_T / 2 + 0.05,
                           -P.FACE_T / 2 + 0.05 + NUT3_T, z, to)
                v = vol(asm.common(path))
                check(v < VOID, "M3 nut can be fed in at x=%+7.2f z=%5.2f"
                      % (xc, z), "%.3f mm3" % v)

    print("\n[rear joints -- M6 into a trapped nut, behind the device]")
    NUT6_AF, NUT6_T = 10.0, 5.0
    for sx in (-1, 1):
        for x, z0 in [(a, b) for a in P.REAR_BOLT_X for b in P.REAR_BOLT_Z]:
            xc, z = sx * x, z0
            shank = Part.makeCylinder(
                6.0 / 2, P.REAR_Y1 - P.REAR_Y_MID + P.M6_HEX_D + 0.2,
                Vector(xc, P.REAR_Y_MID - P.M6_HEX_D - 0.1, z), Vector(0, 1, 0))
            v = vol(asm.common(shank))
            check(v < VOID, "M6 shank clear at x=%+7.2f z=%4.1f" % (xc, z), "%.3f mm3" % v)
            n = nut(xc, z, NUT6_AF, P.REAR_Y_MID - P.M6_HEX_D + 0.05,
                    P.REAR_Y_MID - 0.05)
            v = vol(asm.common(n))
            check(v < VOID, "M6 nut seats at x=%+7.2f z=%4.1f" % (xc, z), "%.3f mm3" % v)
            path = box(xc - NUT6_AF / 2, xc + NUT6_AF / 2,
                       P.REAR_Y_MID - P.M6_HEX_D + 0.05, P.REAR_Y_MID - 0.05,
                       z, P.REAR_Z1)
            v = vol(asm.common(path))
            check(v < VOID, "M6 nut can be fed in at x=%+7.2f z=%4.1f" % (xc, z),
                  "%.3f mm3" % v)
            # The bolt must not reach the device: an M6x10 tip stops short.
            tip = P.REAR_Y1 - P.M6_CB_Y - 10.0
            check(tip > P.POCKET_D, "M6x10 tip clears the device at x=%+7.2f z=%4.1f"
                  % (xc, z), "tip Y=%.1f, device ends %.1f" % (tip, P.POCKET_D))

    print("\n[the tray has to bear on the ear, not hang off bolts]")
    for y in (10.0, 50.0, 90.0, 125.0):
        band = box(P.STEP_X0, P.LAP_X, y - 5, y + 5, -1.0, P.FLOOR_T + 1)
        ve = vol(parts["ear_r"].common(band))
        vt = vol(parts["tray"].common(band))
        check(ve > 50.0 and vt > 50.0,
              "step lap carries load at Y=%5.1f" % y,
              "ear %.0f mm3, tray %.0f mm3" % (ve, vt))
    # The ear's half of the lap must be the lower one, or it would print in air.
    low = box(P.STEP_X0, P.LAP_X, 40.0, 60.0, -1.0, P.STEP_Z - 0.1)
    check(vol(parts["tray"].common(low)) < VOID,
          "the ear takes the underside of the lap",
          "%.3f mm3 of tray below it" % vol(parts["tray"].common(low)))
    # The rear block has to be tied out to the side rail.
    web = box(P.LAP_X, P.BODY_HW, P.REAR_Y_MID, P.REAR_Y1, 0.0, P.REAR_Z1)
    check(vol(parts["ear_r"].common(web)) > 1000.0,
          "rear block is webbed out to the side rail",
          "%.0f mm3 of web" % vol(parts["ear_r"].common(web)))

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
