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
POST_DEPTH = 35.0  # [rack] post cross-section front-to-back

# Front to back. The side panel is 175.9 mm and fits BETWEEN the posts, so
# that is the INNER depth -- reading it as the outer one is what made the
# first bracket 27 mm too short. Outer, front post face to rear post face:
RACK_INNER = 175.9              # [rack] side panel, between the posts
RACK_D = RACK_INNER + 2 * 35.0  # [rack] 245.9, front face to rear face

# 245.9 + two 8 mm ears is 261.9 mm, and a 180 mm bed takes 225.6 mm even
# cornerwise, so each side is two pieces: a front section carrying everything
# that touches the device, and a rear leg that reaches the back posts. They
# splice behind the device, where there is nothing in the way, and the splice
# is slotted -- so the depth is set by sliding it rather than by trusting the
# number above. That matters: the rack's own depth members are 170 mm, which
# would imply 240 rather than 245.9, and the slot covers both.
SPLICE_Y0 = 146.0     # [design] front of the overlap, behind the device
SPLICE_Y1 = 206.0     # [design] rear end of the front section
SPLICE_T = 3.2        # [design] the leg's lap plate, same as the rail
SPLICE_BOLT_Y = (161.0, 191.0)  # [design] nominal; the slots move +/-10
SPLICE_BOLT_Z = 20.0  # [design]
SPLICE_SLOT = 26.0    # [design] slot length -> +/-10 mm of adjustment
SPLICE_BOSS_T = 8.0   # [design] the leg thickens here to hold an M6 nut
SPLICE_BOSS_H = 18.0  # [design] and is this tall around each one

# --------------------------------------------------------------- device ----
# UniFi Cloud Gateway Fiber. Fanless: vents underneath and on both sides.
DEV_W = 212.8  # [dev]
DEV_D = 127.6  # [dev]
DEV_H = 30.0   # [dev]
DEV_MASS_G = 734  # [dev] with an SSD fitted

CLR_W = 1.2  # [design] total width clearance
CLR_H = 0.8  # [design]
CLR_D = 1.4  # [design]

POCKET_W = DEV_W + CLR_W   # 214.0
POCKET_HW = POCKET_W / 2   # 107.0

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
BODY_HW = POCKET_HW + RAIL_T  # 110.2, leaves 0.925 mm per side to the posts

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
TRAY_X1 = POCKET_HW   # 107, out to the inner face of the side rail
# The tray drops into the gap between the ledge's front nib and the rear stop.
# Modelled flush it is exactly as long as that gap, which in printed plastic
# is an interference fit, so it is made this much shorter.
TRAY_FIT = 0.4        # [design]
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
KEY_FIT = 0.3         # [design] clearance in its socket
KEY_X = 22.0          # [design] near the edges of the lap, so a pair holds the
                      # halves square as well as together
KEY_Y = (20.0, 116.0)  # [design] one pair just inside the gateway's front edge,
                       # one pair near its back

# ---------------------------------------------------------- the top bar ----
# Bolted on last, from the front, through the ear and into a hex nut trapped
# in the bar with the pocket facing rear. It nests into a notch in the side so
# the ear and the rail still meet below it.
BAR_T = 8.0         # [design] thickness, front to back
BAR_NUT_Y0 = 3.0    # [design] where the nut's near face sits, 5 mm of nut
                    # behind it filling the bar to its back face
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

# The display, measured on the device with callipers: a 21.0 x 10.0 stadium,
# centred on the case's width, and its CENTRE 14.0 above the case's bottom --
# confirmed, not inferred. It is the only thing on the front face: no reset
# button, and the power jack is at the back with the ports. So the faceplate
# needs this one window and nothing else.
#
# The window is a little larger than the display. The gateway can shift 0.6 mm
# either way between the rails, and showing a hair of white case is better
# than clipping the display. Its height needs no such allowance: the case sits
# on the tray, so DEV_Z0 fixes it.
WIN_W = 22.5          # [dev] 21.0 plus the float
WIN_H = 11.0          # [dev] 10.0 plus a little
WIN_Z = DEV_Z0 + 14.0  # 20.0, measured from the case's bottom, which sits on
                       # the tray at DEV_Z0
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
