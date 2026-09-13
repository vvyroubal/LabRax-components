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
import devices  # noqa: E402

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


def hexnut2(cy, cz, af, x0, x1):
    """A hex nut lying with its axis along X, flats facing the slot walls.

    That is how a nut dropped into a slot sits: `af` across in Y, and the
    corners -- af * 2 / sqrt(3) -- standing up in Z.
    """
    r = af / math.sqrt(3.0)
    pts = [Vector(x0, cy + r * math.cos(math.radians(a)),
                  cz + r * math.sin(math.radians(a)))
           for a in (30, 90, 150, 210, 270, 330)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(
        Vector(x1 - x0, 0, 0))


def hexnut3(cx, cz, af, y0, y1):
    """A hex nut with its axis along Y, flats facing the slot walls."""
    r = af / math.sqrt(3.0)
    pts = [Vector(cx + r * math.cos(math.radians(a)), y0,
                  cz + r * math.sin(math.radians(a)))
           for a in (0, 60, 120, 180, 240, 300)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(
        Vector(0, y1 - y0, 0))


def hexnut4(sx, y, z, af):
    """An M6 nut in a splice boss, axis along X."""
    r = af / math.sqrt(3.0)
    x0 = sx * (P.POCKET_HW - P.SPLICE_BOSS_T) + sx * 0.05
    x1 = x0 + sx * (P.M6_HEX_D - 0.1)
    # Same phase as sk.hexagon, which is what cut the pocket: vertices along
    # Y, flats top and bottom. Thirty degrees out and the corners foul.
    pts = [Vector(x0, y + r * math.cos(math.radians(a)),
                  z + r * math.sin(math.radians(a)))
           for a in (0, 60, 120, 180, 240, 300)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(
        Vector(x1 - x0, 0, 0))


def stadium(cx, cz, w, h, y0, y1):
    """A slot-shaped solid bored along +Y: `w` long, `h` across, round ends."""
    r = h / 2.0
    flat = w - h
    sol = box(cx - flat / 2, cx + flat / 2, y0, y1, cz - r, cz + r)
    for x in (cx - flat / 2, cx + flat / 2):
        sol = sol.fuse(Part.makeCylinder(r, y1 - y0, Vector(x, y0, cz),
                                         Vector(0, 1, 0)))
    return sol


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
    keys = os.environ.get("UCG_DEVICE", "").split(",")
    todo = [d for d in devices.ALL if not keys[0] or d.key in keys]

    # Everything below is checked once per device: the chassis is shared, so
    # it has to be shown to work with each of them, and two devices' trays
    # occupy the same space by design -- they are never in the rack together.
    for dev in todo:
        doc = App.newDocument("check_" + dev.key)
        bodies = model.build(doc, only=dev)
        doc.recompute()
        parts = {n: b.Shape for n, b in bodies.items()}
        print("\n" + "=" * 62)
        print("== %s  %.1f x %.1f x %.1f, %d g"
              % (dev.name, dev.w, dev.d, dev.h, dev.mass_g))
        print("=" * 62)
        print("\n[parts]")
        for n in sorted(parts):
            sh = parts[n]
            check(sh.isValid() and len(sh.Solids) == 1,
                  "%-14s is one valid solid" % n, "%d solids" % len(sh.Solids))
            ok, how = fits_bed(sh.BoundBox)
            check(ok, "%-14s fits the A1 mini bed" % n, how)
            b = bodies[n]
            sk_ = [o for o in b.Group if o.TypeId == "Sketcher::SketchObject"]
            so = [o for o in b.Group
                  if o.TypeId in ("PartDesign::Pad", "PartDesign::Pocket")]
            check(len(sk_) > 0 and len(so) > 0,
                  "%-14s is sketches driving solids" % n,
                  "%d sketches, %d pads/pockets" % (len(sk_), len(so)))
        one_device(parts, bodies, dev)


def one_device(parts, bodies, dev):
    names = ["side_l", "side_r", "leg_l", "leg_r",
             dev.part("tray_l"), dev.part("tray_r"), dev.part("faceplate")]
    asm = parts[names[0]]
    for n in names[1:]:
        asm = asm.fuse(parts[n])
    asm = asm.removeSplitter()
    front = dev.front
    lip_x = (dev.hw + P.TRAY_WALL_T) if dev.walls else P.REAR_LIP_X

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
    check(P.POST_CLEAR_HW - hw >= 0.5, "body passes between the posts",
          "half-width %.3f, limit %.3f, clearance %.3f per side"
          % (hw, P.POST_CLEAR_HW, P.POST_CLEAR_HW - hw))

    print("\n[rack screws -- M6 from outside into the post's own nut]")
    for tag, y_out, into in (("front", -P.EAR_T, +1),
                             ("rear", P.RACK_D + P.EAR_T, -1)):
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

    print("\n[the rear legs -- reaching the back posts]")
    check(abs(P.RACK_D - (P.RACK_INNER + 2 * P.POST_D)) < 1e-9,
          "outer depth is the clear gap plus both posts",
          "%.1f = %.1f + 2 x %.1f" % (P.RACK_D, P.RACK_INNER, P.POST_D))
    check(abs(P.RACK_INNER - 170.0) < 1e-9,
          "the clear gap comes from the frame beams, not the side panel",
          "170.0, the length of three members in the rack's own 3MF")
    # The nut must travel as far as its bolt, and its pocket must not end
    # flush with the slot -- that tangency is what broke the solid before.
    check(abs((P.LEG_NUT_SLOT - 2 * P.M6_HEX_AF / 3 ** 0.5)
              - (P.LEG_SLOT - P.M6_CLEAR)) < 1e-6,
          "the leg's nut travels exactly as far as its bolt",
          "%.2f mm each" % (P.LEG_SLOT - P.M6_CLEAR))
    check(P.LEG_NUT_SLOT > P.LEG_SLOT + 1.0,
          "the nut pocket runs past the ends of the bolt slot",
          "%.2f vs %.2f" % (P.LEG_NUT_SLOT, P.LEG_SLOT))
    for sx, nm in ((-1, "leg_l"), (1, "leg_r")):
        lg = parts[nm]
        b = lg.BoundBox
        check(abs(b.YMax - (P.RACK_D + P.EAR_T)) < 1e-6,
              "%s reaches the back of the rear post" % nm,
              "ends at Y %.1f, post rear face at %.1f" % (b.YMax, P.RACK_D))
        # It has to lap the side over a real length, not just touch it.
        lap = box(sx * P.POCKET_HW, sx * (P.POCKET_HW - P.SPLICE_T),
                  P.SPLICE_Y0, P.SPLICE_Y1, 0.0, P.RAIL_TOP)
        vl = vol(lg.common(lap))
        side = parts["side_l" if sx < 0 else "side_r"]
        vs = vol(side.common(box(sx * P.POCKET_HW, sx * P.BODY_HW,
                                 P.SPLICE_Y0, P.SPLICE_Y1, 0.0, P.RAIL_TOP)))
        check(vl > 3000.0 and vs > 3000.0, "%s laps the side over %.0f mm"
              % (nm, P.SPLICE_Y1 - P.SPLICE_Y0),
              "%.0f mm3 of leg against %.0f mm3 of rail" % (vl, vs))
        check(vol(lg.common(side)) < VOID, "%s does not foul the side" % nm,
              "%.3f mm3" % vol(lg.common(side)))
    # The splice bolts, and the range they give. Both halves are slotted, so
    # the travel is the sum: the side's slot plus the leg's.
    adj = ((P.SPLICE_SLOT - P.M6_CLEAR) + (P.LEG_SLOT - P.M6_CLEAR)) / 2.0
    lo, hi = P.RACK_D - adj, P.RACK_D + adj
    check(adj >= 18.0, "the splice adjusts far enough to be set by fitting",
          "+/-%.1f mm, so %.1f..%.1f outer depth" % (adj, lo, hi))
    # It must reach BOTH readings the rack's own parts give, since the mesh
    # does not say which way the 30 x 35 post faces.
    for d in (170.0 + 2 * 30.0, 170.0 + 2 * 35.0):
        check(lo <= d <= hi, "it reaches a %.0f mm rack" % d,
              "%.1f..%.1f covers it" % (lo, hi))
    # And it must NOT still reach the reading that caused the problem, or the
    # same mistake just gets made at the other end of the slot.
    check(hi < 245.9 + 10.0, "the old 245.9 reading is no longer the middle",
          "nominal now %.1f" % P.RACK_D)
    for sx in (-1, 1):
        lg = parts["leg_l" if sx < 0 else "leg_r"]
        side = parts["side_l" if sx < 0 else "side_r"]
        for y in P.SPLICE_BOLT_Y:
            shank = Part.makeCylinder(
                3.0, P.RAIL_T + P.SPLICE_T + P.SPLICE_BOSS_T,
                Vector(sx * P.BODY_HW, y, P.SPLICE_BOLT_Z), Vector(-sx, 0, 0))
            v = vol(side.common(shank)) + vol(lg.common(shank))
            check(v < VOID, "splice M6 passes both at y=%5.1f" % y,
                  "%.3f mm3" % v)
            n = hexnut4(sx, y, P.SPLICE_BOLT_Z, 10.0)
            check(vol(lg.common(n)) < VOID, "its nut seats at y=%5.1f" % y,
                  "%.3f mm3" % vol(lg.common(n)))
        # And both really are slots, not holes. The travel adds up across the
        # joint, but each part only ever sees its OWN slot's half of it --
        # testing either one at the full +/-19.6 would be testing a position
        # the bolt never reaches in that part.
        side_adj = (P.SPLICE_SLOT - P.M6_CLEAR) / 2.0
        leg_adj = (P.LEG_SLOT - P.M6_CLEAR) / 2.0
        for y in P.SPLICE_BOLT_Y:
            for d in (-side_adj, side_adj):
                sh = Part.makeCylinder(3.0, P.RAIL_T + 0.2,
                                       Vector(sx * P.BODY_HW, y + d,
                                              P.SPLICE_BOLT_Z),
                                       Vector(-sx, 0, 0))
                check(vol(side.common(sh)) < VOID,
                      "side slot clears at y=%5.1f%+5.1f" % (y, d),
                      "%.3f mm3" % vol(side.common(sh)))
            for d in (-leg_adj, leg_adj):
                sh = Part.makeCylinder(
                    3.0, P.SPLICE_BOSS_T + 0.2,
                    Vector(sx * (P.POCKET_HW - P.SPLICE_BOSS_T), y + d,
                           P.SPLICE_BOLT_Z), Vector(sx, 0, 0))
                check(vol(lg.common(sh)) < VOID,
                      "leg slot clears at y=%5.1f%+5.1f" % (y, d),
                      "%.3f mm3" % vol(lg.common(sh)))
            # the nut has to follow the bolt the whole way
            for d in (-leg_adj, leg_adj):
                n = hexnut4(sx, y + d, P.SPLICE_BOLT_Z, 10.0)
                check(vol(lg.common(n)) < VOID,
                      "its nut still seats at y=%5.1f%+5.1f" % (y, d),
                      "%.3f mm3" % vol(lg.common(n)))

    print("\n[the front face -- one plate, with a window for the display]")
    fp = parts[dev.part("faceplate")]
    check(len(fp.Solids) == 1, "the faceplate is one solid", "%d" % len(fp.Solids))
    b = fp.BoundBox
    check(abs(b.ZMin) < 1e-6 and abs(b.ZMax - P.RACK_U) < 1e-6,
          "it covers the whole height of the U", "Z %.2f..%.2f" % (b.ZMin, b.ZMax))
    check(b.XLength >= dev.w, "and the whole width of the gateway's face",
          "%.1f mm across a %.1f mm face" % (b.XLength, dev.w))
    for sx in (-1, 1):
        rail = box(sx * P.POCKET_HW, sx * P.BODY_HW, -1.0, P.RACK_D,
                   0.0, P.RAIL_TOP)
        check(vol(fp.common(rail)) < VOID,
              "it clears the rail at x=%+6.1f" % (sx * P.POCKET_HW),
              "%.3f mm3" % vol(fp.common(rail)))
    if front.kind == "window":
        # The window, against the display it has to show. The display is placed
        # from ITS OWN measured height, never from the window's -- the old check
        # built the panel at front.z(dev), so the window was compared against itself
        # and would have passed at any height at all. That is why a window 5 mm
        # low got printed. Modelled as the stadium it is: a sharp-cornered
        # rectangle would report the window's own radii as clipping.
        disp = stadium(0.0, front.z(dev), front.disp_w, front.disp_h,
                       -1.0, P.BAR_T + 1.0)
        check(vol(fp.common(disp)) < VOID, "the display is not clipped",
              "%.3f mm3 across the %.1f x %.1f panel"
              % (vol(fp.common(disp)), front.disp_w, front.disp_h))
        # The window has to be concentric with it, with margin left all round.
        for nm, w, d in (("above and below", front.h, front.disp_h),
                         ("each side", front.w, front.disp_w)):
            check((w - d) / 2.0 >= 0.5, "margin %s the display" % nm,
                  "%.2f mm" % ((w - d) / 2.0))
        # THE RULE: the oval's top edge sits exactly 5.0 mm below the underside of
        # the top bar. Both edges are found on the BUILT SOLID, by scanning for
        # where material starts and stops -- not read back out of params, which
        # would prove nothing.
        def solid_at(y, x, z):
            """Is there material at (x, y, z)?

            The probe is 4 x 1 x 0.4 mm -- 1.6 mm3 when fully buried, well
            over the 1 mm3 noise floor. A thinner one reads as empty
            everywhere and the scan silently finds nothing.
            """
            probe = box(x - 2.0, x + 2.0, y - 0.5, y + 0.5, z, z + 0.4)
            return vol(fp.common(probe)) > 1.5

        def scan_z(y, x, z0, z1, want, tol=0.01):
            """The z in [z0, z1] where material starts, by bisection.

            Material presence is monotonic over both ranges used here -- void
            below, solid above -- so halving beats stepping: a dozen booleans
            instead of the several hundred a 0.05 mm walk costs, and it is
            the more accurate of the two. Stepping the whole range twice over
            was enough to make this run die.
            """
            if solid_at(y, x, z0) == want:
                return z0
            if solid_at(y, x, z1) != want:
                return None
            lo, hi = z0, z1
            while hi - lo > tol:
                mid = (lo + hi) / 2.0
                if solid_at(y, x, mid) == want:
                    hi = mid
                else:
                    lo = mid
            return hi

        # behind the round-over, where the window is at full size
        win_top = scan_z(P.BAR_T - 1.0, 0.0, front.z(dev), P.RACK_U - 1.0, True)
        # inside the flange, which reaches back over the gateway
        bar_bottom = scan_z(P.BAR_T + 4.0, 0.0, 0.0, P.RACK_U - 1.0, True)
        check(win_top is not None and bar_bottom is not None,
              "the window's top edge and the top bar's underside are both found",
              "window top %s, bar underside %s" % (win_top, bar_bottom))
        if win_top is not None and bar_bottom is not None:
            gap = bar_bottom - win_top
            check(abs(gap - front.top_gap) < 0.1,
                  "the oval's top edge is %.1f mm below the top bar" % front.top_gap,
                  "measured %.2f mm on the solid: window top z=%.2f, "
                  "bar underside z=%.2f" % (gap, win_top, bar_bottom))
        # The round-over runs above the bar's line on the FRONT face, which is
        # fine -- the flange is 8 mm behind it and the plate is solid up there --
        # but it must not reach the top of the plate.
        rim = front.z(dev) + front.h / 2.0 + front.fillet
        check(rim < P.RACK_U - 2.0,
              "the rounded rim stays inside the plate",
              "reaches z=%.1f of %.2f" % (rim, P.RACK_U))
        check(front.w > front.disp_w and front.h > front.disp_h,
              "the window is larger than the display it shows",
              "%.1f x %.1f against %.1f x %.1f"
              % (front.w, front.h, front.disp_w, front.disp_h))
        check(front.z(dev) - front.h / 2 > dev.z0 and front.z(dev) + front.h / 2 < dev.z1,
              "and lies within the gateway's face",
              "Z %.1f..%.1f inside %.0f..%.0f"
              % (front.z(dev) - front.h / 2, front.z(dev) + front.h / 2, dev.z0, dev.z1))
        # The window's front edge is rounded over. Check the round is there by
        # looking for material that a sharp-edged window would still have: just
        # outside the window's outline, at the front face.
        r = front.fillet
        # Thin in Y: a round-over has curved well in by even half a millimetre
        # of depth, so a deeper probe measures the round itself, not a corner.
        flare = box(-4.0, 4.0, 0.0, 0.2,
                    front.z(dev) + front.h / 2 + 0.4, front.z(dev) + front.h / 2 + 4.0)
        check(vol(fp.common(flare)) < VOID,
              "the window's front edge is rounded over",
              "%.1f mm radius, %.3f mm3 of square corner left"
              % (r, vol(fp.common(flare))))
        # ...and that it has not eaten through to the back, where the window has
        # to stay the size the display needs.
        back = stadium(0.0, front.z(dev), front.disp_w, front.disp_h,
                       P.BAR_T - 0.5, P.BAR_T + 0.5)
        check(vol(fp.common(back)) < VOID,
              "and has not narrowed the window at the back",
              "%.3f mm3" % vol(fp.common(back)))
        check(r < P.BAR_T, "the round leaves wall behind it",
              "%.1f mm radius in a %.1f mm plate, %.1f mm left"
              % (r, P.BAR_T, P.BAR_T - r))

    else:
        # A frame, not a window: the opening is onto the ports, and its job is
        # to let a plug in while not letting the case out.
        w, h, z = front.w(dev), front.h(dev), front.z(dev)
        check(w < dev.w and h < dev.h,
              "the case cannot pass through its own opening",
              "case %.1f x %.1f, opening %.1f x %.1f" % (dev.w, dev.h, w, h))
        check(front.border_x >= 2.0 and front.border_z >= 1.0,
              "the border that holds it in is worth having",
              "%.2f mm each side, %.2f mm top and bottom"
              % (front.border_x, front.border_z))
        # An RJ45 with its latch is about 12 x 16. It has to pass the opening
        # AND the 8 mm of plate behind it, so the probe is swept the whole way.
        plug = box(-6.0, 6.0, -1.0, P.BAR_T + 1.0, z - 8.0, z + 8.0)
        check(vol(fp.common(plug)) < VOID,
              "an RJ45 plug passes the opening and the plate behind it",
              "%.3f mm3 in the way of a 12 x 16 plug" % vol(fp.common(plug)))
        # The opening must sit on the ports, which are on the case's face.
        check(z - h / 2 > dev.z0 and z + h / 2 < dev.z1,
              "the opening lies within the case's face",
              "Z %.2f..%.2f inside %.2f..%.2f"
              % (z - h / 2, z + h / 2, dev.z0, dev.z1))
        check(abs(z - P.RACK_U / 2.0) < 0.5,
              "and is centred in the U, because it is what you look at",
              "opening centre z=%.3f, U centre %.3f" % (z, P.RACK_U / 2.0))
        # Nothing in front of the case except that border.
        face = box(-dev.w / 2, dev.w / 2, 0.0, dev.y0, dev.z0, dev.z1)
        held = vol(fp.common(face))
        check(held > 500.0, "the frame stands in front of the case all round",
              "%.0f mm3 of border over its face" % held)

    ahead = box(-P.FACE_HW, P.FACE_HW, -P.EAR_T + 0.01, 0.0, 0.0, P.RACK_U)
    stray = [n for n in names
             if n not in ("side_l", "side_r")
             and vol(parts[n].common(ahead)) > VOID]
    check(not stray, "nothing protrudes into the reveal",
          ", ".join(stray) if stray else "clear")
    for sx in (-1, 1):
        for z in (P.BAR_SCREW_Z, P.BOT_SCREW_Z):
            x = sx * P.BAR_SCREW_X
            # Against the whole assembly, not just the plate the pocket is
            # in: a nut can sit happily in its pocket and still foul the rail
            # beside it.
            n = hexnut3(x, z, 10.0, P.BAR_NUT_Y0 + 0.05,
                        P.BAR_NUT_Y0 + P.M6_HEX_D - 0.05)
            check(vol(asm.common(n)) < VOID,
                  "M6 nut seats clear of everything at x=%+7.2f z=%5.2f" % (x, z),
                  "%.3f mm3" % vol(asm.common(n)))
            through = Part.makeCylinder(3.0, P.EAR_T + P.BAR_NUT_Y0 + 0.1,
                                        Vector(x, -P.EAR_T - 0.05, z),
                                        Vector(0, 1, 0))
            check(vol(asm.common(through)) < VOID,
                  "its screw reaches through the ear at x=%+7.2f z=%5.2f"
                  % (x, z), "%.3f mm3" % vol(asm.common(through)))

    print("\n[device]")
    case = box(-dev.w / 2, dev.w / 2, dev.y0, dev.y0 + dev.d,
               dev.z0, dev.z1)
    check(vol(asm.common(case)) < VOID, "device sits without interference",
          "%.3f mm3" % vol(asm.common(case)))
    cradle = parts["side_l"].fuse(parts["side_r"]).fuse(
        parts[dev.part("tray_l")]).fuse(parts[dev.part("tray_r")])
    drop = box(-dev.w / 2, dev.w / 2, dev.y0, dev.y0 + dev.d,
               dev.z0, 400)
    check(vol(cradle.common(drop)) < VOID, "drops in from above between the sides",
          "%.3f mm3" % vol(cradle.common(drop)))
    shelf = box(-dev.w / 2, dev.w / 2, dev.y0, dev.y0 + dev.d,
                dev.z0 - 2.0, dev.z0)
    check(vol(cradle.common(shelf)) > 20000.0, "the tray carries it",
          "%.0f mm3 under it" % vol(cradle.common(shelf)))
    fwd = box(-dev.w / 2, dev.w / 2, dev.y0 - P.BAR_T, dev.y0,
              dev.z0, dev.z1)
    check(vol(asm.common(fwd)) > 100.0, "stopped at the front",
          "%.0f mm3" % vol(asm.common(fwd)))
    back = box(-dev.w / 2, dev.w / 2, dev.y1, dev.y1 + P.STOP_T,
               dev.z0, dev.z1)
    check(vol(asm.common(back)) > 100.0, "stopped at the rear",
          "%.0f mm3" % vol(asm.common(back)))
    # And it must not be able to leave through the front once the bar is on.
    # The top bar's end blocks reach down to BAR_END_Z0 and stand directly in
    # front of the device's face at each end; nothing else does.
    for push in (1.5, 5.0, 20.0):
        moved = box(-dev.w / 2, dev.w / 2, dev.y0 - push,
                    dev.y0 + dev.d - push, dev.z0, dev.z1)
        v = vol(asm.common(moved))
        check(v > 50.0, "cannot be pushed %.1f mm out of the front" % push,
              "%.0f mm3 of interference" % v)
    face = box(-dev.w / 2, dev.w / 2, dev.y0 - P.BAR_T, dev.y0,
               dev.z0, dev.z1)
    half = box(-dev.w / 2, 0.0, dev.y0 - P.BAR_T, dev.y0,
               dev.z0, dev.z1)
    per = vol(fp.common(half))
    # A window covers the face and shows a sliver of it; a frame deliberately
    # opens most of it and keeps only a border. Ask for the border, not for a
    # fixed volume that only a covered face can reach.
    want = 3000.0 if dev.front.kind == "window" else 500.0
    check(per > want, "the faceplate stands across the device's face",
          "%.0f mm3 of it on each half, wanted %.0f" % (per, want))

    over = box(-dev.w / 2, dev.w / 2, dev.y0, dev.y0 + dev.d,
               dev.z1, P.RACK_U)
    check(vol(fp.common(over)) > 100.0, "the faceplate's flange caps it",
          "%.0f mm3 over it" % vol(fp.common(over)))

    print("\n[the tray]")
    trays = parts[dev.part("tray_l")].fuse(parts[dev.part("tray_r")]).removeSplitter()
    # It must be a floor, not two ledges: solid under the device all the way
    # across, at every depth.
    for x in (-100.0, -60.0, -16.0, 0.0, 16.0, 60.0, 100.0):
        col = box(x - 4, x + 4, dev.y0 + 4, dev.y1 - 4, 0.0, dev.z0)
        v = vol(trays.common(col))
        check(v > 300.0, "tray carries the device at x=%+7.1f" % x,
              "%.0f mm3" % v)
    # Each half laps onto its side's ledge for the whole depth.
    for sx, side in ((-1, "side_l"), (1, "side_r")):
        band = box(sx * P.LEDGE_X0, sx * P.TRAY_X1, dev.y0, dev.y1,
                   0.0, P.TRAY_T)
        vt = vol(trays.common(band))
        vs = vol(parts[side].common(band))
        check(vt > 1000.0 and vs > 1000.0, "%s carries the tray's edge" % side,
              "ledge %.0f mm3 under tray %.0f mm3" % (vs, vt))
    # The centre lap has to overlap, not just butt.
    lap = box(-P.CENTRE_LAP, P.CENTRE_LAP, dev.y0, dev.y1, 0.0, P.TRAY_T)
    check(vol(parts[dev.part("tray_l")].common(lap)) > 1000.0
          and vol(parts[dev.part("tray_r")].common(lap)) > 1000.0,
          "the halves lap on the centreline",
          "%.0f / %.0f mm3" % (vol(parts[dev.part("tray_l")].common(lap)),
                               vol(parts[dev.part("tray_r")].common(lap))))
    # No bolt across this joint: the tab that used to carry one snapped off
    # both halves when it was tightened. Nothing may stand behind the gateway
    # where it did, either -- that is where its rear ports are. The rear lip
    # is the one thing allowed back there, and only below the ports, so the
    # clear volume is measured from the top of the lip upwards.
    # Measured between the sides' rear stops: the outer 7.4 mm at each end is
    # covered full height by the stop and the rear leg behind it, and always
    # has been. Everything in from there must stay open above the lip.
    # Every device has something on its back -- ports, or at least a power
    # socket -- so this runs whatever way it faces. Measured across the case's
    # own width, or as much of it as the lip spans, whichever is narrower:
    # wider than the case would count the sides' rear stops for a device that
    # fills the bay, and the tray's own walls for one that does not. Neither
    # is behind the case.
    span = min(dev.w / 2.0, lip_x)
    ports_z0 = dev.z0 + P.REAR_LIP_H
    behind = box(-span, span, dev.y0 + dev.d,
                 dev.y0 + dev.d + 25.0, ports_z0, dev.z1)
    v = vol(asm.common(behind))
    check(v < VOID, "the back of the case is clear above the lip",
          "%.3f mm3 in the 25 mm behind its %.0f mm, above z=%.2f"
          % (v, 2 * span, ports_z0))

    # And say plainly how much of each end is blocked, where anything is, so
    # the one thing this bracket does cover is a number rather than a surprise.
    if dev.w / 2.0 > lip_x:
        ends = box(lip_x, dev.w / 2, dev.y0 + dev.d,
                   dev.y0 + dev.d + 25.0, ports_z0, dev.z1)
        check(vol(asm.common(ends)) > VOID,
              "the outer %.1f mm of each end is blocked by the stop and leg"
              % (dev.w / 2 - lip_x),
              "keep plugs out of the last %.1f mm" % (dev.w / 2 - lip_x))
    else:
        check(True, "nothing overhangs the ends of the case",
              "it is narrower than the lip behind it")

    check(P.REAR_LIP_H <= 3.0, "the rear lip stays low enough to miss a port",
          "%.1f mm above the tray" % P.REAR_LIP_H)

    # --- the lip that stops the gateway sliding back ----------------------
    # Before this existed the only thing behind the gateway was the two rear
    # stops on the sides, reaching in to x = +/-99: 7.4 mm of overlap at each
    # end of a 212.8 mm rear face. The lip covers what is between them.
    lip = box(-dev.w / 2, dev.w / 2, dev.y0 + dev.d,
              dev.y0 + dev.d + 25.0, dev.z0, dev.z0 + P.REAR_LIP_H)
    v = vol(trays.common(lip))
    check(v > 1000.0, "the tray has a lip behind the gateway",
          "%.0f mm3 of it" % v)

    # Walk the rear face and ask, at each x, whether ANYTHING is behind it.
    # This is the check that would have caught the missing lip: the parts all
    # fitted, nothing overlapped, and 93% of the back was still open.
    # 2 mm stride: the gap this caught was 198 mm wide, so nothing that
    # matters hides between samples, and it halves a slow walk that now runs
    # once per device.
    gaps = []
    for i in range(0, int(dev.w / 2.0) + 1):
        x = -dev.w / 2 + 2.0 * i
        probe = box(x - 0.4, x + 0.4, dev.y0 + dev.d + 0.05,
                    dev.y0 + dev.d + P.REAR_LIP_H + 2.0,
                    dev.z0 + 0.2, dev.z0 + P.REAR_LIP_H - 0.2)
        if vol(asm.common(probe)) < VOID:
            gaps.append(x)
    check(not gaps, "something is behind the gateway across its whole width",
          "unbacked at x = %s" % (gaps[:6] if gaps else "nowhere"))

    # The lip must not foul the sides' rear stops, which start where it ends.
    v = vol(trays.common(parts["side_l"].fuse(parts["side_r"])))
    check(v < VOID, "the tray's lip clears the sides' rear stops",
          "%.3f mm3 shared" % v)

    # It has to be behind the gateway, not under it: the case sits on the
    # tray, so a lip that started too far forward would hold it off the floor.
    for nm in (dev.part("tray_l"), dev.part("tray_r")):
        under = box(-dev.w / 2, dev.w / 2, dev.y0,
                    dev.y0 + dev.d, dev.z0 + 0.05, dev.z1)
        v = vol(parts[nm].common(under))
        check(v < VOID, "%s stays below the gateway it carries" % nm,
              "%.3f mm3 in the way" % v)

    # Four pegs key the halves instead.
    # The pegs that key the front of the joint, where no bolt will fit.
    for kx in (-P.KEY_X, P.KEY_X):
        for ky in dev.keys_y:
            peg = Part.makeCylinder(P.KEY_D / 2, P.LAP_T - 0.1,
                                    Vector(kx, ky, 0.05), Vector(0, 0, 1))
            check(vol(parts[dev.part("tray_r")].common(peg)) > 20.0
                  and vol(parts[dev.part("tray_l")].common(peg)) < VOID,
                  "a peg keys the joint at x=%+6.1f y=%5.1f" % (kx, ky),
                  "%.0f mm3 of peg, %.3f in the socket"
                  % (vol(parts[dev.part("tray_r")].common(peg)),
                     vol(parts[dev.part("tray_l")].common(peg))))
    check(len(dev.keys_y) >= 2, "pegs at the front and the back of the lap",
          "rows at y = %s" % ", ".join("%.0f" % y for y in P.KEY_Y))
    # The lap has to be wide, because it is what holds the front together.
    check(2 * P.CENTRE_LAP >= 60.0, "the centre lap is at least 60 mm wide",
          "%.0f mm" % (2 * P.CENTRE_LAP))
    # And nothing may rise above the tray in front of the device.
    front = box(-dev.w / 2, dev.w / 2, -P.EAR_T, dev.y0,
                P.TRAY_T, P.RACK_U)
    v = vol(trays.common(front))
    check(v < VOID, "nothing stands in front of the device's face",
          "%.3f mm3" % v)
    # It has to be able to drop into the gap between the nib and the rear
    # stop, which means being shorter than it -- modelled flush, a printed
    # tray is an interference fit.
    edge = box(P.LEDGE_X0, P.TRAY_X1, -50, 400, P.LAP_T, P.TRAY_T)
    got = trays.common(edge).BoundBox.YLength
    gap = dev.y1 - dev.y0
    check(gap - got >= 0.3, "the tray drops into the gap it has to sit in",
          "%.2f mm long, %.2f mm gap, %.2f mm of fit" % (got, gap, gap - got))

    # Held fore and aft by the bottom bar and the rear stop, so it cannot walk.
    ahead = box(-P.TRAY_X1, P.TRAY_X1, dev.y0 - 1.0, dev.y0,
                0.0, P.TRAY_T)
    check(vol(fp.common(ahead)) > 100.0,
          "the faceplate stops the tray sliding forward",
          "%.0f mm3" % vol(fp.common(ahead)))

    print("\n[one screw size -- every joint takes an M6 x %.0f]" % P.SCREW_LEN)

    def screw(what, grip, nut_at, nut_thick, limit=None):
        """grip = solid before the nut; nut_at = where its near face is."""
        reach = P.SCREW_LEN - grip
        eng = reach - (nut_at - grip)
        ok = eng >= 3.0 and (limit is None or reach <= limit)
        check(ok, "%s" % what,
              "engages %.1f mm%s" % (eng, "" if limit is None
                                     else ", tip at %.1f of %.1f" % (reach, limit)))

    # Into the rack post's own nut. The hole is blind, so this one can fail
    # by being too long as well as too short.
    screw("rack screw reaches the post's nut", P.EAR_T,
          P.EAR_T + P.POST_CLEAR_D, P.POST_NUT_D,
          limit=P.EAR_T + P.POST_HOLE_D)
    screw("faceplate screw reaches its nut", P.EAR_T - P.BAR_CB_D,
          P.EAR_T - P.BAR_CB_D + P.BAR_NUT_Y0, P.M6_HEX_D)
    screw("splice screw reaches its nut", P.RAIL_T,
          P.RAIL_T + P.SPLICE_BOSS_T - P.M6_HEX_D, P.M6_HEX_D)


    print("\n[clearances]")
    check(abs((P.POST_CLEAR_HW - P.BODY_HW) - 0.925) < 1e-9,
          "0.925 mm per side between rail and post")
    check(abs((dev.flange_z0 - dev.z1) - dev.clr_h) < 1e-9,
          "height clearance %.2f mm" % (dev.flange_z0 - dev.z1))
    if dev.walls:
        # Narrower than the bay: its tray's walls hold it straight, and the
        # faceplate's border -- checked above -- is what stops it coming out.
        gap = 2 * dev.hw - dev.w
        check(abs(gap - dev.clr_w) < 1e-9,
              "width clearance between the tray's walls %.2f mm" % gap)
        check(2 * (dev.hw + P.TRAY_WALL_T) <= P.POCKET_W,
              "and those walls fit the bay",
              "%.1f mm across a %.1f mm bay"
              % (2 * (dev.hw + P.TRAY_WALL_T), P.POCKET_W))
    else:
        check(abs((P.POCKET_W - dev.w) - dev.clr_w) < 1e-9,
              "width clearance %.2f mm" % (P.POCKET_W - dev.w))
        check(2 * P.EAR_X0 < dev.w,
              "the ears overlap the device's ends, so it cannot slide out",
              "opening %.1f vs device %.1f" % (2 * P.EAR_X0, dev.w))

    print("\n%d checks, %d failed" % (_checks, len(_fails)))
    for f in _fails:
        print("  FAIL %s" % f)
    sys.stdout.flush()
    if _fails:
        sys.exit(1)


main()
