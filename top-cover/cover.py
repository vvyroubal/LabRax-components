"""A top cover for the Lab Rax 10" rack: two halves, vented, with a logo.

It takes the place of the rack's own top panel, so its outline is that panel's:
228.05 x 171.5 x 3, the two halves 114.025 wide like the rack's own Bottom
Panel Halves, butted on the centreline and seated by their edges in the top
frame's grooves.

The halves are held together the way the rack holds its posts together: by
post joiners, the rack's own Bolted Version Post Joiner drawn again here to
the same dimensions, one M6 through each half into a nut trapped in the
joiner below. The bolt heads are on top.

Coordinate system (millimetres), as the rest of the project:

    X   across the rack, 0 = centreline, the seam between the halves
    Y   front to back, 0 = middle of the panel, -Y = front of the rack
    Z   up, 0 = underside of the panel, PANEL_T = its top

Two things are here only as guides and are not copied:

  - Flying4T's "Lab Rax - Top Dual 92mm Fan Panel" (CC BY-NC-SA) gave where the
    vents go: two 92 mm fan positions, 110 mm apart, toward one end. The grille
    here is its own honeycomb.
  - Krafty3D's "Skynet Logo - Plate" (Standard Digital File License) is the
    logo. It is read from top-cover/assets/Skynet.3mf at build time, scaled,
    and never committed: see logo.py and .gitignore.
"""

import math

import FreeCAD as App
from FreeCAD import Vector

import sk

# ------------------------------------------------------------- the panel ---
PANEL_W = 228.05     # [rack] the rack's top panel, Bottom Panel Half x 2
PANEL_D = 171.5      # [rack]
PANEL_T = 3.0        # [rack] and the groove it seats in
HALF_W = PANEL_W / 2.0   # 114.025, one half
# The frame holds the panel by its edges, about 3 mm into a groove, and the
# rack's own joint between its panel halves runs only 120 mm of the 171.5: the
# frame's front and back members are under the rest. A joiner has to stay
# inside that.
EDGE = 3.0           # [rack] how far the edge is hidden in the groove
CLEAR_HD = 60.0      # [rack] half the clear run under the seam, from the
                     # rack's backing strip: 119.9 long, centred

# ------------------------------------------------------------ the vents ----
# Two 92 mm fans' worth of grille, where Flying4T's panel puts its fans: 55 mm
# either side of the centre. That panel has them 30 mm off the middle; these
# are 36 mm back, which leaves the front band tall enough for the logo.
GRILLE_X = 55.0      # [guide] each grille's centre, either side of the seam
GRILLE_Y = 36.0      # [design] behind the middle, toward the back
GRILLE_D = 89.0      # [guide] the opening a 92 mm fan blows through
HEX_AF = 8.0         # [design] each cell across its flats
HEX_RIB = 1.6        # [design] between cells: four 0.4 mm lines
FAN_PITCH = 82.5     # [fan] a 92 mm fan's screw square
FAN_HOLE_D = 4.5     # [fan] for its screws
FAN_RING = 1.5       # [design] solid kept round each fan screw hole

# ----------------------------------------------------------- the joiner ----
# The rack's Bolted Version Post Joiner, measured off its own mesh: a 39.7 x
# 23.85 x 7 plate, two M6 nut traps 20 mm apart and 5 mm deep, each over a
# 2 mm floor with a 6.4 mm hole. The holes are not on the plate's centreline
# but 0.575 off it, toward the side whose two corners are chamfered 0.5.
JOIN_L = 39.7        # [rack] across the seam
JOIN_W = 23.85       # [rack] along it
JOIN_T = 7.0         # [rack]
JOIN_FLOOR = 2.0     # [rack] under each nut, against the panel
JOIN_PITCH = 20.0    # [rack] hole to hole: 10 mm each side of the seam
JOIN_HOLE_D = 6.4    # [rack]
JOIN_NUT_AF = 10.08  # [rack] the trap across its flats
JOIN_OFF = 0.575     # [rack] hole line off the plate's centreline
JOIN_CHAMFER = 0.5   # [rack]
# Two joiners, both between the grilles and both inside the clear run under
# the seam, so the bolt heads stay out of the logo at the front.
JOIN_Y = (20.0, 47.0)    # [design] hole lines
PANEL_HOLE_D = 6.6   # [design] M6 clearance through the panel
BOLT_HEAD_D = 11.0   # [design] room for a button head and its washer
KEEP = 1.0           # [design] solid kept round a head or a joiner

# ------------------------------------------------------------ the logo -----
LOGO_H = 0.6         # [design] how far it stands proud: three 0.2 layers
LOGO_MARGIN = 3.0    # [design] clear of the groove, the grilles, the edge
MIN_STROKE = 0.45    # [design] the thinnest line a 0.4 nozzle lays down
# Its band: in front of the grilles, behind the front groove.
LOGO_Y0 = -PANEL_D / 2.0 + EDGE + LOGO_MARGIN               # -79.75
LOGO_Y1 = GRILLE_Y - GRILLE_D / 2.0 - LOGO_MARGIN           # -11.5
LOGO_X1 = HALF_W - EDGE - LOGO_MARGIN                       # 108.0


def joiner_holes():
    """Where the bolts go, (x, y), both halves."""
    return [(sx * JOIN_PITCH / 2.0, y) for y in JOIN_Y for sx in (-1, 1)]


def grille_cells(sx):
    """Centres of the honeycomb cells in one grille, sx -1 left, +1 right.

    Cells are hexagons with flats top and bottom, on a lattice whose rib is
    HEX_RIB everywhere. A cell is kept only if it lies wholly inside the
    opening and clear of every fan screw, bolt head and joiner, so no cell is
    ever cut through by something else.
    """
    gx, gy = sx * GRILLE_X, GRILLE_Y
    pitch = HEX_AF + HEX_RIB            # flat to flat, cell to cell
    rc = HEX_AF / math.sqrt(3.0)        # a cell's corner radius
    dx = 1.5 * pitch / math.sqrt(3.0)   # column spacing
    keep_out = []                       # (cx, cy, r) circles to stay clear of
    for fx in (-1, 1):
        for fy in (-1, 1):
            keep_out.append((gx + fx * FAN_PITCH / 2.0, gy + fy * FAN_PITCH / 2.0,
                             FAN_HOLE_D / 2.0 + FAN_RING))
    for hx, hy in joiner_holes():
        keep_out.append((hx, hy, BOLT_HEAD_D / 2.0 + KEEP))
    boxes = [(-JOIN_L / 2.0 - KEEP, JOIN_L / 2.0 + KEEP,
              y - JOIN_W / 2.0 + JOIN_OFF - KEEP, y + JOIN_W / 2.0 + JOIN_OFF + KEEP)
             for y in JOIN_Y]
    out = []
    n = int(GRILLE_D / dx) + 2
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            cx = gx + i * dx
            cy = gy + j * pitch + (pitch / 2.0 if i % 2 else 0.0)
            if math.hypot(cx - gx, cy - gy) + rc > GRILLE_D / 2.0:
                continue
            if any(math.hypot(cx - kx, cy - ky) < rc + kr for kx, ky, kr in keep_out):
                continue
            if any(x0 - rc < cx < x1 + rc and y0 - rc < cy < y1 + rc
                   for x0, x1, y0, y1 in boxes):
                continue
            if sx * cx - rc < 1.0:      # never across, or at, the seam
                continue
            out.append((cx, cy))
    return out


def half(doc, sx, name):
    """One half of the cover, sx -1 left, +1 right, as a PartDesign Body."""
    bd = sk.body(doc, name)
    x0, x1 = (-HALF_W, 0.0) if sx < 0 else (0.0, HALF_W)

    s = sk.sketch(doc, bd, name + "_Sk_panel",
                  sk.plane(Vector(0, 0, 0), sk.X, sk.Y))
    sk.rect(s, x0, -PANEL_D / 2.0, x1, PANEL_D / 2.0)
    sk.pad(doc, bd, s, PANEL_T)

    # The grille: one sketch of every cell, cut through.
    s = sk.sketch(doc, bd, name + "_Sk_grille",
                  sk.plane(Vector(0, 0, 0), sk.X, sk.Y))
    for cx, cy in grille_cells(sx):
        sk.hexagon(s, cx, cy, HEX_AF)
    sk.pocket(doc, bd, s, PANEL_T)

    # Screw holes for a fan, if one is ever wanted under the grille.
    s = sk.sketch(doc, bd, name + "_Sk_fan",
                  sk.plane(Vector(0, 0, 0), sk.X, sk.Y))
    for fx in (-1, 1):
        for fy in (-1, 1):
            sk.circle(s, sx * GRILLE_X + fx * FAN_PITCH / 2.0,
                      GRILLE_Y + fy * FAN_PITCH / 2.0, FAN_HOLE_D)
    sk.pocket(doc, bd, s, PANEL_T)

    # The bolts into the joiners below.
    s = sk.sketch(doc, bd, name + "_Sk_bolts",
                  sk.plane(Vector(0, 0, 0), sk.X, sk.Y))
    for hx, hy in joiner_holes():
        if hx * sx > 0:
            sk.circle(s, hx, hy, PANEL_HOLE_D)
    sk.pocket(doc, bd, s, PANEL_T)
    return bd


def joiner(doc, name, y):
    """The rack's post joiner, under the seam with its hole line at y.

    Flat face up against the panel; the nut traps open downward, so the nuts go
    in from below and the bolts come down through the panel into them.
    """
    bd = sk.body(doc, name)
    c, L, W = JOIN_CHAMFER, JOIN_L / 2.0, JOIN_W / 2.0
    ya, yb = -W + JOIN_OFF, W + JOIN_OFF    # the plate, about its hole line
    s = sk.sketch(doc, bd, name + "_Sk_plate",
                  sk.plane(Vector(0, 0, 0), sk.X, sk.Y))
    # Corners on the near side chamfered, as on the rack's own joiner.
    sk.polygon(s, [(-L + c, ya), (L - c, ya), (L, ya + c), (L, yb),
                   (-L, yb), (-L, ya + c)])
    sk.pad(doc, bd, s, JOIN_T, reversed_=True)

    s = sk.sketch(doc, bd, name + "_Sk_holes",
                  sk.plane(Vector(0, 0, 0), sk.X, sk.Y))
    for hx in (-JOIN_PITCH / 2.0, JOIN_PITCH / 2.0):
        sk.circle(s, hx, 0.0, JOIN_HOLE_D)
    sk.pocket(doc, bd, s, JOIN_T)

    s = sk.sketch(doc, bd, name + "_Sk_nuts",
                  sk.plane(Vector(0, 0, -JOIN_T), sk.X, sk.Y))
    for hx in (-JOIN_PITCH / 2.0, JOIN_PITCH / 2.0):
        sk.hexagon(s, hx, 0.0, JOIN_NUT_AF)
    sk.pocket(doc, bd, s, JOIN_T - JOIN_FLOOR)
    bd.Placement = App.Placement(Vector(0, y, 0), App.Rotation())
    return bd
