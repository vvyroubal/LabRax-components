"""The nuc6i7kyk profile: what the tray, faceplate and sides in this folder
are drawn around. The rear legs in common/ take no notice of it."""

import params as P
from devices import Device, Frame


# Intel NUC6i7KYK, "Skull Canyon". Intel publish 211 x 116 x 28 and 45 W, but
# their 211 leaves out the bulges on its ends: measured across them the case
# is about 223 mm, and it goes between the rack's posts with about 1 mm to
# spare. Intel do not publish a weight; 700 g is a guess and only feeds the
# load checks, where the gateway's 734 g is the tested case.
#
# At 223 mm it is wider than the 214 mm bay between the shared sides' rails,
# so it gets sides of its own (side_nuc_l, side_nuc_r): the rail is cut down
# below the case for the length of it, and the case stands between the posts
# with nothing of the bracket beside it. Nothing holds it sideways but the
# posts, half a millimetre off each end.
#
# It is the first device here that is not passive. A 45 W part with a blower
# takes its air in through the underside, and the tray sits flat against it,
# so this tray is slotted -- see vent=True and VENT_* in params.
#
# Ports are on BOTH long faces: two USB 3.0 and the audio jack at the front,
# and everything else -- Thunderbolt 3, HDMI, two mini-DP, Ethernet, two more
# USB, the power inlet -- at the back. The frame shows the front pair; the
# back is open to the rear of the rack as it is for every device here.
#
# The frame's border cannot be the 4 mm the other switches use: at 223 mm wide
# a 4 mm border would put the opening at x = +/-107.5, straight through the
# faceplate's own M6 nut pockets at +/-100. 22 mm keeps it 5.5 mm clear.
#
# The opening's front edge is rounded over like the gateway's window and the
# Flex Mini's frame, but by 4 mm rather than their 6. The opening ends at
# x = +/-89.5 and the nut slots start at +/-93.87: a 6 mm round would run its
# rim to 95.5, into them. 4 mm stops at 93.5 and leaves half the plate behind.
DEVICE = Device(
    key="nuc", name="NUC6i7KYK",
    doc="NUC6i7KYK_LabRax",
    w=223.0, d=116.0, h=28.0, mass_g=700,
    plinth=(P.RACK_U - 28.0) / 2.0 - P.TRAY_T,   # 2.225, centres it in the U
    keys_y=(20.0, 110.0),
    vent=True,
    front=Frame(border_x=22.0, border_z=5.0, fillet=4.0),
)
