"""The tl-sg108e profile: what the panel in this folder is drawn around.

It takes nothing from the chassis in common/."""

from devices import Device


# TP-Link TL-SG108E, eight gigabit ports on one long face, external 5 V brick.
# 158 x 101 x 25, from tp-link.com/us/business-networking/soho-switch-easy-
# smart/tl-sg108e. TP-Link do not publish a weight; 250 g is a guess.
#
# It goes in a PANEL of its own (PNL_* in params), after a rack panel made
# for this switch: a plate across the rack with a 159 x 26 opening, the case
# standing in it flush with the front, held along each side in a channel and
# pressed down by a finger on top. Bolted to the front posts only -- it is
# light, so it needs neither the sides, the rear legs nor a tray. Two tray-
# and-faceplate kits came before it and both were no good in print: the case
# sat 8 mm behind a 4 mm border, then in a full opening on a tray.
#
# The panel is 254 wide and the bed 180, so it is two halves joined behind
# the opening's bars by two splice plates and four M3 x 16 with nuts. All
# four parts go on one A1 mini plate, the halves face down.
#
# Its power jack is on the BACK; the panel is open behind the case.
DEVICE = Device(
    key="sg108e", name="TL-SG108E",
    doc="TL_SG108E_LabRax",
    w=158.0, d=101.0, h=25.0, mass_g=250,
    panel=True,
)
