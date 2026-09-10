#!/usr/bin/env freecadcmd
"""Build the bracket: cad/UCG_Fiber_LabRax.FCStd plus STL and STEP.

Each part is a PartDesign Body made of sketches with pads and pockets, so the
document opens as something you can edit feature by feature.

    make            # model + exports
    make verify     # check it against the rack and the device
"""

import os
import sys

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

ROOT = os.environ.get("UCG_ROOT")
if not ROOT:
    try:
        ROOT = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "src"))

import FreeCAD as App  # noqa: E402
import Mesh  # noqa: E402,F401
import MeshPart  # noqa: E402
import Part  # noqa: E402

import params as P  # noqa: E402
import model  # noqa: E402

DOC = "UCG_Fiber_LabRax"
PARTS = ("side_l", "side_r", "leg_l", "leg_r", "tray_l", "tray_r", "top_bar")


def main():
    for sub in ("cad", "export/stl", "export/step"):
        os.makedirs(os.path.join(ROOT, sub), exist_ok=True)

    doc = App.newDocument(DOC)
    bodies = model.build(doc)
    doc.recompute()

    bad = [n for n in PARTS
           if not bodies[n].Shape.isValid() or len(bodies[n].Shape.Solids) != 1]
    if bad:
        print("NOT A SINGLE VALID SOLID: %s" % ", ".join(bad))

    doc.saveAs(os.path.join(ROOT, "cad", DOC + ".FCStd"))

    for name in PARTS:
        mesh = MeshPart.meshFromShape(Shape=bodies[name].Shape,
                                      LinearDeflection=0.02,
                                      AngularDeflection=0.25, Relative=False)
        mesh.write(os.path.join(ROOT, "export", "stl", name + ".stl"))
    Part.export([bodies[n] for n in PARTS],
                os.path.join(ROOT, "export", "step", DOC + ".step"))

    print("\n%-10s %-34s %12s %8s" % ("part", "bounding box (mm)",
                                      "volume (cm3)", "features"))
    total = 0.0
    for name in PARTS:
        sh = bodies[name].Shape
        b = sh.BoundBox
        total += sh.Volume
        print("%-10s %8.2f x %8.2f x %8.2f  %12.1f %8d"
              % (name, b.XLength, b.YLength, b.ZLength, sh.Volume / 1000.0,
                 len(bodies[name].Group)))
    print("%-10s %36s %12.1f" % ("total", "", total / 1000.0))
    print("\nrack: %.2f wide x %.2f high, posts %.1f apart front to back"
          % (P.FACE_W, P.RACK_U, P.RACK_D))
    sys.stdout.flush()


main()
