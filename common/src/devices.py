"""The devices this bracket carries, and the two parts that differ per device.

Each device has a folder of its own at the top of the project -- ucg-fiber/,
usw-flex-mini/ and so on -- holding its profile in device.py and everything
made for it: its tray and faceplate STLs, its FreeCAD document and STEP, its
3MF, its renders. The chassis,
and the code, are in common/. This module holds the classes a profile is
written with, loads the profiles, and says where each part's files go.

The chassis -- side_l, side_r, leg_l, leg_r -- is sized by the RACK and knows
nothing about what goes in it. Only the tray pair and the faceplate are drawn
around a device, so a second device costs three prints, not seven.

What a profile has to say:

    doc          what its FreeCAD document and STEP are called, less the
                 extension: the same stem its 3MF has
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

import importlib.util
import os

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

    def __init__(self, border_x, border_z, border_z_top=None, fillet=0.0):
        self.border_x = border_x
        # Top and bottom are separate because the ports are not centred on the
        # case. The bottom edge is the one that matters -- it is what a plug's
        # body has to clear -- so it stays put and the top edge moves.
        self.border_z = border_z
        self.border_z_top = border_z if border_z_top is None else border_z_top
        self.fillet = fillet

    def w(self, dev):
        return dev.w - 2 * self.border_x

    def h(self, dev):
        return dev.h - self.border_z - self.border_z_top

    def z(self, dev):
        return dev.z0 + self.border_z + self.h(dev) / 2.0


class Device(object):
    def __init__(self, key, name, doc, w, d, h, mass_g, front, keys_y,
                 plinth=0.0, vent=False, clr_w=None, clr_h=None, clr_d=None):
        self.key = key
        self.name = name
        self.doc = doc
        self.w = w
        self.d = d
        self.h = h
        self.mass_g = mass_g
        self.front = front
        self.keys_y = keys_y
        self.plinth = plinth
        # True for a device that draws its cooling air through its underside.
        # Its tray is slotted; a solid one would be a lid on the intake.
        self.vent = vent
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

    # --- where its files go -------------------------------------------------
    # `dir` is the device's own folder, set when its device.py is loaded.
    @property
    def parts(self):
        """The three prints drawn around this device."""
        return tuple(self.part(b) for b in ("tray_l", "tray_r", "faceplate"))

    @property
    def stl_dir(self):
        return os.path.join(self.dir, "stl")

    @property
    def cad_path(self):
        """Its own document: the chassis and its three parts, nothing else."""
        return os.path.join(self.dir, self.doc + ".FCStd")

    @property
    def step_path(self):
        return os.path.join(self.dir, self.doc + ".step")

    @property
    def images_dir(self):
        return os.path.join(self.dir, "images")


# ------------------------------------------------------------------ layout --
# common/src/devices.py -> the project root, unless the caller says otherwise.
ROOT = os.environ.get("UCG_ROOT") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMMON = os.path.join(ROOT, "common")

# The four parts every device shares. They are sized by the rack, not by a
# device, so they live in common/.
CHASSIS = ("side_l", "side_r", "leg_l", "leg_r")

# One folder per device, in the order they are built and reported. Adding a
# device is a folder with a device.py in it, and its name here.
DIRS = ("ucg-fiber", "usw-flex-mini", "tl-sg108e", "nuc6i7kyk")


def _load(folder):
    path = os.path.join(ROOT, folder, "device.py")
    spec = importlib.util.spec_from_file_location(
        "device_" + folder.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.DEVICE.dir = os.path.join(ROOT, folder)
    return mod.DEVICE


ALL = tuple(_load(f) for f in DIRS)
BY_KEY = dict((d.key, d) for d in ALL)


def stl_dir(part):
    """Where a part's STL goes: common/stl for the chassis, else its device's."""
    if part in CHASSIS:
        return os.path.join(COMMON, "stl")
    for dev in ALL:
        if part in dev.parts:
            return dev.stl_dir
    raise KeyError("no device makes %r" % part)


def stl_path(part):
    return os.path.join(stl_dir(part), part + ".stl")
