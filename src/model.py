"""The bracket, built as PartDesign bodies from sketches.

Six printed parts:

    side_l, side_r      one piece each: front ear, side rail, rear ear, the
                        ledge the tray lands on, and the rear stop
    tray_l, tray_r      the floor the device stands on, lapped on the
                        centreline
    top_bar_l, top_bar_r  the front panel's top bar, in halves

The bracket bolts to all four rack posts. Every rack screw is an M6 driven
from outside the rack inwards into the hex nut the post already holds, so the
ears only carry clearance slots. The top bar is bolted on last, from the
front, through the ear and into a nut trapped in the bar with its pocket
facing rear; the bar nests into a notch in the side so that the ear and the
rail still meet below it.
"""

import FreeCAD as App
from FreeCAD import Vector

import params as P
import sk


def side(doc, sx, name):
    """One side of the bracket, front ear through to rear ear."""
    bd = sk.body(doc, name)
    out = sx < 0

    # --- the rail that spans front to back -------------------------------
    s = sk.sketch(doc, bd, name + "_Sk_rail",
                  sk.plane(Vector(sx * P.POCKET_HW, 0, 0), sk.Y, sk.Z))
    sk.rect(s, 0.0, 0.0, P.RACK_D, P.RAIL_TOP)
    sk.pad(doc, bd, s, P.RAIL_T, reversed_=out)

    # --- the two ears ----------------------------------------------------
    s = sk.sketch(doc, bd, name + "_Sk_ear_front",
                  sk.plane(Vector(0, 0, 0), sk.X, sk.Z))
    sk.rect(s, sx * P.EAR_X0, 0.0, sx * P.FACE_HW, P.RACK_U)
    sk.pad(doc, bd, s, P.EAR_T)

    s = sk.sketch(doc, bd, name + "_Sk_ear_rear",
                  sk.plane(Vector(0, P.RACK_D, 0), sk.X, sk.Z))
    sk.rect(s, sx * P.EAR_X0, 0.0, sx * P.FACE_HW, P.RACK_U)
    sk.pad(doc, bd, s, P.EAR_T, reversed_=True)

    # --- the shelf the device rests on, and the stop behind it -----------
    # An L in section: a full-height nib in front of the device, then the
    # shelf the tray laps onto. The nib and the rear stop between them hold
    # the tray fore and aft, so it needs no fixing to the side.
    s = sk.sketch(doc, bd, name + "_Sk_ledge",
                  sk.plane(Vector(sx * P.LEDGE_X0, 0, 0), sk.Y, sk.Z))
    sk.polygon(s, [(0.0, 0.0), (P.DEV_Y1, 0.0), (P.DEV_Y1, P.LAP_T),
                   (P.DEV_Y0, P.LAP_T), (P.DEV_Y0, P.TRAY_T), (0.0, P.TRAY_T)])
    sk.pad(doc, bd, s, P.BODY_HW - P.LEDGE_X0, reversed_=out)

    s = sk.sketch(doc, bd, name + "_Sk_stop",
                  sk.plane(Vector(0, P.DEV_Y1, 0), sk.X, sk.Z))
    sk.rect(s, sx * P.STOP_X0, 0.0, sx * P.BODY_HW, P.DEV_Z1)
    sk.pad(doc, bd, s, P.STOP_T, reversed_=True)

    # --- what gets taken away --------------------------------------------
    # The rack screws: three slots per ear, on the EIA pitch. Slotted because
    # a printed rack's posts do not land on the nominal pitch every time.
    for tag, y in (("front", 0.0), ("rear", P.RACK_D)):
        s = sk.sketch(doc, bd, name + "_Sk_slots_" + tag,
                      sk.plane(Vector(0, y, 0), sk.X, sk.Z))
        for z in P.EIA_Z:
            sk.slot(s, sx * P.SCREW_X, z, P.SLOT_W, P.SLOT_H)
        sk.pocket(doc, bd, s, P.EAR_T)

    # Clearance for the screw that holds the top bar on.
    s = sk.sketch(doc, bd, name + "_Sk_barscrew",
                  sk.plane(Vector(0, 0, 0), sk.X, sk.Z))
    sk.circle(s, sx * P.BAR_SCREW_X, P.BAR_SCREW_Z, P.M6_CLEAR)
    sk.pocket(doc, bd, s, P.EAR_T)

    # The notch the top bar's end sits in. Cut only behind the ear, so the
    # ear and the rail still meet under it.
    # Sketched on the bar's rear face and cut forward, so it takes the rail
    # and never the ear -- the two directions both have material to remove,
    # so this one cannot be left to the automatic choice.
    s = sk.sketch(doc, bd, name + "_Sk_barnotch",
                  sk.plane(Vector(0, P.BAR_T, 0), sk.X, sk.Z))
    sk.rect(s, sx * (P.BAR_END_X0 - 2.0), P.BAR_END_Z0,
            sx * (P.BAR_X1 + 0.4), P.RACK_U)
    sk.pocket(doc, bd, s, P.BAR_T, reversed_=True)

    # The device vents through its sides, so the rails are windowed.
    s = sk.sketch(doc, bd, name + "_Sk_vents",
                  sk.plane(Vector(sx * P.POCKET_HW, 0, 0), sk.Y, sk.Z))
    for y0, y1 in P.RAIL_VENTS_Y:
        sk.rect(s, y0, P.RAIL_VENT_Z0, y1, P.RAIL_VENT_Z1)
    sk.pocket(doc, bd, s, P.RAIL_T)
    return bd


def top_bar(doc, sx, name):
    """Half of the front panel's top bar."""
    bd = sk.body(doc, name)

    s = sk.sketch(doc, bd, name + "_Sk_profile",
                  sk.plane(Vector(0, 0, 0), sk.X, sk.Z))
    sk.polygon(s, [(0.0, P.BAR_Z0),
                   (sx * P.BAR_END_X0, P.BAR_Z0),
                   (sx * P.BAR_END_X0, P.BAR_END_Z0),
                   (sx * P.BAR_X1, P.BAR_END_Z0),
                   (sx * P.BAR_X1, P.RACK_U),
                   (0.0, P.RACK_U)])
    sk.pad(doc, bd, s, P.BAR_T, reversed_=True)

    # Reaches back over the device, so it cannot lift once the bar is on.
    s = sk.sketch(doc, bd, name + "_Sk_flange",
                  sk.plane(Vector(0, P.BAR_T, 0), sk.X, sk.Z))
    sk.rect(s, 0.0, P.BAR_FLANGE_Z0, sx * P.POCKET_HW, P.RACK_U)
    sk.pad(doc, bd, s, P.BAR_FLANGE_D, reversed_=True)

    # Screw clearance from the front, then the nut, its pocket facing rear.
    s = sk.sketch(doc, bd, name + "_Sk_screw",
                  sk.plane(Vector(0, 0, 0), sk.X, sk.Z))
    sk.circle(s, sx * P.BAR_SCREW_X, P.BAR_SCREW_Z, P.M6_CLEAR)
    sk.pocket(doc, bd, s, P.BAR_T - P.M6_HEX_D)

    s = sk.sketch(doc, bd, name + "_Sk_nut",
                  sk.plane(Vector(0, P.BAR_T, 0), sk.X, sk.Z))
    sk.hexagon(s, sx * P.BAR_SCREW_X, P.BAR_SCREW_Z, P.M6_HEX_AF)
    sk.pocket(doc, bd, s, P.M6_HEX_D)
    return bd


def tray(doc, sx, name):
    """Half of the tray.

    The two halves are not mirrors: at the centreline one has to pass under
    the other. The left half takes the bottom of every lap, the right half the
    top, which is the only rule needed to read the section below -- and it is
    also why the right half carries the peg and the nuts, and the left half
    the socket and the bolt clearance.
    """
    bd = sk.body(doc, name)
    lap = P.CENTRE_LAP
    if sx < 0:
        # outer edge laps ON TOP of the ledge; centre tongue runs underneath
        pts = [(-P.TRAY_X1, P.LAP_T), (-P.LEDGE_X0, P.LAP_T),
               (-P.LEDGE_X0, 0.0), (lap, 0.0), (lap, P.LAP_T),
               (-lap, P.LAP_T), (-lap, P.TRAY_T), (-P.TRAY_X1, P.TRAY_T)]
    else:
        pts = [(-lap, P.LAP_T), (lap, P.LAP_T), (lap, 0.0),
               (P.LEDGE_X0, 0.0), (P.LEDGE_X0, P.LAP_T),
               (P.TRAY_X1, P.LAP_T), (P.TRAY_X1, P.TRAY_T), (-lap, P.TRAY_T)]
    s = sk.sketch(doc, bd, name + "_Sk_plate",
                  sk.plane(Vector(0, P.DEV_Y0, 0), sk.X, sk.Z))
    sk.polygon(s, pts)
    sk.pad(doc, bd, s, P.DEV_Y1 - P.DEV_Y0, reversed_=True)

    # Forward of the device the lap simply continues, and a peg keys the two
    # halves together. There is only 8 mm there -- an M6 nut wants 10.2 of
    # slot and 15.5 of height -- so the bolts cannot go at this end.
    s = sk.sketch(doc, bd, name + "_Sk_frontlap",
                  sk.plane(Vector(0, 0, 0), sk.X, sk.Z))
    z0, z1 = (0.0, P.LAP_T) if sx < 0 else (P.LAP_T, P.TRAY_T)
    sk.rect(s, -P.CENTRE_LAP, z0, P.CENTRE_LAP, z1)
    sk.pad(doc, bd, s, P.DEV_Y0, reversed_=True)

    # Behind it there is room to work: one tab per half, side by side, with
    # two M6 running across the joint.
    u0, u1 = (-P.TAB_HX, 0.0) if sx < 0 else (0.0, P.TAB_HX)
    s = sk.sketch(doc, bd, name + "_Sk_tab",
                  sk.plane(Vector(0, P.DEV_Y1, 0), sk.X, sk.Z))
    sk.rect(s, u0, 0.0, u1, P.TAB_Z1)
    sk.pad(doc, bd, s, P.TAB_D, reversed_=True)

    s = sk.sketch(doc, bd, name + "_Sk_boltholes",
                  sk.plane(Vector(u0, 0, 0), sk.Y, sk.Z))
    for y in P.TRAY_BOLT_Y:
        sk.circle(s, y, P.TRAY_BOLT_Z, P.M6_CLEAR)
    sk.pocket(doc, bd, s, P.TAB_HX)

    # Two pegs and the sockets they drop into. Near the edges of the lap, so
    # they hold the halves square to each other as well as together.
    s = sk.sketch(doc, bd, name + "_Sk_key",
                  sk.plane(Vector(0, 0, P.LAP_T), sk.X, sk.Y))
    for kx in (-P.KEY_X, P.KEY_X):
        sk.circle(s, kx, P.KEY_Y,
                  P.KEY_D if sx > 0 else P.KEY_D + P.KEY_FIT)
    if sx > 0:
        sk.pad(doc, bd, s, P.LAP_T - 0.6, reversed_=True)
    else:
        sk.pocket(doc, bd, s, P.LAP_T)

    if sx > 0:
        s = sk.sketch(doc, bd, name + "_Sk_nutslots",
                      sk.plane(Vector(2.0, 0, 0), sk.Y, sk.Z))
        for y in P.TRAY_BOLT_Y:
            sk.rect(s, y - P.M6_NUT_AF / 2, P.TRAY_BOLT_Z - 5.8,
                    y + P.M6_NUT_AF / 2, P.TAB_Z1 + 1.0)
        # Explicit: material lies both ways from this plane, so the
        # automatic choice would happily cut the wrong side of the bolt.
        sk.pocket(doc, bd, s, P.M6_NUT_D, reversed_=True)
    return bd


def build(doc):
    """Every part, as its own Body. Returns {name: body}."""
    return {
        "side_l": side(doc, -1, "side_l"),
        "side_r": side(doc, +1, "side_r"),
        "tray_l": tray(doc, -1, "tray_l"),
        "tray_r": tray(doc, +1, "tray_r"),
        "top_bar_l": top_bar(doc, -1, "top_bar_l"),
        "top_bar_r": top_bar(doc, +1, "top_bar_r"),
    }
