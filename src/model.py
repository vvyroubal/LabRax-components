"""The bracket, built as PartDesign bodies from sketches.

Seven printed parts:

    side_l, side_r      front ear, side rail, the ledge the tray lands on,
                        and the rear stop
    leg_l, leg_r        the rear legs, which reach the back posts and carry
                        the rear ears. Spliced to the sides through slots, so
                        the rack's depth is set by sliding them
    tray_l, tray_r      the floor the device stands on, lapped on the
                        centreline
    faceplate           the front, in one piece, with a window for the
                        gateway's display

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
import devices


def _ear_outline(sx):
    """A rack ear, with its two outer corners cut back."""
    c = P.EAR_CHAMFER
    return [(sx * P.EAR_X0, 0.0),
            (sx * (P.FACE_HW - c), 0.0),
            (sx * P.FACE_HW, c),
            (sx * P.FACE_HW, P.RACK_U - c),
            (sx * (P.FACE_HW - c), P.RACK_U),
            (sx * P.EAR_X0, P.RACK_U)]


def side(doc, sx, name):
    """One side of the bracket, front ear through to rear ear."""
    bd = sk.body(doc, name)
    out = sx < 0

    # --- the rail that spans front to back -------------------------------
    s = sk.sketch(doc, bd, name + "_Sk_rail",
                  sk.plane(Vector(sx * P.POCKET_HW, 0, 0), sk.Y, sk.Z))
    sk.rect(s, 0.0, 0.0, P.SPLICE_Y1, P.RAIL_TOP)
    sk.pad(doc, bd, s, P.RAIL_T, reversed_=out)

    # --- the two ears ----------------------------------------------------
    s = sk.sketch(doc, bd, name + "_Sk_ear_front",
                  sk.plane(Vector(0, 0, 0), sk.X, sk.Z))
    sk.polygon(s, _ear_outline(sx))
    sk.pad(doc, bd, s, P.EAR_T)

    # --- the shelf the device rests on, and the stop behind it -----------
    # The shelf the tray laps onto. It starts where the bottom bar ends: that
    # bar is what stops the tray sliding forward now, so the ledge needs no
    # nib of its own.
    s = sk.sketch(doc, bd, name + "_Sk_ledge",
                  sk.plane(Vector(sx * P.LEDGE_X0, 0, 0), sk.Y, sk.Z))
    sk.rect(s, P.LEDGE_Y0, 0.0, P.LEDGE_Y1, P.LAP_T)
    sk.pad(doc, bd, s, P.BODY_HW - P.LEDGE_X0, reversed_=out)

    s = sk.sketch(doc, bd, name + "_Sk_stop",
                  sk.plane(Vector(0, P.STOP_Y, 0), sk.X, sk.Z))
    sk.rect(s, sx * P.STOP_X0, 0.0, sx * P.BODY_HW, P.STOP_H)
    sk.pad(doc, bd, s, P.STOP_T, reversed_=True)

    # --- what gets taken away --------------------------------------------
    # The rack screws: three slots per ear, on the EIA pitch. Slotted because
    # a printed rack's posts do not land on the nominal pitch every time.
    s = sk.sketch(doc, bd, name + "_Sk_slots",
                  sk.plane(Vector(0, 0, 0), sk.X, sk.Z))
    for z in P.EIA_Z:
        sk.slot(s, sx * P.SCREW_X, z, P.SLOT_W, P.SLOT_H)
    sk.pocket(doc, bd, s, P.EAR_T)

    # Slots for the rear leg, so the depth is set by sliding it. The rack's
    # own numbers disagree by about 6 mm -- the side panel says 245.9 outer,
    # the depth members say 240 -- and this covers both.
    s = sk.sketch(doc, bd, name + "_Sk_splice",
                  sk.plane(Vector(sx * P.POCKET_HW, 0, 0), sk.Y, sk.Z))
    for y in P.SPLICE_BOLT_Y:
        sk.slot(s, y, P.SPLICE_BOLT_Z, P.SPLICE_SLOT, P.M6_CLEAR)
    sk.pocket(doc, bd, s, P.RAIL_T)

    # Clearance for the two screws that hold the bars on, one high, one low,
    # each with its head sunk a millimetre so a 12 mm screw reaches its nut.
    s = sk.sketch(doc, bd, name + "_Sk_barscrews",
                  sk.plane(Vector(0, 0, 0), sk.X, sk.Z))
    for z in (P.BAR_SCREW_Z, P.BOT_SCREW_Z):
        sk.circle(s, sx * P.BAR_SCREW_X, z, P.M6_CLEAR)
    sk.pocket(doc, bd, s, P.EAR_T)

    s = sk.sketch(doc, bd, name + "_Sk_barheads",
                  sk.plane(Vector(0, -P.EAR_T, 0), sk.X, sk.Z))
    for z in (P.BAR_SCREW_Z, P.BOT_SCREW_Z):
        sk.circle(s, sx * P.BAR_SCREW_X, z, P.M6_HEAD_D)
    sk.pocket(doc, bd, s, P.BAR_CB_D)

    # The notch the top bar's end sits in. Cut only behind the ear, so the
    # ear and the rail still meet under it.
    # Sketched on the bar's rear face and cut forward, so it takes the rail
    # and never the ear -- the two directions both have material to remove,
    # so this one cannot be left to the automatic choice.
    # No notch for the faceplate: it stops at the rail's inner face, so the
    # ear and the rail still meet over their whole height. Cutting one full
    # height, as the two bars needed, would have severed them.
    # The device vents through its sides, so the rails are windowed.
    s = sk.sketch(doc, bd, name + "_Sk_vents",
                  sk.plane(Vector(sx * P.POCKET_HW, 0, 0), sk.Y, sk.Z))
    for y0, y1 in P.RAIL_VENTS_Y:
        sk.rect(s, y0, P.RAIL_VENT_Z0, y1, P.RAIL_VENT_Z1)
    sk.pocket(doc, bd, s, P.RAIL_T)
    return bd


def leg(doc, sx, name):
    """A rear leg: the tie from the side back to the rear posts.

    It carries no device weight -- the tray lands on the sides' ledges, well
    forward of here -- so this is a tie, not a beam. What it does is stop the
    bracket hanging off the front posts alone.

    It laps on the inner face of the side's rail and bolts through the slots
    there, which is where the rack's depth is finally set: nothing in this
    part depends on RACK_D being exactly right.
    """
    bd = sk.body(doc, name)
    inward = sx > 0

    s = sk.sketch(doc, bd, name + "_Sk_plate",
                  sk.plane(Vector(sx * P.POCKET_HW, 0, 0), sk.Y, sk.Z))
    sk.rect(s, P.SPLICE_Y0, 0.0, P.RACK_D, P.RAIL_TOP)
    sk.pad(doc, bd, s, P.SPLICE_T, reversed_=inward)

    # The rear ear, on the far side of the rear posts: the screws go into
    # them from outside the rack, like every other one.
    s = sk.sketch(doc, bd, name + "_Sk_ear",
                  sk.plane(Vector(0, P.RACK_D, 0), sk.X, sk.Z))
    sk.polygon(s, _ear_outline(sx))
    sk.pad(doc, bd, s, P.EAR_T, reversed_=True)

    s = sk.sketch(doc, bd, name + "_Sk_slots",
                  sk.plane(Vector(0, P.RACK_D + P.EAR_T, 0), sk.X, sk.Z))
    for z in P.EIA_Z:
        sk.slot(s, sx * P.SCREW_X, z, P.SLOT_W, P.SLOT_H)
    sk.pocket(doc, bd, s, P.EAR_T)

    # A boss at each splice bolt, thick enough to trap an M6 nut. They sit
    # behind the device, where there is nothing to foul.
    x_in = sx * (P.POCKET_HW - P.SPLICE_BOSS_T)
    s = sk.sketch(doc, bd, name + "_Sk_bosses",
                  sk.plane(Vector(sx * P.POCKET_HW, 0, 0), sk.Y, sk.Z))
    for y in P.SPLICE_BOLT_Y:
        sk.rect(s, y - P.SPLICE_SLOT / 2 - 4.0, P.SPLICE_BOLT_Z - P.SPLICE_BOSS_H / 2,
                y + P.SPLICE_SLOT / 2 + 4.0, P.SPLICE_BOLT_Z + P.SPLICE_BOSS_H / 2)
    sk.pad(doc, bd, s, P.SPLICE_BOSS_T, reversed_=inward)

    # Slotted, like the side's half of the joint. The side alone gave +/-9.7,
    # which was not enough once the rack turned out to be shallower than the
    # side panel implied; slotting this end too doubles the travel and costs
    # only a leg reprint, the side being the part that takes four hours.
    s = sk.sketch(doc, bd, name + "_Sk_boltholes",
                  sk.plane(Vector(x_in, 0, 0), sk.Y, sk.Z))
    for y in P.SPLICE_BOLT_Y:
        sk.slot(s, y, P.SPLICE_BOLT_Z, P.LEG_SLOT, P.M6_CLEAR)
    sk.pocket(doc, bd, s, P.SPLICE_BOSS_T)

    # The nut pocket is stretched with it, so the nut travels the length of
    # the slot. Its two flats parallel to Y stay captured, so it still cannot
    # turn while the bolt is done up.
    s = sk.sketch(doc, bd, name + "_Sk_nuts",
                  sk.plane(Vector(x_in, 0, 0), sk.Y, sk.Z))
    for y in P.SPLICE_BOLT_Y:
        sk.hexslot(s, y, P.SPLICE_BOLT_Z, P.M6_HEX_AF, P.LEG_NUT_SLOT)
    sk.pocket(doc, bd, s, P.M6_HEX_D, reversed_=inward)
    return bd


def faceplate(doc, dev, name):
    """The front of the bracket for one device: one plate across the opening.

    It replaces the bar above the device and the bar below it. Being one piece
    it has no joint to open, it stops the device across its whole face rather
    than at four corner blocks, and it stops the tray sliding forward.

    What the opening in it is depends on the device. A gateway with a display
    facing front gets a Window: a small oval placed by a rule against the top
    bar. A switch with its ports facing front gets a Frame: a large opening
    onto the ports whose border overlaps the case, so the case can be reached
    but cannot come out. Either way the plate itself is identical.

    It stops at the rails' inner faces rather than spanning the full opening,
    so the sides need no notch cut in them -- one cut full height would have
    separated each ear from its rail.
    """
    bd = sk.body(doc, name)
    front = dev.front

    s = sk.sketch(doc, bd, name + "_Sk_plate",
                  sk.plane(Vector(0, 0, 0), sk.X, sk.Z))
    sk.rect(s, -P.POCKET_HW, 0.0, P.POCKET_HW, P.RACK_U)
    sk.pad(doc, bd, s, P.BAR_T, reversed_=True)

    s = sk.sketch(doc, bd, name + "_Sk_window",
                  sk.plane(Vector(0, 0, 0), sk.X, sk.Z))
    if front.kind == "window":
        sk.slot(s, 0.0, front.z(dev), front.w, front.h)
    else:
        w, h, z = front.w(dev), front.h(dev), front.z(dev)
        sk.rect(s, -w / 2.0, z - h / 2.0, w / 2.0, z + h / 2.0)
    sk.pocket(doc, bd, s, P.BAR_T)

    # The flange over the top of the device, so it cannot lift. It sits on the
    # device, so a short device brings it down with it.
    s = sk.sketch(doc, bd, name + "_Sk_flange",
                  sk.plane(Vector(0, P.BAR_T, 0), sk.X, sk.Z))
    sk.rect(s, -P.POCKET_HW, dev.flange_z0, P.POCKET_HW, P.RACK_U)
    sk.pad(doc, bd, s, P.BAR_FLANGE_D, reversed_=True)

    # Four M6, at the same places the two bars used, so the ears do not
    # change: clearance from the front, then the nut, its pocket facing rear.
    s = sk.sketch(doc, bd, name + "_Sk_screws",
                  sk.plane(Vector(0, 0, 0), sk.X, sk.Z))
    for sx in (-1, 1):
        for z in (P.BAR_SCREW_Z, P.BOT_SCREW_Z):
            sk.circle(s, sx * P.BAR_SCREW_X, z, P.M6_CLEAR)
    sk.pocket(doc, bd, s, P.BAR_NUT_Y0)

    s = sk.sketch(doc, bd, name + "_Sk_nuts",
                  sk.plane(Vector(0, P.BAR_NUT_Y0 + P.M6_HEX_D, 0), sk.X, sk.Z))
    for sx in (-1, 1):
        for z in (P.BAR_SCREW_Z, P.BOT_SCREW_Z):
            sk.hexagon(s, sx * P.BAR_SCREW_X, z, P.M6_HEX_AF)
    # Explicit: there is plate both sides of this plane, so the automatic
    # choice would cut the pocket behind the nut instead of around it.
    last = sk.pocket(doc, bd, s, P.M6_HEX_D, reversed_=True)

    # The flange follows the device's height, so a short device pulls it down
    # into the path a nut must travel to reach its pocket -- on the Flex Mini
    # it sat 1.58 mm into that path and the upper nuts could not be fitted at
    # all. Cut it back where that happens. At x = +/-100 the flange is
    # outboard of every device carried so far, so the relief costs nothing.
    nut_top = P.BAR_SCREW_Z + P.M6_HEX_AF / 2.0
    if dev.flange_z0 < nut_top + P.NUT_FEED_CLEAR:
        hw = P.M6_HEX_AF / 3 ** 0.5 + 0.5      # across corners, plus room
        s = sk.sketch(doc, bd, name + "_Sk_nutrelief",
                      sk.plane(Vector(0, P.BAR_T, 0), sk.X, sk.Z))
        for sx in (-1, 1):
            sk.rect(s, sx * P.BAR_SCREW_X - hw, dev.flange_z0,
                    sx * P.BAR_SCREW_X + hw, nut_top + P.NUT_FEED_CLEAR)
        # Rearward, into the flange. On an X-Z plane a pocket's reversed_ is
        # -Y -- the nut pockets above rely on that -- so this one is False,
        # and it has to be stated: there is material both sides of this plane,
        # so letting the direction be worked out would notch the front plate
        # above the nut instead and leave the flange where it was.
        sk.pocket(doc, bd, s, P.BAR_FLANGE_D, reversed_=False)

    if not front.fillet:
        return bd

    # Round the window's front edge, so the opening reads as a bezel rather
    # than a hole punched in a plate. Found geometrically: the four edges that
    # lie on the front face within the window's own extent.
    m = 0.2
    w, h, z = front.w, front.h, front.z(dev)
    edges = sk.edges_on(last.Shape,
                        (-w / 2 - m, w / 2 + m),
                        (-m, m),
                        (z - h / 2 - m, z + h / 2 + m))
    if len(edges) != 4:
        raise RuntimeError("expected 4 window edges to round, found %d: %s"
                           % (len(edges), edges))
    sk.fillet(doc, bd, last, edges, front.fillet, name + "_Fillet_window")
    return bd


def tray(doc, dev, sx, name):
    """Half of the tray that carries one device.

    The two halves are not mirrors: at the centreline one has to pass under
    the other. The left half takes the bottom of the lap, the right half the
    top, which is the only rule needed to read the section below -- and it is
    also why the right half carries the pegs and the left half the sockets.

    This is the part that knows what device it is for. The plate and the lap
    are the same whatever goes on top; the rear lip moves to the back of that
    device, and a device narrower or shorter than the bay gets a plinth to
    lift it and walls to hold it straight.
    """
    bd = sk.body(doc, name)
    lap = P.CENTRE_LAP
    rear = dev.y1 - P.TRAY_FIT

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
                  sk.plane(Vector(0, dev.y0, 0), sk.X, sk.Z))
    sk.polygon(s, pts)
    sk.pad(doc, bd, s, rear - dev.y0, reversed_=True)

    # --- the strip that reaches the rear stop -----------------------------
    # The tray is located fore and aft by the faceplate in front and the
    # sides' rear stops behind, and what reaches them is the strip riding the
    # ledge, not the plate under the device. A tray shorter than the bay has
    # to carry that strip back to the stop or it walks: the Flex Mini's had
    # 38 mm of slack, the TL-SG108E's 27 and the NUC's 12. The gateway fills
    # the bay already, so it grows nothing.
    back = P.LEDGE_Y1 - P.TRAY_FIT
    if rear < back - 1e-9:
        s = sk.sketch(doc, bd, name + "_Sk_rails",
                      sk.plane(Vector(0, rear, 0), sk.X, sk.Z))
        sk.rect(s, sx * P.LEDGE_X0, P.LAP_T, sx * P.TRAY_X1, P.TRAY_T)
        sk.pad(doc, bd, s, back - rear, reversed_=True)

    # Four pegs key the two halves to each other. There is no bolt: the one
    # that used to be here hung off a 10 x 3 mm neck and snapped off both
    # halves the first time it was tightened. The lap does the work -- 60 mm
    # wide, the full depth, closed by the device's weight -- and the pegs
    # stop the halves shifting or going out of square.
    s = sk.sketch(doc, bd, name + "_Sk_keys",
                  sk.plane(Vector(0, 0, P.LAP_T), sk.X, sk.Y))
    for kx in (-P.KEY_X, P.KEY_X):
        for ky in dev.keys_y:
            sk.circle(s, kx, ky,
                      P.KEY_D if sx > 0 else P.KEY_D + P.KEY_FIT)
    if sx > 0:
        # Down to Z=0, so each peg stands on the bed when this half is
        # printed and fills its socket to full depth when it is assembled.
        sk.pad(doc, bd, s, P.LAP_T, reversed_=True)
    else:
        sk.pocket(doc, bd, s, P.LAP_T)

    # --- the plinth, where the device has to be lifted --------------------
    # A short device sitting on the tray floor leaves a band of blank plate
    # above it, which matters when its front face is the one you look at.
    # The plinth raises it until it is centred in the U.
    if dev.plinth > 0.0:
        x0, x1 = ((-dev.hw, -lap) if sx < 0 else (-lap, dev.hw))
        s = sk.sketch(doc, bd, name + "_Sk_plinth",
                      sk.plane(Vector(0, 0, P.TRAY_T), sk.X, sk.Y))
        sk.rect(s, x0, dev.y0, x1, rear)
        # Upward: on an XY sketch plane, reversed_ is -Z (the pegs use that).
        sk.pad(doc, bd, s, dev.plinth)

    # --- walls, where the device is narrower than the bay -----------------
    # A device that fills the bay is held straight by the sides' own rails.
    # One that does not would wander, so its tray holds it instead.
    if dev.walls:
        t = P.TRAY_WALL_T
        x0, x1 = ((-dev.hw - t, -dev.hw) if sx < 0 else (dev.hw, dev.hw + t))
        s = sk.sketch(doc, bd, name + "_Sk_wall",
                      sk.plane(Vector(0, 0, P.TRAY_T), sk.X, sk.Y))
        sk.rect(s, x0, dev.y0, x1, rear)
        sk.pad(doc, bd, s, dev.plinth + P.TRAY_WALL_H)

    # --- ventilation, for a device that breathes through its underside ----
    # Slots run fore and aft through the full-thickness part of this half --
    # outboard of the lap, inboard of the ledge. The lap itself is left solid:
    # a hole there would have to pass through both halves where they overlap,
    # and the lap is the joint that holds the tray together.
    if dev.vent:
        lo, hi = lap + P.VENT_MARGIN, P.LEDGE_X0 - P.VENT_MARGIN
        y0, y1 = dev.y0 + P.VENT_MARGIN, rear - P.VENT_MARGIN
        pitch = P.VENT_W + P.VENT_RIB
        n = int((hi - lo + P.VENT_RIB) // pitch)
        if n > 0:
            run = n * pitch - P.VENT_RIB
            x = lo + (hi - lo - run) / 2.0
            s = sk.sketch(doc, bd, name + "_Sk_vents",
                          sk.plane(Vector(0, 0, 0), sk.X, sk.Y))
            for i in range(n):
                a0 = x + i * pitch
                if sx < 0:
                    sk.rect(s, -a0 - P.VENT_W, y0, -a0, y1)
                else:
                    sk.rect(s, a0, y0, a0 + P.VENT_W, y1)
            # Up through the plate and any plinth on top of it: a slot that
            # stops under the plinth is not a vent, it is a pocket. The
            # direction is left to be worked out -- there is material on one
            # side of z=0 only, so there is nothing to get wrong.
            sk.pocket(doc, bd, s, P.TRAY_T + dev.plinth)

    # --- the lip across the back ------------------------------------------
    # Raised off the tray's own rear face and padded backwards, so it lands
    # just behind the device and catches the bottom of its back panel. The
    # two halves carry it between them. It rises from the device's underside,
    # not the tray's, so a plinth carries it up too.
    top = dev.z0 + P.REAR_LIP_H
    lip_x = (dev.hw + P.TRAY_WALL_T) if dev.walls else P.REAR_LIP_X
    if sx < 0:
        pts = [(-lip_x, 0.0), (-lap, 0.0), (-lap, top), (-lip_x, top)]
    else:
        # Steps down at the edge of the lap, where this half is only the top
        # 3 mm of the tray -- there is no material below it to stand on.
        pts = [(-lap, P.LAP_T), (lap, P.LAP_T), (lap, 0.0),
               (lip_x, 0.0), (lip_x, top), (-lap, top)]
    s = sk.sketch(doc, bd, name + "_Sk_rearlip",
                  sk.plane(Vector(0, rear, 0), sk.X, sk.Z))
    sk.polygon(s, pts)
    sk.pad(doc, bd, s, P.REAR_LIP_T, reversed_=True)

    return bd


def build(doc, only=None):
    """Every part, as its own Body. Returns {name: body}.

    Four of them are the chassis and are shared: they are sized by the rack
    and never read a device. The rest come in threes, one set per device.

    `only` restricts it to one device's set plus the chassis. The checkers use
    that to work on one device at a time: a document holding every part of
    every device is a lot of solid to fuse and intersect, and doing it twice
    over in one process is what made the checks fall over.
    """
    out = {
        "side_l": side(doc, -1, "side_l"),
        "side_r": side(doc, +1, "side_r"),
        "leg_l": leg(doc, -1, "leg_l"),
        "leg_r": leg(doc, +1, "leg_r"),
    }
    for dev in (devices.ALL if only is None else (only,)):
        out[dev.part("tray_l")] = tray(doc, dev, -1, dev.part("tray_l"))
        out[dev.part("tray_r")] = tray(doc, dev, +1, dev.part("tray_r"))
        out[dev.part("faceplate")] = faceplate(doc, dev,
                                                 dev.part("faceplate"))
    return out
