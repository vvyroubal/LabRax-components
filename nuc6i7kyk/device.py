"""The nuc6i7kyk profile: what the tray and faceplate in this folder are drawn
around. The chassis in common/ takes no notice of it."""

import params as P
from devices import Device, Frame


# Intel NUC6i7KYK, "Skull Canyon". 211 x 116 x 28 and 45 W, from intel.com.
# Intel do not publish a weight; 700 g is a guess and only feeds the load
# checks, where the gateway's 734 g is the tested case.
#
# At 211 mm it is the second device to fill the bay: the sides' own rails hold
# it, so its tray needs no walls. The 3 mm it leaves across the bay is the
# clearance, not the 1.2 the others use, so it says so rather than letting the
# check go looking for a number that is not there.
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
# The frame's border cannot be the 4 mm the other switches use: at 211 mm wide
# a 4 mm border would put the opening at x = +/-101.5, straight through the
# faceplate's own M6 nut pockets at +/-100. 16 mm keeps it 5.5 mm clear.
DEVICE = Device(
    key="nuc", name="NUC6i7KYK",
    w=211.0, d=116.0, h=28.0, mass_g=700,
    plinth=(P.RACK_U - 28.0) / 2.0 - P.TRAY_T,   # 2.225, centres it in the U
    keys_y=(20.0, 110.0),
    vent=True,
    clr_w=3.0,
    front=Frame(border_x=16.0, border_z=5.0),
)
