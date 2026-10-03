"""Every dimension for the UCG-Fiber / Lab Rax bracket, with its provenance.

Coordinate system used throughout the model (millimetres):

    X   rack width, 0 = rack centreline, +X = right when facing the rack
    Y   depth,      0 = front face of the FRONT posts, +Y = into the rack
    Z   height,     0 = bottom edge of the 1U the bracket occupies

Numbers tagged [rack] were measured off the Lab Rax rack models themselves,
[dev] comes from Ubiquiti's published specification, and [design] is a choice
made here. See docs/measurements.md for how the [rack] figures were obtained.

The bracket bolts to all four posts. Every screw into the rack is an M6 driven
from OUTSIDE the rack inwards, into the hex nut pocket the post already has.
"""

# ---------------------------------------------------------------- rack -----
RACK_U = 44.45  # [rack] one rack unit
FACE_W = 254.0  # [rack] faceplate width, 10" nominal
FACE_HW = FACE_W / 2

SCREW_DX = 236.525  # [rack] distance between the two screw columns
SCREW_X = SCREW_DX / 2

# EIA-310 hole heights within one U, from the bottom of the U.
EIA_Z = (6.35, 22.225, 38.1)  # [rack]

# The post already carries the nut. From its outer face: a 7.60 clearance hole
# 2 mm deep, then a hexagon 10.09 across flats / 11.65 across corners, 5 mm
# deep, holding an M6 nut. So the bracket's ears only need a clearance slot.
POST_SCREW_D = 7.6   # [rack]
POST_NUT_AF = 10.09  # [rack]

SLOT_W = 11.0  # [design] horizontal slot -> +/-2.3 mm of adjustment
SLOT_H = 6.6   # [design] M6 clearance across the slot

POST_CLEAR_W = 222.25  # [rack] clear width between the posts
POST_CLEAR_HW = POST_CLEAR_W / 2

# The rack's depth, and the number this design got wrong twice.
#
# The first build read the side panel's 175.9 mm as the CLEAR gap between the
# posts. It is not: the panel is 3 mm thick and seats about 2.95 mm into a
# groove at each end. The gap it spans is the frame beams' 170.0 mm -- three
# separate members in the rack's own 3MF are 170.0 long (objects 11, 24, 79),
# and 170.0 + 2 x 2.95 is the panel's 175.9 exactly.
#
# So the clear gap is 170.0, not 175.9, and the bracket built on the old
# reading came out about 16 mm too long -- far enough that winding the splice
# all the way in still left the rear ears standing proud of the rear posts.
#
# The post's cross-section is 30 x 35 and the mesh does not say which way it
# faces, so the outer depth is either 230.0 or 240.0. Rather than pick one,
# the nominal sits between them and the splice -- now slotted at BOTH ends --
# reaches either comfortably. Set it by fitting, not by this number.
RACK_INNER = 170.0              # [rack] clear between the posts, from the beams
POST_D = 32.5                   # [rack] cross-section is 30 x 35 and the
                                # mesh does not say which way; take the midpoint
RACK_D = RACK_INNER + 2 * POST_D  # [rack] 235.0, front face to rear face

# A side with an ear at each end would be about 248 mm long, and a 180 mm bed
# takes about 212 even cornerwise, so each side is two pieces: a front section
# carrying everything that touches the device, and a rear leg that reaches the
# back posts.
#
# They used to be bolted together through slots, two M6 a side driven in from
# OUTSIDE the rail. That joint could only ever be made inside the rack -- the
# side goes in from the front and the leg from the rear, each stopped by its
# own ear -- and in there its screw heads faced the rack's side wall, 0.9 mm
# from the post line, where no driver reaches. The leg's boss also sat hard
# against the side's rear stop, so the "adjustment" only ever went one way.
#
# So there is no fastener here now. The side carries a dovetail tongue along
# the inner face of its rail and the leg a groove to match. The leg is bolted
# to the rear posts first, from behind, where there is room to work; the side
# then slides into it from the front like a drawer onto a runner. The rack's
# depth is taken up by how far it slides, not by the number above.
RAIL_Y1 = 206.0       # [design] rear end of the side's rail
RUN_Z = 20.0          # [design] height of the runner's centreline
RUN_D = 4.0           # [design] how far the tongue stands off the rail
RUN_ROOT = 10.0       # [design] its height at the rail. The flanks are at
                      # 45 degrees, so neither part needs support for them
RUN_TIP = RUN_ROOT + 2 * RUN_D   # 18.0, its height at the tip
RUN_FIT = 0.25        # [design] clearance on every face of the groove. Print
                      # the two coupons in common/stl before the sides and
                      # legs to find out whether your printer agrees
RUN_BACK = 3.2        # [design] what the leg keeps behind the groove
RUN_JAW = 5.0         # [design] and above and below it, past the tongue's tip
LEG_T = 3.2           # [design] the leg's plate, same as the rail
LEG_Y0 = 152.0        # [design] front of the leg, 8 mm behind the rear stop
RUN_MOUTH = 6.0       # [design] the groove opens out over its first 6 mm...
RUN_MOUTH_FIT = 1.0   # [design] ...by this much, so the tongue finds its way
RUN_MIN = 30.0        # [design] the least engagement worth calling a joint

# --------------------------------------------------------------- device ----
# UniFi Cloud Gateway Fiber. Fanless: vents underneath and on both sides.
DEV_W = 212.8  # [dev]
DEV_D = 127.6  # [dev]
DEV_H = 30.0   # [dev]
DEV_MASS_G = 734  # [dev] with an SSD fitted

CLR_W = 1.2  # [design] total width clearance
CLR_H = 0.8  # [design]
CLR_D = 1.4  # [design]

# The bay the chassis offers is set by the RACK, not by the device that goes
# in it. The posts leave 222.25 between them; 0.925 mm of clearance a side
# puts the body at 110.2 half-width, and a 3.2 mm rail inside that leaves
# 107.0. The UCG-Fiber needing exactly 214.0 is a happy accident of a
# well-chosen device, not the reason for the number -- which is why a second,
# much narrower device needs no change to the sides or the legs.
RAIL_CLEAR = 0.925         # [rack] per side, between rail and post
BODY_HW = POST_CLEAR_HW - RAIL_CLEAR   # 110.2
POCKET_HW = BODY_HW - 3.2  # 107.0; RAIL_T repeats this below
POCKET_W = 2 * POCKET_HW   # 214.0

# ------------------------------------------------------------ the sides ----
# One screw size for the whole bracket: M6 x 12. That is not a preference,
# it sets dimensions. The rack post's equipment hole is blind 6 mm deep -- 2 mm
# of clearance, then a 4 mm hex pocket -- so a 12 mm screw can only work if the
# ear is thin enough to let it reach the nut and thick enough to stop it
# bottoming out on the end of the hole. 6.5 mm puts the tip 0.5 mm clear with
# 3.5 mm of thread in the nut.
SCREW_LEN = 12.0   # [design] every screw in the bracket
POST_CLEAR_D = 2.0  # [rack] plain part of the post's hole
POST_NUT_D = 4.0    # [rack] its hex pocket, 2..6
POST_HOLE_D = 6.0   # [rack] and the hole is blind there
M6_HEAD_D = 11.0    # [design] counterbore for a button head

EAR_T = 6.5        # [design] front and rear ear plate thickness
EAR_X0 = 94.0      # [design] inboard edge of the ears. Far enough in
                   # that a screw head at BAR_SCREW_X bears fully on it.
RAIL_T = 3.2       # [design] side rail; 107.0 + 3.2 = 110.2 <= 111.125

TRAY_T = 6.0       # [design] the tray the device sits on
LAP_T = TRAY_T / 2  # [design] each half of a step lap
LEDGE_X0 = 99.0    # [design] where the side's ledge begins
DEV_Z0 = TRAY_T            # 6.0
DEV_Z1 = DEV_Z0 + DEV_H    # 36.0
POCKET_TOP = DEV_Z1 + CLR_H  # 36.8
RAIL_TOP = 40.3    # [design]

DEV_Y0 = 8.0                    # [design] front face, against the top bar
DEV_Y1 = DEV_Y0 + DEV_D + CLR_D  # 137.0

STOP_T = 7.0       # [design] rear stop thickness
STOP_X0 = 99.0     # [design]

# The chassis's own idea of how far back it will carry a tray, and where its
# rear stop sits. These happen to be the UCG-Fiber's numbers -- the sides were
# drawn around it -- but the side does not read the device any more. A device
# shorter than this simply leaves the stop unused behind it and is caught by
# its own tray's lip instead, which is what lets one pair of sides serve both.
# The faceplate stands between the back of the ears and the front of the
# ledge. Drawn 8.0 into an 8.0 gap it had to be forced, so the ledge starts a
# little further back than the plate ends.
LEDGE_Y0 = DEV_Y0 + 0.3   # [design] 8.3, the front of the ledge
LEDGE_Y1 = 137.0   # [design] the deepest tray the chassis supports
STOP_Y = 137.0     # [design] front face of the sides' rear stop
STOP_H = 36.0      # [design] how tall it stands

# The runner's tongue starts on the back of the rear stop and stops its own
# depth short of the end of the rail. Run right to the end, its inner corner
# is the furthest point of the side when it lies cornerwise on the bed, and
# the print came within 1.75 mm of the plate's edge; held back by RUN_D the
# rail's own corner is the furthest again, as it always was. The leg's groove
# is blind, and long enough to take the tongue with the leg as far forward as
# the stop lets it come.
RUN_Y0 = STOP_Y + STOP_T                       # 144.0
RUN_Y1 = RAIL_Y1 - RUN_D                       # 202.0
RUN_END = RUN_Y1 + (LEG_Y0 - RUN_Y0) + 4.0     # 214.0

# Ventilation in the side rails -- the device vents through its sides.
RAIL_VENT_Z0 = 10.0
RAIL_VENT_Z1 = 30.0
RAIL_VENTS_Y = ((24.0, 52.0), (60.0, 88.0), (96.0, 124.0))  # [design]

# ------------------------------------------------------------- the tray ----
# The device stands on a tray, not on the two ledges alone. At 214 mm it will
# not fit a 180 mm bed in any orientation, so it comes in halves that lap on
# the centreline. Each half laps the other way onto its side's ledge, and the
# device's own weight closes both laps.
#
# It is a light load over a wide plate -- 734 g on a 214 x 129 x 6 span works
# out around 0.2 mm of deflection -- so the tray does not need stiffening; it
# needs to be held together and located, which is what the joints below do.
# Every face of the tray used to be drawn touching what it meets: 214.0 mm of
# tray in a 214.0 mm bay, its step on the ledge's edge, the two halves on each
# other. None of that overlaps, so every check passed, and none of it goes
# together once it is printed. These are the gaps.
TRAY_SIDE_FIT = 0.2   # [design] per side, to the rail and to the ledge's edge
LAP_FIT = 0.3         # [design] between the two halves, at each end of the lap
TRAY_X1 = POCKET_HW - TRAY_SIDE_FIT   # 106.8, just short of the side rail
TRAY_STEP_X = LEDGE_X0 - TRAY_SIDE_FIT  # 98.8, where the full thickness ends
# The tray drops into the gap between the ledge's front nib and the rear stop.
# Modelled flush it is exactly as long as that gap, which in printed plastic
# is an interference fit, so it is made this much shorter.
TRAY_FIT = 0.6        # [design]
# 60 mm of overlap, and no fastener anywhere in this joint.
#
# There was one: a tab behind the device carrying two M6. Both tabs snapped
# off the moment the bolts were tightened. The tab hung off a 10 x 3 mm neck
# with the bolt 6.5 mm above it and up to 22 mm behind, so nearly all of the
# preload arrived as bending. CalculiX puts the tabs at 26 N and 33 N against
# roughly 1700 N from an M6 at 2 N-m -- fifty times over. That is not a part
# that was over-tightened; 26 N is about 0.03 N-m at the key.
#
# A bigger tab is not the answer either: nothing that clamps two 6 mm printed
# plates edge-on survives an M6. The joint does not need one. The lap is 60 mm
# wide and runs the whole depth; the rails hold the halves sideways; the
# faceplate and the rear stop hold them fore and aft; and the gateway's weight
# sits on the lap and closes it. Four pegs keep them square to each other.
#
# Removing it also clears the space behind the gateway's rear ports, which is
# exactly where that tab stood -- 1 mm behind the face, across the middle 20 mm.
CENTRE_LAP = 30.0     # [design] half-width of the centre lap

KEY_D = 5.0           # [design] peg diameter
KEY_FIT = 0.5         # [design] clearance in its socket, on the diameter
KEY_X = 22.0          # [design] near the edges of the lap, so a pair holds the
                      # halves square as well as together
KEY_Y = (20.0, 116.0)  # [design] one pair just inside the gateway's front edge,
                       # one pair near its back

# The lip across the back of the tray. Without it the only thing behind the
# gateway is the two rear stops on the sides, and those reach in only to
# x = +/-99 -- 7.4 mm of overlap at each end, 7% of a 212.8 mm rear face. Push
# a plug into a socket in the middle and the case slides back on 93% of its
# width with nothing behind it.
#
# It is deliberately LOW. The ports are on this face, so the lip clears the
# tray by 3 mm and no more: it catches the bottom edge of the case, below the
# port openings, and everything above DEV_Z0 + REAR_LIP_H is left open -- which
# `verify` checks. If your unit has anything in the bottom 3 mm of its back,
# drop REAR_LIP_H; 1 mm still stops it.
#
# 3 mm is not thin for the job. The load is a plug being pushed home, order
# 30 N spread over the lip's 198 mm; even taken as a point load on 20 mm of
# lip that is about 3 MPa against PETG's ~50. This is nothing like the bolt
# tab that broke -- that one carried 1700 N of preload on a 3 mm neck.
REAR_LIP_H = 3.0      # [design] how far it stands above the tray
REAR_LIP_T = 3.0      # [design] thickness, fore and aft
# A tray for a device narrower than the bay has to locate it sideways, which
# the sides' own rails do for a device that fills the bay. Walls on the tray,
# and a plinth under the device where one is wanted to centre it in the U.
TRAY_WALL_T = 4.0     # [design] wall thickness
TRAY_WALL_H = 8.0     # [design] how far it rises above the case's underside

# A tray under a device that breathes through its underside has to be opened
# up, or the tray is a lid on the intake. Slots run fore-and-aft through the
# full-thickness part of each half; the centre lap is left solid, because
# holing it would mean holing both halves at once where they overlap.
VENT_W = 8.0        # [design] slot width
VENT_RIB = 5.0      # [design] material between slots
VENT_MARGIN = 6.0   # [design] solid border kept round the vented panel

REAR_LIP_X = STOP_X0 - LAP_FIT  # [design] it stops just short of where the
                      # sides' rear stops start, so the two together span the
                      # rear face without the lip being wedged between them

# ---------------------------------------------------------- the top bar ----
# Bolted on last, from the front, through the ear and into a hex nut trapped
# in the bar with the pocket facing rear. It nests into a notch in the side so
# the ear and the rail still meet below it.
BAR_T = 8.0         # [design] thickness, front to back
# The plate is a little narrower than the bay it stands in. At the full 214.0
# it was a press fit between two rails that nothing else spaces.
PLATE_FIT = 0.2     # [design] per end
PLATE_HW = POCKET_HW - PLATE_FIT   # 106.8
# The nuts are slid in from the ENDS of the plate, into slots that are closed
# front and back. They used to be fed in from behind, into pockets open to the
# rear: nothing held them, and the upper pair had to be worked 12 mm under the
# flange with a fingertip. In a slot a nut cannot fall out of the back, and
# once the plate is between the rails it cannot come out of the end either.
BAR_NUT_Y0 = 1.5    # [design] where the nut's near face sits. A 12 mm screw
                    # ends at 6.5, flush with the far face of the nut
NUT_SLOT_FIT = 0.3  # [design] room for the nut in its slot, across and through
BAR_CB_D = 1.0      # [design] the bar screws' heads sink this far into the
                    # ear. It is the millimetre that lets a 12 mm screw reach
                    # the nut without moving the nut -- which matters, because
                    # moving it would make every top bar already printed wrong.
BAR_X1 = BODY_HW    # [design] outboard end. The bar passes between the posts
                    # like the rails do, so it gets the same 0.925 mm.
BAR_Z0 = 36.8       # [design] underside over the device
BAR_END_X0 = 96.0   # [design] the taller end block starts here
BAR_END_Z0 = 23.7   # [design] deep enough for an M6 nut across its flats
BAR_FLANGE_D = 12.0  # [design] how far it reaches back over the device.
                     # Every millimetre here costs 0.7 mm of bed diagonal.

BAR_FLANGE_Z0 = BAR_Z0      # flush with the bar's underside

BAR_SCREW_X = 100.0   # [design] inboard of the rack slots. Its nut is
                      # 5.77 from the centre to a corner, and the faceplate
                      # ends at POCKET_HW, so this cannot go further out.
BAR_SCREW_Z = 30.16   # [design] midway between two EIA holes

# The bar above the device and the bar below it are one part: a faceplate
# across the whole opening, with a window for the gateway's display. It takes
# the same four screws the two bars did, at the same four places, so the ears
# are unchanged.
BOT_SCREW_Z = RACK_U - BAR_SCREW_Z  # 14.29, the lower pair

# The window, and where it sits.
#
# Its height is not calculated from the display any more. Two calliper
# readings off the case were tried -- 14.0 to the centre, then 19.0 -- and
# both put the window wrong. The position is now given directly, against a
# feature of the faceplate itself rather than of the gateway:
#
#   THE OVAL'S TOP EDGE SITS EXACTLY 6.0 mm BELOW THE UNDERSIDE OF THE TOP
#   BAR -- the flange that reaches back over the gateway, whose underside is
#   BAR_FLANGE_Z0 = 36.8.
#
# That is a rule about the printed part, so it can be checked on the built
# solid and is not at the mercy of a measurement. It was 5.0 on the faceplate
# before this one; the oval moves DOWN 1 mm by the gap opening to 6.0.
WIN_TOP_GAP = 6.0      # [design] specified: oval top to the top bar's underside
WIN_W = 22.5           # [dev] the display is 21.0 wide, plus the float
WIN_H = 11.0           # [dev] the display is 10.0 tall, plus a little
WIN_Z = BAR_FLANGE_Z0 - WIN_TOP_GAP - WIN_H / 2.0  # 25.3

# The display itself: a 21.0 x 10.0 stadium, centred on the case's width. It
# is the only thing on the front face -- no reset button, and the power jack
# is at the back with the ports. Its height is taken from the window now,
# because the window's height is the thing that was specified; the checks on
# it are therefore about size and concentricity, not about position.
DISP_W = 21.0          # [dev] measured
DISP_H = 10.0          # [dev] measured
DISP_Z = WIN_Z
WIN_FILLET = 6.0       # [design] the window's front edge is rounded over, so
                       # the opening reads as a bezel rather than a hole
                       # punched in a plate. Added by hand in FreeCAD and
                       # brought back into the script from there.

# The ears' outer corners are cut back, so the front reads as a shape rather
# than as four square slabs.
EAR_CHAMFER = 4.0     # [design]

BAR_SCREW_X = 100.0   # [design] inboard of the rack slots. Its nut is
                      # 5.77 from the centre to a corner, and the faceplate
                      # ends at POCKET_HW, so this cannot go further out.
BAR_SCREW_Z = 30.16   # [design] midway between two EIA holes

# The bottom bar mirrors the top one about the middle of the U, so the device
# sits in an even border: 7.65 mm of bracket above it and 7.65 below. Both sit
# 8 mm behind the ears' front faces -- a consistent reveal all the way round,
# rather than the top bar being recessed and nothing being below it.
BOT_BAR_Z1 = RACK_U - BAR_Z0        # 7.65, what you see below the device
BOT_END_Z1 = RACK_U - BAR_END_Z0    # 20.75, the taller ends that hold a nut
BOT_SCREW_Z = RACK_U - BAR_SCREW_Z  # 14.29

# The ears' outer corners are cut back, so the front reads as a shape rather
# than as four square slabs.
EAR_CHAMFER = 4.0     # [design]


# The bar is one piece. At 220.4 x 20 mm it will not fit a 180 mm bed square
# on, but turned 45 degrees its bounding box is 170 mm and it does -- and the
# face that was the top of the 1U lies flat on the bed, so it needs neither
# support nor a joint. Halved and butted it was a beam pinned at each end by a
# single screw, which is a pivot; halved and lapped it needed two M3, the only
# ones left in the design. One piece has neither problem.

# ------------------------------------------------------------ fasteners ----
M6_CLEAR = 6.4      # [rack]
M6_HEX_AF = 10.09   # [rack] 11.65 across corners
M6_HEX_D = 5.0      # [rack] nut thickness
