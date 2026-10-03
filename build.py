#!/usr/bin/env freecadcmd
"""Build the bracket: common/cad/UCG_Fiber_LabRax.FCStd plus STL and STEP.

The chassis STLs go to common/stl, each device's to its own folder's stl/.
Each device's folder also gets a document and a STEP of its own, holding the
chassis and that device's three parts -- the same split its 3MF makes.

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
sys.path.insert(0, os.path.join(ROOT, "common", "src"))

import FreeCAD as App  # noqa: E402
import Mesh  # noqa: E402,F401
import MeshPart  # noqa: E402
import Part  # noqa: E402

import params as P  # noqa: E402
import model  # noqa: E402
import devices  # noqa: E402

DOC = "UCG_Fiber_LabRax"

# Four shared, then three per device. Listed this way so adding a device's
# folder is the whole change -- nothing here has to be edited with it.
PARTS = devices.CHASSIS + tuple(p for d in devices.ALL for p in d.parts)


def bad_solids(bodies, names):
    return [n for n in names
            if not bodies[n].Shape.isValid() or len(bodies[n].Shape.Solids) != 1]


def one_device(dev):
    """The chassis and one device's three parts, saved in that device's folder.

    Built afresh rather than copied out of the big document, so each body
    keeps the sketches, pads and pockets it is made of.
    """
    names = devices.CHASSIS + dev.parts
    doc = App.newDocument(dev.doc)
    bodies = model.build(doc, only=dev)
    doc.recompute()

    bad = bad_solids(bodies, names)
    if bad:
        print("NOT A SINGLE VALID SOLID in %s: %s" % (dev.doc, ", ".join(bad)))

    doc.saveAs(dev.cad_path)
    Part.export([bodies[n] for n in names], dev.step_path)
    App.closeDocument(doc.Name)


def main():
    for sub in ("cad", "stl", "step"):
        os.makedirs(os.path.join(devices.COMMON, sub), exist_ok=True)
    for dev in devices.ALL:
        os.makedirs(dev.stl_dir, exist_ok=True)

    doc = App.newDocument(DOC)
    bodies = model.build(doc)
    # Two short lengths of the runner, to try its fit on before a side is
    # printed. They are not part of any kit, so they are not plated.
    coupons = model.coupons(doc)
    bodies.update(coupons)
    doc.recompute()

    bad = bad_solids(bodies, PARTS + tuple(coupons))
    if bad:
        print("NOT A SINGLE VALID SOLID: %s" % ", ".join(bad))

    doc.saveAs(os.path.join(devices.COMMON, "cad", DOC + ".FCStd"))

    for name in PARTS:
        mesh = MeshPart.meshFromShape(Shape=bodies[name].Shape,
                                      LinearDeflection=0.02,
                                      AngularDeflection=0.25, Relative=False)
        mesh.write(devices.stl_path(name))
    for name in coupons:
        mesh = MeshPart.meshFromShape(Shape=bodies[name].Shape,
                                      LinearDeflection=0.02,
                                      AngularDeflection=0.25, Relative=False)
        mesh.write(os.path.join(devices.COMMON, "stl", name + ".stl"))
    Part.export([bodies[n] for n in PARTS],
                os.path.join(devices.COMMON, "step", DOC + ".step"))

    for dev in devices.ALL:
        one_device(dev)

    print("\n%-16s %-34s %12s %8s" % ("part", "bounding box (mm)",
                                       "volume (cm3)", "features"))
    total = 0.0
    for name in PARTS:
        sh = bodies[name].Shape
        b = sh.BoundBox
        total += sh.Volume
        print("%-16s %8.2f x %8.2f x %8.2f  %12.1f %8d"
              % (name, b.XLength, b.YLength, b.ZLength, sh.Volume / 1000.0,
                 len(bodies[name].Group)))
    print("%-16s %36s %12.1f" % ("total", "", total / 1000.0))
    print("\nrack: %.2f wide x %.2f high, posts %.1f apart front to back"
          % (P.FACE_W, P.RACK_U, P.RACK_D))
    sys.stdout.flush()


main()
