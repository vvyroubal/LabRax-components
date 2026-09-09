"""The bracket, built as PartDesign bodies from sketches.

Four printed parts:

    side_l, side_r      one piece each: front ear, side rail, rear ear, the
                        shelf the device sits on, and the rear stop
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
    s = sk.sketch(doc, bd, name + "_Sk_ledge",
                  sk.plane(Vector(sx * P.LEDGE_X0, 0, 0), sk.Y, sk.Z))
    sk.rect(s, P.DEV_Y0, 0.0, P.DEV_Y1, P.LEDGE_T)
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


def build(doc):
    """Every part, as its own Body. Returns {name: body}."""
    return {
        "side_l": side(doc, -1, "side_l"),
        "side_r": side(doc, +1, "side_r"),
        "top_bar_l": top_bar(doc, -1, "top_bar_l"),
        "top_bar_r": top_bar(doc, +1, "top_bar_r"),
    }
