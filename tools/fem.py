#!/usr/bin/env freecadcmd
"""Stress the tray's bolt tab, the way tightening the joint screw does.

The tabs snapped off both tray halves when their M6 was tightened. This puts
a load on the bolt and asks CalculiX what the part does about it.

    make fem

Each analysis is saved as its own document, cad/fem_<part>.FCStd, so it can
be opened and looked at: the mesh, the constraints, the material and the
result colour map are all in there. It has to be a separate file -- build.py
rewrites cad/UCG_Fiber_LabRax.FCStd from the script on every make, so an
analysis living in that document would not survive the next build.

Only the rear of each tray is modelled -- everything behind Y = CUT -- with
that cut face held fixed. It is far enough from the tab for the boundary not
to matter, and it keeps the mesh small enough to solve in a minute.

The load is applied where the fastener actually pushes: on the counterbore
floor in the left half, where the screw head bears, and on the near wall of
the nut slot in the right half, where the nut bears. Stress is linear in the
load, so one run at LOAD newtons gives the preload the part can take:

    allowable = LOAD x yield / peak von Mises
"""

import os
import shutil
import sys

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

ROOT = os.environ.get("UCG_ROOT")
if not ROOT:
    try:
        ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "src"))

import FreeCAD as App  # noqa: E402
import Part  # noqa: E402
from FreeCAD import Vector  # noqa: E402
import ObjectsFem  # noqa: E402
from femmesh.gmshtools import GmshTools  # noqa: E402
import femtools.ccxtools as ccxtools  # noqa: E402

import params as P  # noqa: E402
import model  # noqa: E402

LOAD = 100.0        # N of bolt preload, applied for the run
YIELD = 50.0        # MPa, PETG in tension -- the number to beat
CUT = 105.0         # mm, everything behind this is modelled
ELEM = 1.5          # mm, characteristic element size


def planar_faces(shape, normal_axis, coord, inside, tol=0.05):
    """Names of the flat faces normal to `normal_axis`, sitting at `coord`
    along it, with their centres inside the box `inside`.

    Faces are found by where they are, not by index: "Face21" means whatever
    the modeller numbered last.
    """
    k = {"x": 0, "y": 1, "z": 2}[normal_axis]
    out = []
    for i, f in enumerate(shape.Faces, start=1):
        if not isinstance(f.Surface, Part.Plane):
            continue
        n = f.Surface.Axis
        if abs(abs((n.x, n.y, n.z)[k]) - 1.0) > 1e-6:
            continue
        c = f.CenterOfMass
        if abs((c.x, c.y, c.z)[k] - coord) > tol:
            continue
        (x0, x1), (y0, y1), (z0, z1) = inside
        if x0 <= c.x <= x1 and y0 <= c.y <= y1 and z0 <= c.z <= z1:
            out.append((f.Area, "Face%d" % i))
    out.sort(reverse=True)
    return [n for _, n in out]


def run(name, sx):
    doc = App.newDocument("fem_" + name)
    parts = model.build(doc)
    doc.recompute()
    whole = parts[name].Shape
    rear = whole.common(Part.makeBox(400, 400, 100, Vector(-200, CUT, -20)))

    obj = doc.addObject("Part::Feature", name + "_rear")
    obj.Shape = rear

    ana = ObjectsFem.makeAnalysis(doc, "Analysis")
    sol = ObjectsFem.makeSolverCalculiXCcxTools(doc, "Solver")
    sol.AnalysisType = "static"
    sol.GeometricalNonlinearity = "linear"
    ana.addObject(sol)

    mat = ObjectsFem.makeMaterialSolid(doc, "PETG")
    m = mat.Material
    m["Name"] = "PETG"
    m["YoungsModulus"] = "2000 MPa"
    m["PoissonRatio"] = "0.38"
    m["Density"] = "1270 kg/m^3"
    mat.Material = m
    ana.addObject(mat)

    big = ((-200, 200), (-200, 400), (-50, 60))
    cut_faces = planar_faces(rear, "y", CUT, big)
    fixed = ObjectsFem.makeConstraintFixed(doc, "Fixed")
    fixed.References = [(obj, f) for f in cut_faces]
    ana.addObject(fixed)
    print("  held: %d face(s) on the cut at Y=%.0f" % (len(cut_faces), CUT))

    # Where the fastener bears, and which way it pushes this half.
    if sx < 0:
        x_at = -P.TAB_HX + P.TRAY_CB_D      # counterbore floor, screw head
        push = 1.0
    else:
        x_at = 2.0                          # near wall of the nut slot
        push = -1.0
    near = ((-P.TAB_HX - 1, P.TAB_HX + 1),
            (P.TRAY_BOLT_Y[0] - 12, P.TRAY_BOLT_Y[1] + 12),
            (-1, P.TAB_Z1 + 1))
    load_faces = planar_faces(rear, "x", x_at, near)
    if not load_faces:
        print("  found no face for the fastener to bear on")
        return None
    print("  loaded: %d bearing face(s) at x=%.1f" % (len(load_faces), x_at))

    frc = ObjectsFem.makeConstraintForce(doc, "Preload")
    frc.References = [(obj, f) for f in load_faces]
    # Total across both bolts, so LOAD is the preload in one of them. The
    # unit matters: a bare number here is millinewtons, not newtons.
    frc.Force = "%s N" % (LOAD * len(load_faces))
    # The direction comes from the bearing face itself, whose normal points
    # out of the material; the fastener pushes the other way.
    frc.Direction = (obj, load_faces[:1])
    frc.Reversed = (push > 0) == (x_at < 0)
    ana.addObject(frc)

    msh = ObjectsFem.makeMeshGmsh(doc, name + "_mesh")
    msh.Shape = obj
    msh.CharacteristicLengthMax = "%s mm" % ELEM
    msh.CharacteristicLengthMin = "%s mm" % (ELEM / 3.0)
    msh.ElementOrder = "2nd"
    ana.addObject(msh)
    gm = GmshTools(msh)
    err = gm.create_mesh()
    if err:
        print("  mesh: %s" % err)
    print("  mesh: %d nodes, %d volume elements"
          % (msh.FemMesh.NodeCount, msh.FemMesh.VolumeCount))

    work = os.path.join(ROOT, ".fem-%s" % name)
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    fea = ccxtools.FemToolsCcx(ana, sol)
    fea.update_objects()
    fea.setup_working_dir(work)
    fea.setup_ccx()
    msg = fea.check_prerequisites()
    if msg:
        print("  prerequisites: %s" % msg)
        return None
    fea.purge_results()
    fea.write_inp_file()
    fea.ccx_run()
    fea.load_results()

    res = [o for o in doc.Objects if o.isDerivedFrom("Fem::FemResultObject")]
    if not res:
        print("  no result came back")
        return None
    r = res[0]
    print("  applied %s, worst deflection %.3f mm"
          % (frc.Force, max(r.DisplacementLengths)))
    vm = r.vonMises
    peak = max(vm)
    i = list(vm).index(peak)
    node = r.Mesh.FemMesh.Nodes[r.NodeNumbers[i]]

    # Save it, so there is something to open and look at.
    out = os.path.join(ROOT, "cad", "fem_%s.FCStd" % name)
    doc.saveAs(out)
    print("  saved %s (%.1f MB)"
          % (os.path.relpath(out, ROOT), os.path.getsize(out) / 1e6))

    shutil.rmtree(work, ignore_errors=True)
    return peak, (node.x, node.y, node.z), msh.FemMesh.NodeCount


def main():
    print("Tray bolt tab under %.0f N of preload, PETG at %.0f MPa\n"
          % (LOAD, YIELD))
    for name, sx in (("tray_l", -1), ("tray_r", 1)):
        print("%s:" % name)
        out = run(name, sx)
        if not out:
            continue
        peak, at, n = out
        allow = LOAD * YIELD / peak
        print("  peak von Mises %.1f MPa at (%.1f, %.1f, %.1f)"
              % (peak, at[0], at[1], at[2]))
        print("  yields at about %.0f N of preload" % allow)
        print("  an M6 at 2 N-m develops about 1700 N -> %.0fx over\n"
              % (1700.0 / allow))


main()
