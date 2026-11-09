"""The tl-sg108e profile: what the tray and faceplate in this folder are drawn
around. The chassis in common/ takes no notice of it."""

import params as P
from devices import Device, Opening


# TP-Link TL-SG108E, eight gigabit ports on one long face, external 5 V brick.
# 158 x 101 x 25, from tp-link.com/us/business-networking/soho-switch-easy-
# smart/tl-sg108e. TP-Link do not publish a weight; 250 g is a guess, and it
# only feeds the load checks, where the UCG-Fiber's 734 g is the tested case.
#
# Its whole face shows. It used to sit behind a Frame with a 4 mm border all
# round, which left a 150 x 17 window onto a 158 x 25 face, 8 mm deep: the
# printed one was no good. It is an Opening now, after a rack panel made for
# this switch: 159 x 26, the case plus 0.5 mm all round, with the case
# standing in it flush with the front of the plate. Nothing is in front of
# it, so its tray's walls grip it with a sprung leaf each (GRIP_* in params),
# and it slides in and out through the front with the bracket in the rack.
#
# Its power jack is on the BACK. The tray's rear lip stands 3 mm above the
# case floor, well under any barrel jack, and verify measures that nothing
# else is behind the case above that line.
#
# The opening's front edge is broken with a 1 mm round. The 6 mm one the
# Frame had would leave a 6 mm moat round a face that is now flush with it.
DEVICE = Device(
    key="sg108e", name="TL-SG108E",
    doc="TL_SG108E_LabRax",
    w=158.0, d=101.0, h=25.0, mass_g=250,
    plinth=(P.RACK_U - 25.0) / 2.0 - P.TRAY_T,   # 3.725, centres it in the U
    keys_y=(20.0, 95.0),
    front=Opening(clr=0.5, fillet=1.0),
)
