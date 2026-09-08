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
LIP_T = 3.5     # [design] top lip thickness
LIP_IN = 4.0    # [design] how far the top lip reaches over the device

DEV_Z0 = FLOOR_T                    # 4.0  device underside
DEV_Z1 = DEV_Z0 + DEV_H             # 34.0 device top
POCKET_TOP = DEV_Z0 + DEV_H + CLR_H  # 34.8
RAIL_TOP = POCKET_TOP + LIP_T       # 38.3

BODY_HW = POCKET_HW + RAIL_T  # 110.2, leaves 0.925 mm per side to the posts
LIP_X = POCKET_HW - LIP_IN    # 103.0 inner edge of the top lip

BODY_D = 141.0  # [design] floor depth; device occupies Y 0..129

# Faceplate window. Smaller than the device on every side, so the device --
# loaded from the rear -- cannot pass through it. 2.0-2.4 mm of lip all round
# is enough to catch it without masking any connector.
WIN_HW = 104.0   # [design] 208 mm wide vs the device's 212.8
WIN_Z0 = 8.0     # [design] 2.0 mm below the device underside
WIN_Z1 = 34.0    # [design] 2.0 mm above the device top

# ---------------------------------------------------- split for printing ---
# 212.8 mm will not fit a 180 x 180 bed in any orientation, so the bracket is
# a centre tray plus two mirrored end brackets. 172 mm keeps 4 mm of margin.
SPLIT_X = 72.0   # [design] tray / ear boundary
LAP_X = 86.0     # [design] outboard end of the faceplate lap; also the widest
                 # point of the tray, so 2*LAP_X must fit the bed
BOSS_D = 14.0    # [design] depth of the tray's screw boss above the device

# Joint screws: M3 self-tapping into a printed pilot, driven from the front
# through the ear's half of the faceplate lap.
M3_CLEAR = 3.3
M3_PILOT = 2.5
M3_CB_D = 6.2   # button-head counterbore
M3_CB_Z = 2.0
JOINT_SCREW_X = (76.0, 83.0)  # [design] within the lap
JOINT_SCREW_Z = (4.0, 39.0)   # [design] one row in the front rail below the
                              # window, one in the top rail above it

# ------------------------------------------------------------- venting -----
VENT_W = 9.0        # [design] floor slot width
VENT_PITCH = 15.0   # [design]
VENT_Y0 = 14.0
VENT_Y1 = 120.0
VENT_MAX_X = 78.0   # [design] keep slots clear of the tray/ear joint

RAIL_VENT_Z0 = 10.0
RAIL_VENT_Z1 = 30.0
RAIL_VENTS_Y = ((16.0, 44.0), (56.0, 84.0), (96.0, 124.0))  # [design]

# --------------------------------------------------------- rear retainer ---
# The device slides in from the rear and stops against the faceplate lips. A
# pair of small stops then closes the rear. They sit at the extreme corners so
# they cannot foul a connector.
STOP_X0 = 98.0       # [design] 8.4 mm of overlap onto the device corner
STOP_Y0 = POCKET_D   # 129.0
STOP_T = 4.0         # [design] upright thickness
STOP_Z1 = 28.0       # [design] upright height
STOP_FOOT_D = 12.0   # [design] foot length behind the upright
STOP_SCREW_Y = (136.0,)  # [design] hold-down screw
STOP_FOOT_T = 6.0    # [design] foot thickness, enough for the screw counterbore
