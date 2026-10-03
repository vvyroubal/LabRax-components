#!/usr/bin/env freecadcmd
"""Check the whole bracket as an assembly, with real fasteners.

verify.py walks the parts and the stack-up arithmetic. This does something
different and less forgiving: it puts a solid M6 x 12 screw and a solid M6 nut
at every one of the sixteen fastener positions and asks whether they fit
the geometry that was actually built. Arithmetic can agree with itself while
the hole is somewhere else entirely.

    make assembly

For each fastener it checks that the shank has clearance the whole way, that
the head has something to bear on, and that the nut sits in its pocket without
fouling anything. It then checks the parts against each other and the gateway
against all of them.

Exits non-zero on any failure.
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
        ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    except NameError:
        ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "common", "src"))

import FreeCAD as App  # noqa: E402
import Part  # noqa: E402
from FreeCAD import Vector  # noqa: E402

import params as P  # noqa: E402
import devices  # noqa: E402
import model  # noqa: E402

VOID = 1.0        # mm^3 below which an intersection is boolean noise
HEAD_D = 10.5     # an M6 button head
HEAD_H = 3.3
WASHER_D = 12.5   # M6 form A washer, 12.5 outside, 1.6 thick
WASHER_T = 1.6

# Below this the head is standing on too little plastic to tighten against.
# A slot is 6.4 wide and a head is 10.5 across, so on a slotted hole the head
# lands on two crescents and needs a washer to spread the load.
MIN_SEAT = 40.0   # mm2
SHANK_D = 5.9     # the screw itself, a hair under nominal
NUT_AF = 10.0
NUT_T = 5.0

_fails = []
_n = 0


def check(ok, what, detail=""):
    global _n
    _n += 1
    if not ok:
        _fails.append(what + ((" -- " + detail) if detail else ""))
    print("  %s  %-58s %s" % ("ok  " if ok else "FAIL", what, detail))


def vol(s):
    return 0.0 if s is None or not s.Solids else s.Volume


def cyl(d, length, base, axis):
    return Part.makeCylinder(d / 2.0, length, base, axis)


def hexprism(af, centre, axis, thick, phase=0.0):
    """A nut. `phase` 0 puts vertices on the first perpendicular axis."""
    r = af / math.sqrt(3.0)
    a = Vector(*axis).normalize()
    u = Vector(0, 0, 1).cross(a)
    if u.Length < 1e-6:
        u = Vector(1, 0, 0).cross(a)
    u.normalize()
    v = a.cross(u)
    pts = []
    for k in range(6):
        t = math.radians(60 * k + phase)
        p = Vector(*centre) + u * (r * math.cos(t)) + v * (r * math.sin(t))
        pts.append(p)
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(a * thick)


class Fastener:
    """One screw, where its head sits and which way it goes in."""

    def __init__(self, name, seat, axis, nut_at=None, phase=0.0, sunk=0.0,
                 washer=False):
        self.name = name
        self.washer = washer
        self.seat = Vector(*seat)     # underside of the head
        self.axis = Vector(*axis).normalize()
        self.nut_at = nut_at          # distance from the seat to the nut's face
        self.phase = phase
        self.sunk = sunk              # how far the head is recessed

    def shank(self):
        return cyl(SHANK_D, P.SCREW_LEN, self.seat, self.axis)

    def head(self):
        off = WASHER_T if self.washer else 0.0
        return cyl(HEAD_D, HEAD_H,
                   self.seat - self.axis * (HEAD_H + off), self.axis)

    def washer_solid(self):
        if not self.washer:
            return None
        return cyl(WASHER_D, WASHER_T,
                   self.seat - self.axis * WASHER_T, self.axis)

    def nut(self):
        if self.nut_at is None:
            return None
        c = self.seat + self.axis * self.nut_at
        return hexprism(NUT_AF, c, self.axis, NUT_T, self.phase)

    def bearing(self):
        """A thin disc of the part that the load lands on.

        It starts at the seat and goes into the material, not across it -- a
        disc straddling the face measures half air and reports half the seat.
        """
        d = WASHER_D if self.washer else HEAD_D
        return cyl(d, 0.4, self.seat, self.axis)


def fasteners():
    out = []
    for sx in (-1, 1):
        for z in P.EIA_Z:
            out.append(Fastener("rack front x%+.0f z%.2f" % (sx * P.SCREW_X, z),
                                (sx * P.SCREW_X, -P.EAR_T, z), (0, 1, 0),
                                washer=True))
            out.append(Fastener("rack rear  x%+.0f z%.2f" % (sx * P.SCREW_X, z),
                                (sx * P.SCREW_X, P.RACK_D + P.EAR_T, z),
                                (0, -1, 0), washer=True))
    for sx in (-1, 1):
        for z, tag in ((P.BAR_SCREW_Z, "faceplate hi"),
                       (P.BOT_SCREW_Z, "faceplate lo")):
            out.append(Fastener(
                "%s x%+.0f" % (tag, sx * P.BAR_SCREW_X),
                (sx * P.BAR_SCREW_X, -P.EAR_T + P.BAR_CB_D, z), (0, 1, 0),
                nut_at=P.EAR_T - P.BAR_CB_D + P.BAR_NUT_Y0, sunk=P.BAR_CB_D))
    # The sides and the rear legs take no screw: the leg is a runner the
    # side slides into. See RUN_* in params.
    return out


def main():
    keys = os.environ.get("UCG_DEVICE", "").split(",")
    todo = [d for d in devices.ALL if not keys[0] or d.key in keys]
    for dev in todo:
        doc = App.newDocument("check_" + dev.key)
        bodies = model.build(doc, only=dev)
        doc.recompute()
        parts = {n: b.Shape for n, b in bodies.items()}
        print("\n" + "=" * 62)
        print("== %s" % dev.name)
        print("=" * 62)
        one_device(parts, dev)


def one_device(parts, dev):
    names = ["side_l", "side_r", "leg_l", "leg_r",
             dev.part("tray_l"), dev.part("tray_r"), dev.part("faceplate")]
    asm = parts[names[0]]
    for n in names[1:]:
        asm = asm.fuse(parts[n])
    asm = asm.removeSplitter()

    print("\n[the parts against each other]")
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            v = vol(parts[a].common(parts[b]))
            check(v < VOID, "%-10s and %-10s do not overlap" % (a, b),
                  "%.3f mm3" % v)

    fs = fasteners()
    print("\n[%d fasteners, every one a real M6 x %.0f]" % (len(fs), P.SCREW_LEN))
    nuts = 0
    for f in fs:
        v = vol(asm.common(f.shank()))
        check(v < VOID, "%-26s shank is clear" % f.name, "%.3f mm3" % v)
        v = vol(asm.common(f.head()))
        check(v < VOID, "%-26s head has room" % f.name, "%.3f mm3" % v)
        b = vol(asm.common(f.bearing())) / 0.4
        check(b >= MIN_SEAT, "%-26s has %s to bear on"
              % (f.name, "washer and seat" if f.washer else "seat"),
              "%.1f mm2" % b)
        w = f.washer_solid()
        if w is not None:
            v = vol(asm.common(w))
            check(v < VOID, "%-26s washer lies flat" % f.name, "%.3f mm3" % v)
        n = f.nut()
        if n is not None:
            nuts += 1
            v = vol(asm.common(n))
            check(v < VOID, "%-26s nut seats in its pocket" % f.name,
                  "%.3f mm3" % v)
    print("\n  %d screws, %d with nuts, %d with washers"
          % (len(fs), nuts, sum(1 for f in fs if f.washer)))

    print("\n[the device]")
    case = Part.makeBox(dev.w, dev.d, dev.h,
                        Vector(-dev.w / 2, dev.y0, dev.z0))
    check(vol(asm.common(case)) < VOID, "sits in the bracket without fouling it",
          "%.3f mm3" % vol(asm.common(case)))
    for f in fs:
        n = f.nut()
        bits = f.shank().fuse(f.head())
        if n is not None:
            bits = bits.fuse(n)
        w = f.washer_solid()
        if w is not None:
            bits = bits.fuse(w)
        v = vol(case.common(bits))
        if v > VOID:
            check(False, "%-26s clears the gateway" % f.name, "%.1f mm3" % v)
    check(True, "no fastener touches the gateway",
          "checked all %d" % len(fs))

    print("\n%d checks, %d failed" % (_n, len(_fails)))
    for f in _fails:
        print("  FAIL %s" % f)
    sys.stdout.flush()
    if _fails:
        sys.exit(1)


main()
