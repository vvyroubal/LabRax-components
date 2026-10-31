#!/usr/bin/env freecadcmd
"""Build the top cover: its FreeCAD document, STLs and STEP, and check them.

    make cover          # this, then the 3MFs

Writes top-cover/TopCover_LabRax.FCStd and .step, and top-cover/stl/: the two
halves and the joiner, which are this project's own, and -- when
top-cover/assets/Skynet.3mf is there -- the logo's pieces for each half and a
second document with them in, TopCover_Skynet_LabRax.FCStd, which are not and
are ignored by git (see logo.py).
"""

import math
import os
import sys

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

ROOT = os.environ.get("UCG_ROOT") or os.getcwd()
HERE = os.path.join(ROOT, "top-cover")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "common", "src"))

import FreeCAD as App  # noqa: E402
import MeshPart  # noqa: E402
import Part  # noqa: E402
from FreeCAD import Vector  # noqa: E402

import cover as C  # noqa: E402
import logo  # noqa: E402

DOC = "TopCover_LabRax"
LOGO_DOC = "TopCover_Skynet_LabRax"   # the same with the logo; not committed
STL = os.path.join(HERE, "stl")
BED = 180.0
VOID = 1.0

_fails = []
_n = 0


def check(ok, what, detail=""):
    global _n
    _n += 1
    print("  %-4s  %s   %s" % ("ok" if ok else "FAIL", what, detail))
    if not ok:
        _fails.append(what)


def export(shape, name):
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.02,
                                  AngularDeflection=0.25, Relative=False)
    mesh.write(os.path.join(STL, name + ".stl"))


def main():
    os.makedirs(STL, exist_ok=True)
    doc = App.newDocument(DOC)
    halves = {-1: C.half(doc, -1, "cover_l"), 1: C.half(doc, 1, "cover_r")}
    joiners = [C.joiner(doc, "joiner_%d" % (i + 1), y)
               for i, y in enumerate(C.JOIN_Y)]
    doc.recompute()
    # The cover alone first: this document is the project's own.
    doc.saveAs(os.path.join(HERE, DOC + ".FCStd"))

    # Then the logo, into a second document that git ignores.
    pieces, report = {}, None
    if logo.available():
        placed, report = logo.layout()
        for (colour, side), shape in sorted(logo.solids(placed).items()):
            name = "logo_%s_%s" % (colour, "l" if side < 0 else "r")
            o = doc.addObject("Part::Feature", name)
            o.Shape = shape
            o.Visibility = True   # a headless build saves it hidden otherwise
            pieces[name] = shape
        doc.recompute()
        doc.saveAs(os.path.join(HERE, LOGO_DOC + ".FCStd"))

    parts = [halves[-1], halves[1]] + joiners
    Part.export(parts, os.path.join(HERE, DOC + ".step"))
    export(halves[-1].Shape, "cover_l")
    export(halves[1].Shape, "cover_r")
    # One joiner STL, at its own origin, printed twice.
    export(joiners[0].Shape.translated(Vector(0, -C.JOIN_Y[0], 0)), "joiner")
    for name, shape in pieces.items():
        export(shape, name)

    print("\n[parts]")
    for o in parts:
        sh = o.Shape
        check(sh.isValid() and len(sh.Solids) == 1, "%-8s is one valid solid" % o.Name,
              "%d solids, %.1f cm3" % (len(sh.Solids), sh.Volume / 1000))
        b = sh.BoundBox
        check(b.XLength <= BED - 8 and b.YLength <= BED - 8,
              "%-8s fits the A1 mini bed with 4 mm all round" % o.Name,
              "%.1f x %.1f" % (b.XLength, b.YLength))

    L, R = halves[-1].Shape, halves[1].Shape
    print("\n[the cover]")
    w = R.BoundBox.XMax - L.BoundBox.XMin
    check(abs(w - C.PANEL_W) < 1e-6 and abs(L.BoundBox.YLength - C.PANEL_D) < 1e-6,
          "it is the rack's top panel", "%.2f x %.2f x %.1f"
          % (w, L.BoundBox.YLength, L.BoundBox.ZLength))
    check(L.common(R).Volume < VOID and abs(L.BoundBox.XMax - R.BoundBox.XMin) < 1e-6,
          "the halves butt on the centreline", "seam at x = %.3f" % R.BoundBox.XMin)
    for side, sh in ((-1, L), (1, R)):
        cells = len(C.grille_cells(side))
        opening = cells * (C.HEX_AF ** 2 * math.sqrt(3) / 2)
        check(cells > 40, "%s grille: %d cells, %.0f cm2 open, %.0f%% of a 92 mm fan"
              % ("left " if side < 0 else "right", cells, opening / 100,
                 100 * opening / (math.pi * (C.GRILLE_D / 2) ** 2)))

    print("\n[the joiners]")
    for jn, y in zip(joiners, C.JOIN_Y):
        b = jn.Shape.BoundBox
        check(-C.CLEAR_HD <= b.YMin and b.YMax <= C.CLEAR_HD,
              "%s is inside the clear run under the seam" % jn.Name,
              "y %.1f .. %.1f of +/-%.0f" % (b.YMin, b.YMax, C.CLEAR_HD))
        check(b.ZMax <= 1e-6 and jn.Shape.common(L.fuse(R)).Volume < VOID,
              "%s sits under the panel without fouling it" % jn.Name)
        for hx in (-C.JOIN_PITCH / 2, C.JOIN_PITCH / 2):
            # A 6 mm bolt down through panel and joiner floor, clear all the way.
            bolt = Part.makeCylinder(2.9, C.PANEL_T + C.JOIN_T + 2,
                                     Vector(hx, y, -C.JOIN_T - 1))
            hit = bolt.common(L.fuse(R).fuse(jn.Shape)).Volume
            check(hit < VOID, "an M6 goes straight through at x=%+.0f y=%.0f"
                  % (hx, y), "%.2f mm3 in the way" % hit)
            # And its nut sits in a trap, under the floor, that holds it.
            nut = Part.makeCylinder(C.JOIN_NUT_AF / 2 - 0.05, 4.9,
                                    Vector(hx, y, -C.JOIN_T))
            hit = nut.common(jn.Shape).Volume
            check(hit < VOID, "  and its nut fits the trap", "%.2f mm3" % hit)
        # The grille stays clear of the joiner and the heads on top.
        # Solid, that is, but for the two bolt holes.
        foot = Part.makeBox(C.JOIN_L, C.JOIN_W, C.PANEL_T,
                            Vector(-C.JOIN_L / 2, y - C.JOIN_W / 2 + C.JOIN_OFF, 0))
        holes = 2 * math.pi * (C.PANEL_HOLE_D / 2) ** 2 * C.PANEL_T
        solid = foot.common(L.fuse(R)).Volume / (foot.Volume - holes)
        check(solid > 0.999, "the panel is solid over %s but for its bolts"
              % jn.Name, "%.1f%% of the rest of its footprint" % (100 * solid))

    if report:
        print("\n[the logo]")
        print("  scale %.3f, %.1f x %.1f mm, %d pieces kept, %d too thin left out"
              % (report["scale"], report["size"][0], report["size"][1],
                 report["kept"], report["dropped"]))
        check(report["thinnest"] >= C.MIN_STROKE, "every line is printable",
              "thinnest %.2f mm, nozzle 0.4" % report["thinnest"])
        allp = Part.makeCompound(list(pieces.values()))
        b = allp.BoundBox
        check(C.LOGO_Y0 - 1e-6 <= b.YMin and b.YMax <= C.LOGO_Y1 + 1e-6
              and -C.LOGO_X1 <= b.XMin and b.XMax <= C.LOGO_X1,
              "it stays in its band, clear of grilles and grooves",
              "x %.1f..%.1f y %.1f..%.1f" % (b.XMin, b.XMax, b.YMin, b.YMax))
        check(abs(b.ZMin - C.PANEL_T) < 1e-3 and abs(b.ZMax - C.PANEL_T - C.LOGO_H) < 1e-3,
              "it stands %.1f mm proud of the panel" % C.LOGO_H)
        for name, sh in pieces.items():
            side = L if name.endswith("_l") else R
            under = sh.translated(Vector(0, 0, -0.3)).common(side).Volume
            check(under > 0, "%s rests on its own half" % name,
                  "%d pieces" % len(sh.Solids))
    else:
        print("\n  (no top-cover/assets/Skynet.3mf: built without the logo)")

    print("\n%d checks, %d failed" % (_n, len(_fails)))
    for f in _fails:
        print("  FAIL %s" % f)
    sys.stdout.flush()
    return 1 if _fails else 0


try:
    rc = main()
except Exception:
    import traceback
    traceback.print_exc()
    print("\nbuild CRASHED")
    rc = 1
sys.stdout.flush()
os._exit(rc)
