"""The tl-sg108e profile: what the tray and faceplate in this folder are drawn
around. The chassis in common/ takes no notice of it."""

import params as P
from devices import Device, Frame


# TP-Link TL-SG108E, eight gigabit ports on one long face, external 5 V brick.
# 158 x 101 x 25, from tp-link.com/us/business-networking/soho-switch-easy-
# smart/tl-sg108e. TP-Link do not publish a weight; 250 g is a guess, and it
# only feeds the load checks, where the UCG-Fiber's 734 g is the tested case.
#
# Ports face front like the Flex Mini, so it gets a Frame. It is 25 mm tall
# rather than 21.2, which buys a real border: 4 mm all round still leaves a
# 17 mm opening, comfortably over the 16 an RJ45 plug with its latch needs.
#
# Its power jack is on the BACK. The tray's rear lip stands 3 mm above the
# case floor, well under any barrel jack, and verify measures that nothing
# else is behind the case above that line.
#
# The opening's front edge is rounded over by 6 mm, as the gateway's window
# and the Flex Mini's frame are. There is room for it here: the opening ends
# at x = +/-75, so the rim reaches 81, well short of the nut slots at 93.87.
DEVICE = Device(
    key="sg108e", name="TL-SG108E",
    doc="TL_SG108E_LabRax",
    w=158.0, d=101.0, h=25.0, mass_g=250,
    plinth=(P.RACK_U - 25.0) / 2.0 - P.TRAY_T,   # 3.725, centres it in the U
    keys_y=(20.0, 95.0),
    front=Frame(border_x=4.0, border_z=4.0, fillet=6.0),
)
