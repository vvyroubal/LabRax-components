"""The nuc6i7kyk profile: what the sides in this folder are drawn around.
The rear legs in common/ take no notice of it."""

import params as P
from devices import Device


# Intel NUC6i7KYK, "Skull Canyon", 45 W. Intel publish 211 x 116 x 28, but
# measured whole -- the bulges on its ends, its feet -- the case is 233 x 143 x
# 40, and it goes between the rack's posts with about 1 mm to spare. Intel do
# not publish a weight; 700 g is a guess.
#
# Forty millimetres of case leaves 4.45 of the U, which is no room for a 6 mm
# tray under it and a flange over it. So it is BARE: no tray and no
# faceplate. It stands straight on its own sides' seats, 3.5 mm up, with its
# top at 43.5, inside the U. Its face is half a millimetre behind the ears,
# which overlap its ends and stop it coming forward; the back of it is half a
# millimetre short of the runner's tongue, which stops it going back. The
# posts hold it sideways.
#
# At 233 mm it is wider than the bay, so its sides are its own (side_nuc_l,
# side_nuc_r): rail and rear stop cut away over the case, a 19.2 mm seat under
# it joined into the ear in front and into a yoke round the leg behind. Where
# the leg runs on them they are the shared side's, so they ride the same legs.
# See SEAT_* and BULK_* in params.
#
# It takes its air in through its underside. Standing on two seats at its
# ends, it has nothing else under it but the U below.
DEVICE = Device(
    key="nuc", name="NUC6i7KYK",
    doc="NUC6i7KYK_LabRax",
    w=233.0, d=143.0, h=40.0, mass_g=700,
    clr_d=P.RUN_Y0 - P.BARE_Y0 - 143.0,   # 0.5, so it ends at the tongue
    bare=True,
)
