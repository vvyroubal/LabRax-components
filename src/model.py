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
    """Side rails with an inward top lip, so the device cannot lift out.

    The lip runs the full depth and the device slides in under it from the
    rear. The rails are windowed because the device vents through its sides.
    """
    out = None
    for sx in (-1, 1):
        x0, x1 = sx * P.POCKET_HW, sx * P.BODY_HW
        rail = box(x0, x1, 0.0, P.BODY_D, 0.0, P.RAIL_TOP)
        lo, hi = sorted((x0, x1))
        for y0, y1 in P.RAIL_VENTS_Y:
            rail = rail.cut(box(lo - 1, hi + 1, y0, y1,
                                P.RAIL_VENT_Z0, P.RAIL_VENT_Z1))
        lx0, lx1 = sx * P.LIP_X, sx * P.POCKET_HW
        rail = rail.fuse(box(lx0, lx1, 0.0, P.BODY_D, P.POCKET_TOP, P.RAIL_TOP))
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


def bracket_solid():
    """The whole bracket, before it is divided into printable parts."""
    s = _faceplate()
    for piece in (_floor(), _rails(), _top_flange(), _stop_pads()):
        s = s.fuse(piece)
    return s.removeSplitter()


# --------------------------------------------------------------------------
#  Dividing it up
# --------------------------------------------------------------------------

def _top_region():
    """Everything the top bar owns: the faceplate above the window, plus the
    flange behind it that the joint screws bite into."""
    r = box(-P.SPLIT_X, P.SPLIT_X, -BIG, BIG, P.WIN_Z1, BIG)
    for x0, x1 in ((P.SPLIT_X, P.LAP_X), (-P.LAP_X, -P.SPLIT_X)):
        r = r.fuse(box(x0, x1, -P.FACE_T / 2, P.BOSS_D, P.WIN_Z1, BIG))
    return r


def _tray_region():
    """Everything the tray owns: the floor and the faceplate below the window.

    Past the split it keeps the rear half of the faceplate and the full
    thickness of the floor, so a screw driven from the front has 16 mm of
    solid material to tap into.
    """
    r = box(-P.SPLIT_X, P.SPLIT_X, -BIG, BIG, -BIG, P.WIN_Z1)
    for x0, x1 in ((P.SPLIT_X, P.LAP_X), (-P.LAP_X, -P.SPLIT_X)):
        r = r.fuse(box(x0, x1, -P.FACE_T / 2, BIG, -BIG, P.WIN_Z1))
    return r


def _joint_axes():
    """(x, z) of every tray/ear and topbar/ear joint screw."""
    return [(sx * x, z)
            for sx in (-1, 1)
            for x in P.JOINT_SCREW_X
            for z in P.JOINT_SCREW_Z]


def _joint_pilots():
    """Pilot holes, in whichever part the screw taps into."""
    return [hole(x, z, P.M3_PILOT, -P.FACE_T / 2 - 0.1, P.BOSS_D + 0.1)
            for x, z in _joint_axes()]


def _joint_clearance():
    """Clearance holes and counterbores through the ears' half of the lap."""
    cuts = []
    for x, z in _joint_axes():
        cuts.append(hole(x, z, P.M3_CLEAR, -P.FACE_T - 0.1, -P.FACE_T / 2 + 0.1))
        cuts.append(hole(x, z, P.M3_CB_D, -P.FACE_T - 0.1, -P.FACE_T + P.M3_CB_Z))
    return cuts


def _stop_pilots():
    cuts = []
    for sx in (-1, 1):
        xc = sx * (P.STOP_X0 + P.POCKET_HW) / 2.0
        for y in P.STOP_SCREW_Y:
            cuts.append(vhole(xc, y, P.M3_PILOT, 0.6, P.FLOOR_T + 0.1))
    return cuts


def build_parts():
    """Return {name: Part.Shape} for every printable part."""
    full = bracket_solid()
    tray_r = _tray_region()
    top_r = _top_region()

    pilots = _joint_pilots()

    tray = full.common(tray_r)
    for c in pilots + _stop_pilots():
        tray = tray.cut(c)

    top_bar = full.common(top_r)
    for c in pilots:
        top_bar = top_bar.cut(c)

    ears = full.cut(tray_r).cut(top_r)
    for c in _joint_clearance() + _stop_pilots():
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
    rear corner by about 6 mm -- far enough outboard that it cannot foul a
    connector whichever way round the device is fitted.
    """
    x0, x1 = sx * P.STOP_X0, sx * P.POCKET_HW
    up = box(x0, x1, P.STOP_Y0, P.STOP_Y0 + P.STOP_T, P.FLOOR_T, P.STOP_Z1)
    foot_y0 = P.STOP_Y0 + P.STOP_T
    foot_top = P.FLOOR_T + P.STOP_FOOT_T
    foot = box(x0, x1, foot_y0, P.BODY_D, P.FLOOR_T, foot_top)
    s = up.fuse(foot)
    xc = sx * (P.STOP_X0 + P.POCKET_HW) / 2.0
    for y in P.STOP_SCREW_Y:
        s = s.cut(vhole(xc, y, P.M3_CLEAR, P.FLOOR_T - 0.1, foot_top + 0.1))
        s = s.cut(vhole(xc, y, P.M3_CB_D, foot_top - P.M3_CB_Z, foot_top + 0.1))
    return s
