"""The ucg-fiber profile: what the tray and faceplate in this folder are drawn
around. The chassis in common/ takes no notice of it."""

from devices import Device, Window


# The gateway this bracket was drawn for. Fanless: it vents underneath and on
# both sides, and its display faces the rack front while the ports face back.
DEVICE = Device(
    key="ucg", name="UCG-Fiber",
    doc="UCG_Fiber_LabRax",
    w=212.8, d=127.6, h=30.0, mass_g=734,
    plinth=0.0,
    keys_y=(20.0, 116.0),   # one pair inside the front edge, one near the back
    front=Window(w=22.5, h=11.0, top_gap=7.0, fillet=6.0,
                 disp_w=21.0, disp_h=10.0),
)
