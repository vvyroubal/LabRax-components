"""The usw-flex-mini profile: what the tray and faceplate in this folder are drawn
around. The chassis in common/ takes no notice of it."""

import params as P
from devices import Device, Frame


# UniFi Flex Mini 2.5G, five 2.5 GbE ports on one long face, USB-C powered.
# 117.1 x 90 x 21.2, from techspecs.ui.com/unifi/switching/usw-flex-2-5g-5.
#
# It is 96.9 mm narrower than the bay, so its tray carries walls. It is also
# 8.8 mm shorter, and its ports are what you look at, so the plinth lifts it
# until the case is centred in the U rather than sitting on the floor with
# 17 mm of blank plate above it.
DEVICE = Device(
    key="usw", name="USW-Flex-2.5G-5",
    w=117.1, d=90.0, h=21.2, mass_g=206,
    plinth=(P.RACK_U - 21.2) / 2.0 - P.TRAY_T,   # 5.625, centres it in the U
    keys_y=(20.0, 85.0),    # its tray is shorter, so the back pair comes in
    # The opening is 1 mm taller at the top than a centred one would be: with
    # it centred, an RJ45 would not go in. The bottom edge is fixed -- that is
    # the one a plug's body sits on -- so the extra millimetre comes off the
    # top border, which drops from 1.85 to 0.85.
    # 6 mm round-over on the opening's front edge, the same bezel the
    # gateway's window has. It leaves 2 mm of the 8 mm plate behind it.
    front=Frame(border_x=4.0, border_z=1.85, border_z_top=0.85, fillet=6.0),
)
