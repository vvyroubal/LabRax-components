"""The bracket, built as PartDesign bodies from sketches.

Seven printed parts:

    side_l, side_r      front ear, side rail, the ledge the tray lands on,
                        the rear stop, and the tongue the leg rides on
    leg_l, leg_r        the rear legs, which reach the back posts and carry
                        the rear ears. Each is a runner: the side slides into
                        it from the front, so the rack's depth sets itself
    tray_l, tray_r      the floor the device stands on, lapped on the
                        centreline
    faceplate           the front, in one piece, with a window for the
                        gateway's display

The bracket bolts to all four rack posts. Every rack screw is an M6 driven
from outside the rack inwards into the hex nut the post already holds, so the
ears only carry clearance slots.

It goes together in two stages. The legs are bolted to the rear posts, from
behind. The sides, the faceplate, the tray and the device are put together on
the bench -- four M6 through the ears into nuts slid into the ends of the
faceplate -- and that goes into the rack from the front as one piece, each
side's tongue running into its leg's groove, until the ears meet the posts.
No screw in the bracket has to be reached from inside the rack.
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


def _tongue(doc, bd, name, sx, y0, y1):
    """The dovetail a rear leg rides on, along the inner face of a rail.

    Narrow where it leaves the rail and wider at its tip, with both flanks at
    45 degrees: the leg's groove cannot lift off it, drop off it or pull away
    from it, and can only slide along it.
    """
    x, d, zc = P.POCKET_HW, P.RUN_D, P.RUN_Z
    r, t = P.RUN_ROOT / 2.0, P.RUN_TIP / 2.0
    s = sk.sketch(doc, bd, name + "_Sk_runner",
                  sk.plane(Vector(0, y0, 0), sk.X, sk.Z))
    # Rooted half a millimetre inside the rail, so the two are one solid
    # rather than two that happen to share a face.
    sk.polygon(s, [(sx * (x + 0.5), zc - r), (sx * x, zc - r),
                   (sx * (x - d), zc - t), (sx * (x - d), zc + t),
                   (sx * x, zc + r), (sx * (x + 0.5), zc + r)])
    return sk.pad(doc, bd, s, y1 - y0, reversed_=True)


def _runner(doc, bd, name, sx, y0, y1, y_end):
    """The grooved length of a rear leg: plate, block, and the groove in it.

    The plate stands RUN_FIT off the rail's inner face and the groove is the
    tongue's outline grown by the same amount, so every face has that much
    room. Its first few millimetres are opened out further, and the plate's
    outer face cut back with them, so a tongue arriving a little high, low or
    wide is steered in rather than stopped.
    """
    inward = sx > 0
    fit, zc = P.RUN_FIT, P.RUN_Z
    xo = P.POCKET_HW - fit                 # the leg's outer face
    h = P.RUN_TIP / 2.0 + P.RUN_JAW        # the block's half-height

    s = sk.sketch(doc, bd, name + "_Sk_plate",
                  sk.plane(Vector(sx * xo, 0, 0), sk.Y, sk.Z))
    sk.rect(s, y0, 0.0, y1, P.RAIL_TOP)
    sk.pad(doc, bd, s, P.LEG_T, reversed_=inward)

    s = sk.sketch(doc, bd, name + "_Sk_block",
                  sk.plane(Vector(sx * xo, 0, 0), sk.Y, sk.Z))
    sk.rect(s, y0, zc - h, y1, zc + h)
    sk.pad(doc, bd, s, P.RUN_D + P.RUN_BACK, reversed_=inward)

    def half(x, grow):
        # The tongue's flank, moved RUN_FIT along its own normal.
        return (P.RUN_ROOT / 2.0 + fit * 2 ** 0.5 + (P.POCKET_HW - x) + grow)

    xe = xo + 0.5                          # past the face, into the air

    g = P.RUN_MOUTH_FIT
    xr, xf = xo - g, xo - P.RUN_D - g
    s = sk.sketch(doc, bd, name + "_Sk_mouth",
                  sk.plane(Vector(0, y0, 0), sk.X, sk.Z))
    sk.polygon(s, [(sx * xe, -1.0), (sx * xe, P.RAIL_TOP + 1.0),
                   (sx * xr, P.RAIL_TOP + 1.0), (sx * xr, zc + half(xr, g)),
                   (sx * xf, zc + half(xf, g)), (sx * xf, zc - half(xf, g)),
                   (sx * xr, zc - half(xr, g)), (sx * xr, -1.0)])
    # Rearward, and said so: see the note on directions in faceplate().
    sk.pocket(doc, bd, s, P.RUN_MOUTH, reversed_=False)

    xf = xo - P.RUN_D
    s = sk.sketch(doc, bd, name + "_Sk_groove",
                  sk.plane(Vector(0, y0, 0), sk.X, sk.Z))
    sk.polygon(s, [(sx * xe, zc - half(xe, 0.0)), (sx * xf, zc - half(xf, 0.0)),
                   (sx * xf, zc + half(xf, 0.0)), (sx * xe, zc + half(xe, 0.0))])
    return sk.pocket(doc, bd, s, y_end - y0, reversed_=False)


def _catch(doc, bd, name, sx):
    """The end stop's sprung finger, at the foot of a rear leg.

    A slit frees a strip along the bottom of the plate, rooted at its rear
    end. The tooth on its tip stands into the rail's notch: ramped where the
    rail arrives, square where it leaves. The tab on the other face is what a
    fingertip finds from the back of the rack.
    """
    xo = P.POCKET_HW - P.RUN_FIT           # the leg's outer face
    xi = xo - P.LEG_T                      # and its inner one
    y0, y1 = P.CATCH_Y0, P.CATCH_Y0 + P.CATCH_L
    s = sk.sketch(doc, bd, name + "_Sk_catch_slit",
                  sk.plane(Vector(sx * xo, 0, 0), sk.Y, sk.Z))
    # One cut: a gap in front of the tip, and the slit over the finger.
    sk.polygon(s, [(y0 - 1.0, -1.0), (y0, -1.0), (y0, P.CATCH_Z),
                   (y1, P.CATCH_Z), (y1, P.CATCH_Z + P.CATCH_SLIT),
                   (y0 - 1.0, P.CATCH_Z + P.CATCH_SLIT)])
    sk.pocket(doc, bd, s, P.LEG_T)

    s = sk.sketch(doc, bd, name + "_Sk_catch_tooth",
                  sk.plane(Vector(0, 0, 0), sk.X, sk.Y))
    t = P.CATCH_TOOTH
    # Each rooted a little inside the finger, so they are one solid with it.
    sk.polygon(s, [(sx * (xo - 0.3), y0),
                   (sx * (xo + t), y0 + P.CATCH_RAMP),
                   (sx * (xo + t), P.CATCH_Y),
                   (sx * (xo - 0.3), P.CATCH_Y)])
    sk.rect(s, sx * (xi - P.CATCH_TAB), y0, sx * (xi + 0.3), y0 + 4.0)
    return sk.pad(doc, bd, s, P.CATCH_TOOTH_Z)


def side(doc, sx, name):
    """One side of the bracket, front ear through to rear ear."""
    bd = sk.body(doc, name)
    out = sx < 0

    # --- the rail that spans front to back -------------------------------
    s = sk.sketch(doc, bd, name + "_Sk_rail",
                  sk.plane(Vector(sx * P.POCKET_HW, 0, 0), sk.Y, sk.Z))
    sk.rect(s, 0.0, 0.0, P.RAIL_Y1, P.RAIL_TOP)
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

    # --- the runner the rear leg rides on ---------------------------------
    # From the back of the rear stop almost to the end of the rail. No bolt
    # is in this joint: the leg is fixed to the rear posts and this slides
    # into it, which is what lets the front be built on the bench.
    _tongue(doc, bd, name, sx, P.RUN_Y0, P.RUN_Y1)

    # --- what gets taken away --------------------------------------------
    # The rack screws: three slots per ear, on the EIA pitch. Slotted because
    # a printed rack's posts do not land on the nominal pitch every time.
    s = sk.sketch(doc, bd, name + "_Sk_slots",
                  sk.plane(Vector(0, 0, 0), sk.X, sk.Z))
    for z in P.EIA_Z:
        sk.slot(s, sx * P.SCREW_X, z, P.SLOT_W, P.SLOT_H)
    sk.pocket(doc, bd, s, P.EAR_T)

    # The notch the leg's catch runs in, along the rail's bottom edge. Its
    # rear end is the end stop: draw the frame out and that is what meets the
    # tooth. Behind it the rail is full height again, and rides over the tooth
    # on the way in.
    s = sk.sketch(doc, bd, name + "_Sk_notch",
                  sk.plane(Vector(sx * P.POCKET_HW, 0, 0), sk.Y, sk.Z))
    sk.rect(s, P.NOTCH_Y0, -1.0, P.NOTCH_Y1, P.NOTCH_Z)
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

    It goes into the rack FIRST, bolted to the rear posts from behind. Its
    forward end is a grooved runner, and the side's tongue slides into that
    from the front. Nothing in this part depends on RACK_D being exactly
    right: a deeper or shallower rack just changes how far the tongue runs in.
    """
    bd = sk.body(doc, name)

    _runner(doc, bd, name, sx, P.LEG_Y0, P.RACK_D, P.RUN_END)
    _catch(doc, bd, name, sx)

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

    It stops just short of the rails' inner faces rather than spanning the
    full opening, so the sides need no notch cut in them -- one cut full
    height would have separated each ear from its rail.

    Its four nuts go in from its ENDS, into slots closed front and back, so
    they stay put while it is offered up to the sides.
    """
    bd = sk.body(doc, name)
    front = dev.front

    s = sk.sketch(doc, bd, name + "_Sk_plate",
                  sk.plane(Vector(0, 0, 0), sk.X, sk.Z))
    sk.rect(s, -P.PLATE_HW, 0.0, P.PLATE_HW, P.RACK_U)
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
    sk.rect(s, -P.PLATE_HW, dev.flange_z0, P.PLATE_HW, P.RACK_U)
    sk.pad(doc, bd, s, P.BAR_FLANGE_D, reversed_=True)

    # Four M6, at the same places the two bars used, so the ears do not
    # change. The clearance hole goes right through, so a screw's tip can
    # never bottom out behind its nut.
    s = sk.sketch(doc, bd, name + "_Sk_screws",
                  sk.plane(Vector(0, 0, 0), sk.X, sk.Z))
    for sx in (-1, 1):
        for z in (P.BAR_SCREW_Z, P.BOT_SCREW_Z):
            sk.circle(s, sx * P.BAR_SCREW_X, z, P.M6_CLEAR)
    sk.pocket(doc, bd, s, P.BAR_T)

    # The nut slots, cut in from each end of the plate: as tall as the nut is
    # across its flats, so it cannot turn, and as deep as it is thick. Each
    # runs from the end face to just past the screw, and is closed in front
    # and behind.
    hh = (P.M6_HEX_AF + P.NUT_SLOT_FIT) / 2.0
    x_in = P.BAR_SCREW_X - P.M6_HEX_AF / 3 ** 0.5 - P.NUT_SLOT_FIT
    s = sk.sketch(doc, bd, name + "_Sk_nuts",
                  sk.plane(Vector(0, P.BAR_NUT_Y0 - P.NUT_SLOT_FIT / 2.0, 0),
                           sk.X, sk.Z))
    for sx in (-1, 1):
        for z in (P.BAR_SCREW_Z, P.BOT_SCREW_Z):
            sk.rect(s, sx * x_in, z - hh, sx * (P.PLATE_HW + 0.5), z + hh)
    # Rearward, and said so. On an X-Z plane a pocket's reversed_ is -Y, and
    # there is plate both sides of this one, so left to be worked out it would
    # cut forward through the front face instead.
    last = sk.pocket(doc, bd, s, P.M6_HEX_D + P.NUT_SLOT_FIT, reversed_=False)

    if not front.fillet:
        return bd

    # Round the opening's front edge, so it reads as a bezel rather than a
    # hole punched in a plate. Found geometrically: the four edges that lie on
    # the front face within the opening's own extent -- two lines and two arcs
    # for a window, four lines for a frame, four either way.
    #
    # Applied to the LAST feature, not to the pocket that cut the opening. A
    # PartDesign dressup replaces the chain from its base onwards, so basing
    # it on the window pocket drops everything after it: the flange, the screw
    # holes and the nut pockets all disappear, and the body comes out 8 mm
    # deep instead of 20 with nothing to bolt it on by.
    m = 0.2
    w = front.w(dev) if callable(front.w) else front.w
    h = front.h(dev) if callable(front.h) else front.h
    z = front.z(dev)
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
    # Every vertical face that meets another part stands off it: the outer
    # edge from the rail, the step from the ledge's edge, and each half from
    # the other at both ends of the lap. The faces the load goes through --
    # rim on ledge, lap on lap -- still touch.
    step = P.TRAY_STEP_X
    lap_l = lap - P.LAP_FIT      # where the left half's tongue ends
    lap_r = -lap + P.LAP_FIT     # where the right half's top lap starts

    if sx < 0:
        # outer edge laps ON TOP of the ledge; centre tongue runs underneath
        pts = [(-P.TRAY_X1, P.LAP_T), (-step, P.LAP_T),
               (-step, 0.0), (lap_l, 0.0), (lap_l, P.LAP_T),
               (-lap, P.LAP_T), (-lap, P.TRAY_T), (-P.TRAY_X1, P.TRAY_T)]
    else:
        pts = [(lap_r, P.LAP_T), (lap, P.LAP_T), (lap, 0.0),
               (step, 0.0), (step, P.LAP_T),
               (P.TRAY_X1, P.LAP_T), (P.TRAY_X1, P.TRAY_T), (lap_r, P.TRAY_T)]
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
        sk.rect(s, sx * step, P.LAP_T, sx * P.TRAY_X1, P.TRAY_T)
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
        # Out to the case's pocket, but never past the tray's own edge: a
        # case that fills the bay would otherwise put its plinth on the rail.
        out = min(dev.hw, P.TRAY_X1)
        x0, x1 = ((-out, -lap) if sx < 0 else (lap_r, out))
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
        pts = [(lap_r, P.LAP_T), (lap, P.LAP_T), (lap, 0.0),
               (lip_x, 0.0), (lip_x, top), (lap_r, top)]
    s = sk.sketch(doc, bd, name + "_Sk_rearlip",
                  sk.plane(Vector(0, rear, 0), sk.X, sk.Z))
    sk.polygon(s, pts)
    sk.pad(doc, bd, s, P.REAR_LIP_T, reversed_=True)

    return bd


def coupons(doc):
    """Two short lengths of the runner, to try the fit before the real thing.

    A side is a two-hour print and a pair of legs another two, and whether a
    sliding dovetail runs freely, binds or rattles depends on the printer far
    more than on RUN_FIT. These are 25 mm of rail with its tongue and 25 mm of
    leg with its groove, made by the same two functions that make the real
    ones. Print them standing as exported, slide one into the other, and
    change RUN_FIT if they disagree with it.
    """
    n = 25.0
    a = sk.body(doc, "coupon_tongue")
    s = sk.sketch(doc, a, "coupon_tongue_Sk_rail",
                  sk.plane(Vector(P.POCKET_HW, 0, 0), sk.Y, sk.Z))
    sk.rect(s, 0.0, 0.0, n, P.RAIL_TOP)
    sk.pad(doc, a, s, P.RAIL_T)
    _tongue(doc, a, "coupon_tongue", 1, 0.0, n)

    b = sk.body(doc, "coupon_groove")
    _runner(doc, b, "coupon_groove", 1, 0.0, n, n)
    return {"coupon_tongue": a, "coupon_groove": b}


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
