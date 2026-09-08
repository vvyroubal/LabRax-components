"""Solid geometry for the UCG-Fiber Lab Rax bracket.

The bracket is modelled once, as a single 1U solid spanning the full 254 mm,
and then divided into printable parts by intersecting it with region solids.
Splitting a finished solid -- rather than modelling each part separately --
means the mating faces cannot drift apart when a dimension changes.

Parts:
    tray      centre section: vented floor + the faceplate below the window
    top_bar   the faceplate above the window, bridging the two ears
    ear_l     left end bracket: rack ear, side rail, top lip, floor
    ear_r     mirror of ear_l
    stop_l    small rear stop that closes the device in from behind
    stop_r    mirror of stop_l
"""

import math

import FreeCAD as App
import Part
from FreeCAD import Vector

import params as P

BIG = 400.0  # comfortably larger than the part, for region solids


def box(x0, x1, y0, y1, z0, z1):
    """An axis-aligned box from two opposite corners, given in any order."""
    x0, x1 = sorted((x0, x1))
    y0, y1 = sorted((y0, y1))
    z0, z1 = sorted((z0, z1))
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, Vector(x0, y0, z0))


def slot(xc, zc, w, h, y0, y1):
    """A horizontal slot with semicircular ends, cut along +Y."""
    r = h / 2.0
    span = w - h
    s = box(xc - span / 2, xc + span / 2, y0, y1, zc - r, zc + r)
    for x in (xc - span / 2, xc + span / 2):
        s = s.fuse(Part.makeCylinder(r, y1 - y0, Vector(x, y0, zc), Vector(0, 1, 0)))
    return s


def hole(xc, zc, d, y0, y1):
    """A round hole bored along +Y."""
    return Part.makeCylinder(d / 2.0, y1 - y0, Vector(xc, y0, zc), Vector(0, 1, 0))


def vhole(xc, yc, d, z0, z1):
    """A round hole bored along +Z."""
    return Part.makeCylinder(d / 2.0, z1 - z0, Vector(xc, yc, z0), Vector(0, 0, 1))


def hex_trap(xc, zc, af, y0, y1, slot_to=None):
    """A hexagonal nut pocket bored along +Y, flats top and bottom.

    `af` is across the flats, so the pocket stands `af` tall and af*2/sqrt(3)
    wide -- 10.09 and 11.65 for M6, which is what Lab Rax uses. `slot_to` adds
    a slot of the same width out to that Z, so the nut can be dropped in from
    the nearest outside face rather than being sealed in.
    """
    r = af / math.sqrt(3.0)  # circumradius; across corners is 2r
    pts = [Vector(xc + r * math.cos(math.radians(a)), y0,
                  zc + r * math.sin(math.radians(a)))
           for a in (0, 60, 120, 180, 240, 300)]
    prism = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(
        Vector(0.0, y1 - y0, 0.0))
    if slot_to is not None:
        prism = prism.fuse(box(xc - af / 2, xc + af / 2, y0, y1, zc, slot_to))
    return prism


def vhex_trap(xc, yc, af, z0, z1, slot_to=None):
    """The same pocket bored along +Z, for a bolt that runs vertically."""
    r = af / math.sqrt(3.0)
    pts = [Vector(xc + r * math.cos(math.radians(a)),
                  yc + r * math.sin(math.radians(a)), z0)
           for a in (0, 60, 120, 180, 240, 300)]
    prism = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(
        Vector(0.0, 0.0, z1 - z0))
    if slot_to is not None:
        prism = prism.fuse(box(xc - af / 2, xc + af / 2, yc, slot_to, z0, z1))
    return prism


# --------------------------------------------------------------------------
#  The bracket as one solid
# --------------------------------------------------------------------------

def _faceplate():
    """Full-width 1U plate, pierced by the device window and the M6 slots.

    The window is smaller than the device on every side. The device is loaded
    from the rear and lands against those lips, so nothing extra is needed to
    stop it at the front.
    """
    fp = box(-P.FACE_HW, P.FACE_HW, -P.FACE_T, 0.0, 0.0, P.RACK_U)
    fp = fp.cut(box(-P.WIN_HW, P.WIN_HW, -P.FACE_T - 1, 1.0, P.WIN_Z0, P.WIN_Z1))
    for sx in (-1, 1):
        for z in P.EIA_Z:
            fp = fp.cut(slot(sx * P.SCREW_X, z, P.SLOT_W, P.SLOT_H,
                             -P.FACE_T - 1, 1.0))
    return fp


def _floor():
    """Floor under the device, slotted to clear its underside vents."""
    fl = box(-P.BODY_HW, P.BODY_HW, 0.0, P.BODY_D, 0.0, P.FLOOR_T)
    n = int(P.VENT_MAX_X / P.VENT_PITCH)
    for i in range(-n, n + 1):
        xc = i * P.VENT_PITCH
        fl = fl.cut(box(xc - P.VENT_W / 2, xc + P.VENT_W / 2,
                        P.VENT_Y0, P.VENT_Y1, -1.0, P.FLOOR_T + 1))
    return fl


def _rails():
    """Side rails that locate the device sideways.

    No top lip: the device is lowered in between them, so anything reaching
    over it would have to be fitted afterwards. They are windowed because the
    device vents through its sides.
    """
    out = None
    for sx in (-1, 1):
        x0, x1 = sx * P.POCKET_HW, sx * P.BODY_HW
        rail = box(x0, x1, 0.0, P.BODY_D, 0.0, P.RAIL_TOP)
        lo, hi = sorted((x0, x1))
        for y0, y1 in P.RAIL_VENTS_Y:
            rail = rail.cut(box(lo - 1, hi + 1, y0, y1,
                                P.RAIL_VENT_Z0, P.RAIL_VENT_Z1))
        out = rail if out is None else out.fuse(rail)
    return out


def _top_flange():
    """A shelf behind the top of the faceplate, above the device.

    This is the only place behind the faceplate with room for a deep pilot
    hole, so the top bar's joint screws land here. It starts at the top of the
    device pocket, not at the top of the window -- the window edge is 2 mm
    lower, and a flange that deep would foul the device.
    """
    return box(-P.LAP_X, P.LAP_X, 0.0, P.BOSS_D, P.POCKET_TOP, P.RACK_U)


def _stop_pads():
    """Local floor thickening behind the device, for the rear stop screws."""
    out = None
    for sx in (-1, 1):
        x0, x1 = sx * P.STOP_X0, sx * P.POCKET_HW
        pad = box(x0, x1, P.STOP_Y0, P.BODY_D, 0.0, P.FLOOR_T)
        out = pad if out is None else out.fuse(pad)
    return out


def _rear_blocks():
    """Blocks behind the device where the ear and tray bolt together with M6.

    A trapped M6 nut wants about 13 mm of material around it and the faceplate
    rails are 8.0 and 10.45 mm tall, so this is the only part of the bracket
    that can host one: behind the device the whole 1U is free. Kept to 15 mm
    tall so cables leaving the rear ports pass over the top.
    """
    out = None
    for sx in (-1, 1):
        blk = box(sx * P.REAR_X0, sx * P.LAP_X, P.REAR_Y0, P.REAR_Y1,
                  0.0, P.REAR_Z1)
        out = blk if out is None else out.fuse(blk)
    return out


def bracket_solid():
    """The whole bracket, before it is divided into printable parts."""
    s = _faceplate()
    for piece in (_floor(), _rails(), _top_flange(), _stop_pads(),
                  _rear_blocks()):
        s = s.fuse(piece)
    return s.removeSplitter()


# --------------------------------------------------------------------------
#  Dividing it up
# --------------------------------------------------------------------------

def _top_region():
    """Everything the top bar owns: the faceplate above the window, plus the
    flange behind it."""
    r = box(-P.SPLIT_X, P.SPLIT_X, -BIG, BIG, P.WIN_Z1, BIG)
    for x0, x1 in ((P.SPLIT_X, P.LAP_X), (-P.LAP_X, -P.SPLIT_X)):
        r = r.fuse(box(x0, x1, -P.FACE_T / 2, P.BOSS_D, P.WIN_Z1, BIG))
    return r


def _tray_region():
    """Everything the tray owns.

    Past the split it keeps the rear half of the faceplate and the full
    thickness of the floor. The rear joint blocks are then handed back: the
    tray takes the front half of each, the ear the back half, so a bolt driven
    from behind pulls the two together.
    """
    r = box(-P.SPLIT_X, P.SPLIT_X, -BIG, BIG, -BIG, P.WIN_Z1)
    for x0, x1 in ((P.SPLIT_X, P.LAP_X), (-P.LAP_X, -P.SPLIT_X)):
        r = r.fuse(box(x0, x1, -P.FACE_T / 2, BIG, -BIG, P.WIN_Z1))
    for sx in (-1, 1):
        r = r.cut(box(sx * P.REAR_X0, sx * P.LAP_X, P.REAR_Y_MID, BIG,
                      -BIG, BIG))
    return r


# --------------------------------------------------------------------------
#  Fasteners
#
#  Both joints follow the Lab Rax pattern: a clearance hole, then a hexagonal
#  pocket holding a nut. The faceplate ones are M3 because a trapped M6 needs
#  about 13 mm of material and the rails are 8.0 and 10.45 mm tall; the joints
#  behind the device, where the whole 1U is free, are M6.
# --------------------------------------------------------------------------

def _face_axes():
    return [(sx * x, z) for sx in (-1, 1)
            for x in P.JOINT_SCREW_X for z in P.JOINT_SCREW_Z]


def _face_bolt_side():
    """Counterbore and clearance through the ear's half of the lap."""
    cuts = []
    for x, z in _face_axes():
        cuts.append(hole(x, z, P.M3_CB_D, -P.FACE_T - 0.1,
                         -P.FACE_T + P.M3_CB_Y))
        cuts.append(hole(x, z, P.M3_CLEAR, -P.FACE_T - 0.1, -P.FACE_T / 2 + 0.1))
    return cuts


def _face_nut_side():
    """Nut pocket and thread relief in the tray's or top bar's half."""
    cuts = []
    for x, z in _face_axes():
        # The nut drops in from whichever outside face of the 1U is nearer.
        slot_to = 0.0 if z < P.WIN_Z1 else P.RACK_U
        cuts.append(hex_trap(x, z, P.M3_HEX_AF, -P.FACE_T / 2,
                             -P.FACE_T / 2 + P.M3_HEX_D, slot_to=slot_to))
        cuts.append(hole(x, z, P.M3_CLEAR, -P.FACE_T / 2, P.BOSS_D))
    return cuts


def _rear_axes():
    return [(sx * x, P.REAR_BOLT_Z) for sx in (-1, 1) for x in P.REAR_BOLT_X]


def _rear_bolt_side():
    """M6 counterbore and clearance through the ear's block, from the back."""
    cuts = []
    for x, z in _rear_axes():
        cuts.append(hole(x, z, P.M6_CB_D, P.REAR_Y1 - P.M6_CB_Y,
                         P.REAR_Y1 + 0.1))
        cuts.append(hole(x, z, P.M6_CLEAR, P.REAR_Y_MID - 0.1, P.REAR_Y1 + 0.1))
    return cuts


def _rear_nut_side():
    """M6 nut pocket in the tray's block, open at the top so it can be fed in."""
    cuts = []
    for x, z in _rear_axes():
        cuts.append(hex_trap(x, z, P.M6_HEX_AF, P.REAR_Y_MID - P.M6_HEX_D,
                             P.REAR_Y_MID, slot_to=P.REAR_Z1))
        cuts.append(hole(x, z, P.M6_CLEAR, P.REAR_Y0 - 0.1,
                         P.REAR_Y_MID - P.M6_HEX_D))
    return cuts


def _stop_nut_side():
    """M3 nut pocket in the underside of the floor, under each rear stop."""
    cuts = []
    for sx in (-1, 1):
        xc = sx * (P.STOP_X0 + P.POCKET_HW) / 2.0
        for y in P.STOP_SCREW_Y:
            cuts.append(vhex_trap(xc, y, P.M3_HEX_AF, -0.1, P.M3_HEX_D))
            cuts.append(vhole(xc, y, P.M3_CLEAR, P.M3_HEX_D, P.FLOOR_T + 0.1))
    return cuts


def build_parts():
    """Return {name: Part.Shape} for every printable part."""
    full = bracket_solid()
    tray_r = _tray_region()
    top_r = _top_region()

    tray = full.common(tray_r)
    for c in _face_nut_side() + _rear_nut_side() + _stop_nut_side():
        tray = tray.cut(c)

    top_bar = full.common(top_r)
    for c in _face_nut_side():
        top_bar = top_bar.cut(c)

    ears = full.cut(tray_r).cut(top_r)
    for c in _face_bolt_side() + _rear_bolt_side() + _stop_nut_side():
        ears = ears.cut(c)

    parts = {"tray": tray.removeSplitter(),
             "top_bar": top_bar.removeSplitter()}
    for name, sx in (("ear_l", -1), ("ear_r", 1)):
        parts[name] = ears.common(box(0.0, sx * BIG, -BIG, BIG,
                                      -BIG, BIG)).removeSplitter()
    for name, sx in (("stop_l", -1), ("stop_r", 1)):
        parts[name] = _rear_stop(sx).removeSplitter()
    return parts


def _rear_stop(sx):
    """L-shaped block that closes the rear of the pocket.

    It sits against the inner face of a side rail, overlapping the device's
    rear corner -- far enough outboard that it cannot foul a connector
    whichever way round the device is fitted. Bolted down into a nut trapped
    in the underside of the floor.
    """
    x0, x1 = sx * P.STOP_X0, sx * P.POCKET_HW
    up = box(x0, x1, P.STOP_Y0, P.STOP_Y0 + P.STOP_T, P.FLOOR_T, P.STOP_Z1)
    # Reaches forward over the device's rear top corner to hold it down.
    up = up.fuse(box(x0, x1, P.STOP_Y0 - P.HOLD_D, P.STOP_Y0,
                     P.POCKET_TOP, P.STOP_Z1))
    foot_y0 = P.STOP_Y0 + P.STOP_T
    foot_top = P.FLOOR_T + P.STOP_FOOT_T
    foot = box(x0, x1, foot_y0, P.BODY_D, P.FLOOR_T, foot_top)
    s = up.fuse(foot)
    xc = sx * (P.STOP_X0 + P.POCKET_HW) / 2.0
    for y in P.STOP_SCREW_Y:
        s = s.cut(vhole(xc, y, P.M3_CLEAR, P.FLOOR_T - 0.1, foot_top + 0.1))
        s = s.cut(vhole(xc, y, P.M3_CB_D, foot_top - P.M3_CB_Y, foot_top + 0.1))
    return s
