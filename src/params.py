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

# Front-to-back over the frame: the front posts' front face to the rear posts'
# rear face. Taken from the side panel, which spans the frame and measures
# 175.9 mm. The rear ears land on this, so if a rack comes out different this
# is the one number to change.
RACK_D = 175.9  # [rack]

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
EAR_T = 8.0        # [design] front and rear ear plate thickness
EAR_X0 = 98.0      # [design] inboard edge of the ears
RAIL_T = 3.2       # [design] side rail; 107.0 + 3.2 = 110.2 <= 111.125
BODY_HW = POCKET_HW + RAIL_T  # 110.2, leaves 0.925 mm per side to the posts

LEDGE_T = 5.0      # [design] the shelf the device sits on
LEDGE_X0 = 99.0    # [design] how far the shelf reaches under the device
DEV_Z0 = LEDGE_T           # 5.0
DEV_Z1 = DEV_Z0 + DEV_H    # 35.0
POCKET_TOP = DEV_Z1 + CLR_H  # 35.8
RAIL_TOP = 40.3    # [design]

DEV_Y0 = 8.0                    # [design] front face, against the top bar
DEV_Y1 = DEV_Y0 + DEV_D + CLR_D  # 137.0

STOP_T = 7.0       # [design] rear stop thickness
STOP_X0 = 99.0     # [design]

# Ventilation in the side rails -- the device vents through its sides.
RAIL_VENT_Z0 = 10.0
RAIL_VENT_Z1 = 30.0
RAIL_VENTS_Y = ((24.0, 52.0), (60.0, 88.0), (96.0, 124.0))  # [design]

# ---------------------------------------------------------- the top bar ----
# Bolted on last, from the front, through the ear and into a hex nut trapped
# in the bar with the pocket facing rear. It nests into a notch in the side so
# the ear and the rail still meet below it.
BAR_T = 8.0         # [design] thickness, front to back
BAR_X1 = 111.0      # [design] outboard end. The bar sits between the
                    # posts, so this must stay inside 111.125.
BAR_Z0 = 36.8       # [design] underside over the device
BAR_END_X0 = 96.0   # [design] the taller end block starts here
BAR_END_Z0 = 23.7   # [design] deep enough for an M6 nut across its flats
BAR_FLANGE_D = 17.0  # [design] how far it reaches back over the device
BAR_FLANGE_Z0 = BAR_Z0      # flush with the bar's underside

BAR_SCREW_X = 103.0   # [design] inboard of the rack slots, inside the ear
BAR_SCREW_Z = 30.16   # [design] midway between two EIA holes

# ------------------------------------------------------------ fasteners ----
M6_CLEAR = 6.4      # [rack]
M6_HEX_AF = 10.09   # [rack] 11.65 across corners
M6_HEX_D = 5.0      # [rack] nut thickness
