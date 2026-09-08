#!/usr/bin/env freecadcmd
"""Build the bracket: writes cad/UCG_Fiber_LabRax.FCStd plus STL and STEP.

Run through the Makefile, which knows how to reach FreeCAD:

    make            # model + exports
    make verify     # check the result against the rack and the device
"""

import os
import sys

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
# Printed as they are modelled: floor down, faceplate standing at the front.
PARTS = ("tray", "top_bar", "ear_l", "ear_r")


def main():
    for sub in ("cad", "export/stl", "export/step"):
        os.makedirs(os.path.join(ROOT, sub), exist_ok=True)

    parts = model.build_parts()

    doc = App.newDocument(DOC)
    objs = []
    for name in PARTS:
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = parts[name]
        objs.append(obj)
    doc.recompute()
    doc.saveAs(os.path.join(ROOT, "cad", DOC + ".FCStd"))

    for name in PARTS:
        # Meshed explicitly rather than via Shape.exportStl, which writes ASCII
        # and gives no control over how finely the slot ends are faceted.
        mesh = MeshPart.meshFromShape(Shape=parts[name],
                                      LinearDeflection=0.02,
                                      AngularDeflection=0.25,
                                      Relative=False)
        mesh.write(os.path.join(ROOT, "export", "stl", name + ".stl"))
    Part.export(objs, os.path.join(ROOT, "export", "step", DOC + ".step"))

    print("\n%-8s %-34s %12s" % ("part", "bounding box (mm)", "volume (cm3)"))
    total = 0.0
    for name in PARTS:
        s = parts[name]
        b = s.BoundBox
        total += s.Volume
        print("%-8s %8.2f x %8.2f x %8.2f  %12.1f"
              % (name, b.XLength, b.YLength, b.ZLength, s.Volume / 1000.0))
    print("%-8s %36s %12.1f" % ("total", "", total / 1000.0))
    print("\nrack envelope: %.2f wide x %.2f high, %.1f deep behind the posts"
          % (P.FACE_W, P.RACK_U, P.BODY_D))


main()
