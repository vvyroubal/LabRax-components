"""The devices this bracket carries, and the two parts that differ per device.

The chassis -- side_l, side_r, leg_l, leg_r -- is sized by the RACK and knows
nothing about what goes in it. Only the tray pair and the faceplate are drawn
around a device, so a second device costs three prints, not seven.

What a profile has to say:

    w, d, h      the case, in mm
    mass_g       what it weighs, for the load checks
    plinth       how far the tray lifts it above its own top face. 0 puts the
                 case on the tray; a positive value centres a short device in
                 the U, which matters when its front face is what you look at.
    front        what the faceplate does: a Window to show a display through,
                 or a Frame that opens onto the ports and holds the case in.

Everything else -- where the case starts, where its lip goes, how high the
faceplate's flange sits -- is derived from those, so a new device is a dozen
numbers rather than a new set of drawings.
"""

import params as P


class Window(object):
    """A small opening to see a display through, placed by a rule.

    The rule is on the faceplate, not on the gateway: the oval's top edge sits
    `top_gap` below the underside of the top bar. Two calliper readings taken
    off the case put this window wrong twice; a rule about the printed part
    can be measured on the built solid, and verify measures it.
    """

    kind = "window"

    def __init__(self, w, h, top_gap, fillet, disp_w, disp_h):
        self.w = w
        self.h = h
        self.disp_w = disp_w
        self.disp_h = disp_h
        self.top_gap = top_gap
        self.fillet = fillet

    def z(self, dev):
        return dev.flange_z0 - self.top_gap - self.h / 2.0


class Frame(object):
    """An opening onto the ports, with a border that will not let the case out.

    Retention here is absolute rather than frictional: the case is wider and
    taller than the hole, so it cannot pass. The plug decides the height --
    an RJ45 with its latch needs about 16 mm -- and on a case only 21 mm tall
    that leaves only a couple of millimetres of border top and bottom. That is
    plenty to stop the case, and the plate itself is full depth above and
    below the opening, so nothing is structurally thin.
    """

    kind = "frame"

    def __init__(self, border_x, border_z, fillet=0.0):
        self.border_x = border_x
        self.border_z = border_z
        self.fillet = fillet

    def w(self, dev):
        return dev.w - 2 * self.border_x

    def h(self, dev):
        return dev.h - 2 * self.border_z

    def z(self, dev):
        return (dev.z0 + dev.z1) / 2.0


class Device(object):
    def __init__(self, key, name, w, d, h, mass_g, front, keys_y, plinth=0.0,
                 clr_w=None, clr_h=None, clr_d=None):
        self.key = key
        self.name = name
        self.w = w
        self.d = d
        self.h = h
        self.mass_g = mass_g
        self.front = front
        self.keys_y = keys_y
        self.plinth = plinth
        self.clr_w = P.CLR_W if clr_w is None else clr_w
        self.clr_h = P.CLR_H if clr_h is None else clr_h
        self.clr_d = P.CLR_D if clr_d is None else clr_d

    # --- where the case sits ------------------------------------------------
    @property
    def z0(self):
        """Underside of the case: the tray's top face, plus any plinth."""
        return P.TRAY_T + self.plinth

    @property
    def z1(self):
        return self.z0 + self.h

    @property
    def y0(self):
        """Front face, against the back of the faceplate."""
        return P.DEV_Y0

    @property
    def y1(self):
        """Where the tray's rear lip goes: the case plus its fore-aft float."""
        return self.y0 + self.d + self.clr_d

    @property
    def hw(self):
        """Half-width of the pocket the case needs, including its float."""
        return (self.w + self.clr_w) / 2.0

    @property
    def flange_z0(self):
        """Underside of the faceplate's top bar, which caps the case."""
        return self.z1 + self.clr_h

    @property
    def walls(self):
        """True when the case is narrow enough to need locating sideways.

        A case that fills the bay is held by the sides' own rails. One that
        does not has to be held by walls on its tray, or it wanders.
        """
        return self.hw < P.POCKET_HW - 1.0

    def part(self, base):
        """tray_l -> tray_ucg_l, faceplate -> faceplate_ucg.

        The key goes before the hand, so the two halves of a pair still sort
        next to each other.
        """
        if base.endswith("_l") or base.endswith("_r"):
            return "%s_%s%s" % (base[:-2], self.key, base[-2:])
        return "%s_%s" % (base, self.key)


# The gateway this bracket was drawn for. Fanless: it vents underneath and on
# both sides, and its display faces the rack front while the ports face back.
UCG_FIBER = Device(
    key="ucg", name="UCG-Fiber",
    w=212.8, d=127.6, h=30.0, mass_g=734,
    plinth=0.0,
    keys_y=(20.0, 116.0),   # one pair inside the front edge, one near the back
    front=Window(w=22.5, h=11.0, top_gap=6.0, fillet=6.0,
                 disp_w=21.0, disp_h=10.0),
)

# UniFi Flex Mini 2.5G, five 2.5 GbE ports on one long face, USB-C powered.
# 117.1 x 90 x 21.2, from techspecs.ui.com/unifi/switching/usw-flex-2-5g-5.
#
# It is 96.9 mm narrower than the bay, so its tray carries walls. It is also
# 8.8 mm shorter, and its ports are what you look at, so the plinth lifts it
# until the case is centred in the U rather than sitting on the floor with
# 17 mm of blank plate above it.
USW_FLEX_MINI = Device(
    key="usw", name="USW-Flex-2.5G-5",
    w=117.1, d=90.0, h=21.2, mass_g=206,
    plinth=(P.RACK_U - 21.2) / 2.0 - P.TRAY_T,   # 5.625, centres it in the U
    keys_y=(20.0, 85.0),    # its tray is shorter, so the back pair comes in
    front=Frame(border_x=4.0, border_z=1.85),
)

ALL = (UCG_FIBER, USW_FLEX_MINI)
BY_KEY = dict((d.key, d) for d in ALL)
