"""Every dimension for the UCG-Fiber / Lab Rax bracket, with its provenance.

Coordinate system used throughout the model (millimetres):

    X   rack width, 0 = rack centreline, +X = right when facing the rack
    Y   depth,      0 = front face of the rack posts, +Y = into the rack
    Z   height,     0 = bottom edge of the 1U the bracket occupies

Numbers tagged [rack] were measured off the Lab Rax rack model itself, [dev]
comes from Ubiquiti's published specification, and [design] is a choice made
here. See docs/measurements.md for how the [rack] figures were obtained.
"""

# ---------------------------------------------------------------- rack -----
# Lab Rax 10" rack, bolted version. Follows EIA-310 vertical spacing.
RACK_U = 44.45  # [rack] one rack unit
FACE_W = 254.0  # [rack] faceplate width, 10" nominal
FACE_HW = FACE_W / 2

# Mounting screw columns. 236.525 is the 10" analogue of the 19" 465.1 figure;
# confirmed on the rack posts, whose holes sit 7.1375 mm inboard of the post
# face that bounds the 222.25 mm opening.
SCREW_DX = 236.525  # [rack] horizontal distance between the two screw columns
SCREW_X = SCREW_DX / 2

# EIA-310 hole heights within one U, measured from the bottom of the U.
# Gaps run 15.875 / 15.875 / 12.7 mm; confirmed on the post at 15.902 / 12.646
# (mesh discretisation) and on a known-good Lab Rax faceplate at 6.325 /
# 22.225 / 38.125.
EIA_Z = (6.35, 22.225, 38.1)  # [rack]

# The rack is 3D printed and the posts are bolted, so the screw columns move a
# little from build to build. Slotting the holes absorbs that; the reference
# faceplate uses 11.4 x 7.4 mm for the same reason.
SLOT_W = 11.0  # [design] horizontal slot length -> +/-2.3 mm of adjustment
SLOT_H = 6.6   # [design] M6 clearance across the slot

# Clear width between the two front posts. Anything behind the faceplate has
# to pass through this.
POST_CLEAR_W = 222.25  # [rack]
POST_CLEAR_HW = POST_CLEAR_W / 2
POST_DEPTH = 35.0  # [rack] post cross-section front-to-back (30 mm across)

# --------------------------------------------------------------- device ----
# UniFi Cloud Gateway Fiber (UCG-Fiber). Fanless: vents on the bottom and both
# sides. Ports + DC input on one long face, 0.96" status display on the other.
DEV_W = 212.8  # [dev]
DEV_D = 127.6  # [dev]
DEV_H = 30.0   # [dev]
DEV_MASS_G = 734  # [dev] with an SSD fitted

# ------------------------------------------------------------------ fit ----
# The device is 212.8 mm wide in a 222.25 mm opening: 4.7 mm per side for a
# side rail plus clearance. These are deliberately tight.
CLR_W = 1.2  # [design] total width clearance
CLR_H = 0.8  # [design] total height clearance
CLR_D = 1.4  # [design] total depth clearance

POCKET_W = DEV_W + CLR_W   # 214.0
POCKET_HW = POCKET_W / 2   # 107.0
POCKET_D = DEV_D + CLR_D   # 129.0

# ----------------------------------------------------------- structure -----
FACE_T = 8.0    # [design] faceplate thickness; laps as 2 x 4 mm at the joint
FLOOR_T = 6.0   # [design] floor under the device; also deep enough that the
                # joint screws' counterbore and pilot both fit in the front rail
RAIL_T = 3.2    # [design] side rail; 107.0 + 3.2 = 110.2 <= 111.125

# The device drops into the cradle from above -- it cannot slide in from the
# rear, because the M6 joint blocks stand in the way and there is nowhere else
# to put them. So the side rails carry no top lip; the top bar's flange holds
# the device down at the front and the rear stops do it at the back.
HOLD_T = 3.5    # [design] thickness of the stops' hold-down flange
HOLD_D = 3.0    # [design] how far it reaches forward over the device; kept
                # short so it bridges rather than needing support

DEV_Z0 = FLOOR_T                    # 4.0  device underside
DEV_Z1 = DEV_Z0 + DEV_H             # 34.0 device top
POCKET_TOP = DEV_Z0 + DEV_H + CLR_H  # 34.8
RAIL_TOP = POCKET_TOP + HOLD_T      # 40.3

BODY_HW = POCKET_HW + RAIL_T  # 110.2, leaves 0.925 mm per side to the posts

BODY_D = 144.0  # [design] floor depth; device occupies Y 0..129

# Faceplate window. Smaller than the device on every side, so the device --
# loaded from the rear -- cannot pass through it. 2.0-2.4 mm of lip all round
# is enough to catch it without masking any connector.
WIN_HW = 104.0   # [design] 208 mm wide vs the device's 212.8
WIN_Z0 = 8.0     # [design] 2.0 mm below the device underside
WIN_Z1 = 34.0    # [design] 2.0 mm above the device top

# ---------------------------------------------------- split for printing ---
# 212.8 mm will not fit a 180 x 180 bed in any orientation, so the bracket is
# a centre tray plus two mirrored end brackets. 172 mm keeps 4 mm of margin.
SPLIT_X = 66.0   # [design] tray / ear boundary
LAP_X = 86.0     # [design] outboard end of the faceplate lap; also the widest
                 # point of the tray, so 2*LAP_X must fit the bed
BOSS_D = 14.0    # [design] depth of the tray's flange above the device

# ------------------------------------------------------- captive nuts ------
# Lab Rax bolts its printed parts together with a hex nut trapped behind a
# clearance hole. Measured off Bolted+Version+Post+Joiner.stl: a 6.40 mm
# clearance hole 2 mm deep, then a hexagonal pocket 11.65 mm across corners
# (10.09 across flats, so AF/sqrt(3) circumradius) and 5 mm deep -- an M6 nut
# is 10.0 across flats and 5.0 thick. The same pattern is used here at both
# sizes. See docs/measurements.md.
M6_CLEAR = 6.4      # [rack]
M6_HEX_AF = 10.09   # [rack] 11.65 across corners
M6_HEX_D = 5.0      # [rack] nut thickness
M6_CB_D = 10.9      # [rack] button-head counterbore
M6_CB_Y = 3.5

M3_CLEAR = 3.4      # [design]
M3_HEX_AF = 5.6     # [design] M3 nut is 5.5 across flats
M3_HEX_D = 2.6      # [design] M3 nut is 2.4 thick
M3_CB_D = 6.2       # [design]
M3_CB_Y = 2.0

# A trapped nut needs roughly 13 mm of material around it at M6, and the
# faceplate rails are only 8.0 and 10.45 mm tall, so the faceplate joints are
# M3 and the M6 ones live behind the device where the whole 1U is free.
JOINT_SCREW_X = (70.0, 78.0)  # [design] within the lap, clear of the step
JOINT_SCREW_Z = (4.0, 39.0)   # [design] one row in the front rail below the
                              # window, one in the top rail above it

# ------------------------------------------- how the tray meets the ear ----
# The device's weight has to reach the rack. It goes into the tray, across to
# the ears, and out through their M6 rack screws -- so the tray must bear on
# the ear along its whole length, not hang off a couple of bolts. A step lap
# runs the full depth: the ear keeps the bottom 3 mm and the tray sits on it.
# Both edges stay 3 mm thick, and the tray's 4 mm overhang bridges cleanly.
STEP_X0 = 82.0   # [design] lap runs from here out to LAP_X
STEP_Z = 3.0     # [design] the ear's share of the floor under the lap

# ------------------------------------------------- rear M6 joint blocks ----
# One block per side, lapped front-to-back behind the device, carrying two M6
# stacked vertically. Sits just inboard of the ear so it is short, and the ear
# ties it out to the side rail with a web -- without that the block hangs off
# the 6 mm floor edge and the joint is worth nothing.
REAR_X0 = 70.0       # [design] inboard end; sets how wide the ear prints
REAR_Y0 = 130.0      # [design] 1.0 mm behind the device pocket
REAR_Y_MID = 137.0   # [design] tray block ends / ear block begins
REAR_Y1 = 144.0      # [design]
REAR_Z1 = 28.0       # [design] room for two M6 nuts, one above the other
REAR_BOLT_X = (78.0,)       # [design] 2.2 mm of wall each side of the nut
REAR_BOLT_Z = (7.0, 21.0)   # [design]
REAR_TIE_Z = 9.0     # [design] low stiffener along the tray's rear edge

# The rear beam runs forward to meet the device, so it is the rear stop as
# well -- no separate part. Outboard enough that it cannot foul a connector
# whichever way round the device is fitted.
REAR_STOP_X0 = 95.0  # [design] 11.4 mm of overlap onto the device's corner

# ------------------------------------------------------------- venting -----
VENT_W = 9.0        # [design] floor slot width
VENT_PITCH = 15.0   # [design]
VENT_Y0 = 14.0
VENT_Y1 = 120.0
VENT_MAX_X = 78.0   # [design] keep slots clear of the tray/ear joint

RAIL_VENT_Z0 = 10.0
RAIL_VENT_Z1 = 30.0
RAIL_VENTS_Y = ((16.0, 44.0), (56.0, 84.0), (96.0, 124.0))  # [design]

