#!/usr/bin/env python3
"""Plate the exported STLs into a Bambu Studio 3MF for the A1 mini.

The bracket needs two plates: the tray fills a 180 mm bed almost exactly on
its own, and everything else goes on the second.

    python3 tools/plate.py        # writes export/3mf/UCG_Fiber_LabRax-A1mini.3mf

Bambu Studio lays its plates out along one global axis, spaced at 1.2 times
the bed size -- 216 mm for the A1 mini's 180 mm bed. That factor is what the
stock Lab Rax rack project uses on a 180 mm bed, and what Bambu Studio itself
writes on its 200 mm default bed (240 mm). Meshes are centred on their own
origin and the transform carries the placement, which is Bambu Studio's own
convention.

Note that `bambu-studio --export-3mf` re-arranges everything on load whatever
the input says, so it cannot be used to check that the placement survives; it
is still worth running `--slice 0` over the result, which is what proves the
plates are well formed and printable.
"""

import os
import re
import struct
import sys
import zipfile

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STL = os.path.join(ROOT, "export", "stl")
OUT = os.path.join(ROOT, "export", "3mf", "UCG_Fiber_LabRax-A1mini.3mf")

BED = 180.0           # A1 mini, and there are no excluded areas on it
PLATE_STRIDE = BED * 1.2  # Bambu Studio's plate spacing; see the note above
MARGIN = 3.0          # smallest gap to the bed edge we will accept

# Each entry: part, (in-plate centre x, y), rotations baked into the mesh as
# (axis, degrees) applied in order, and any per-object slicer settings.
#
# The ears need support. Above the faceplate window there is nothing to build
# on, so the top rail starts as a 200 mm2 ledge hanging in mid-air at z = 34,
# reaching 32 mm inboard from the only full-height part of the faceplate. The
# support column stands inside the window opening and lifts straight out.
SUPPORT = {"enable_support": "1", "support_type": "normal(auto)"}

PLATES = [
    ("Tray", [
        ("tray", (90.0, 90.0), [], {}),
    ]),
    ("Ears, top bar and stops", [
        # The ears turn 90 degrees in plan; they still print floor-down.
        ("ear_l", (90.0, 32.5), [("z", 90)], SUPPORT),
        ("ear_r", (90.0, 92.5), [("z", 90)], SUPPORT),
        ("top_bar", (90.0, 136.0), [], {}),
        # Laid on their backs: the upright's load is then across the layers
        # rather than trying to peel them apart.
        ("stop_l", (78.0, 156.5), [("x", -90), ("z", 90)], {}),
        ("stop_r", (104.0, 156.5), [("x", -90), ("z", 90)], {}),
    ]),
]


def load_stl(path):
    data = open(path, "rb").read()
    if data[:5].lower() == b"solid" and b"facet" in data[:2000]:
        vs = re.findall(rb"vertex\s+(\S+)\s+(\S+)\s+(\S+)", data)
        V = np.array(vs, dtype=float)
    else:
        n = struct.unpack("<I", data[80:84])[0]
        arr = np.frombuffer(data, dtype=np.uint8, count=n * 50, offset=84)
        V = arr.reshape(n, 50)[:, 12:48].copy().view("<f4").reshape(-1, 3)
        V = V.astype(float)
    uniq, inv = np.unique(np.round(V, 5), axis=0, return_inverse=True)
    return uniq, inv.reshape(-1, 3)


def rotate(V, ops):
    for axis, deg in ops:
        a = np.radians(deg)
        c, s = np.cos(a), np.sin(a)
        if axis == "x":
            M = np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
        elif axis == "y":
            M = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
        else:
            M = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        V = V @ M.T
    return V


def plate_origin(index):
    """Bottom-left of plate `index` (1-based) in Bambu's global layout.

    Kept to a single row: the spacing between rows is a different number and
    we have never needed more than a handful of plates.
    """
    return (index - 1) * PLATE_STRIDE, 0.0


def build():
    objects, items, cfg_objects, cfg_plates = [], [], [], []
    report, problems = [], []
    oid = 1

    for pindex, (pname, parts) in enumerate(PLATES, start=1):
        ox, oy = plate_origin(pindex)
        instances = []
        for name, (cx, cy), ops, opts in parts:
            path = os.path.join(STL, name + ".stl")
            if not os.path.exists(path):
                problems.append("%s: no STL, run make first" % name)
                continue
            V, T = load_stl(path)
            V = rotate(V, ops)
            lo, hi = V.min(0), V.max(0)
            size = hi - lo
            # Centre the mesh on its own origin, as Bambu Studio does.
            V = V - (lo + hi) / 2.0

            x0, x1 = cx - size[0] / 2, cx + size[0] / 2
            y0, y1 = cy - size[1] / 2, cy + size[1] / 2
            if x0 < MARGIN or y0 < MARGIN or x1 > BED - MARGIN or y1 > BED - MARGIN:
                problems.append("%s runs off plate %d: x %.1f..%.1f y %.1f..%.1f"
                                % (name, pindex, x0, x1, y0, y1))

            verts = "".join('<vertex x="%.5f" y="%.5f" z="%.5f"/>' % tuple(v)
                            for v in V)
            tris = "".join('<triangle v1="%d" v2="%d" v3="%d"/>' % tuple(t)
                           for t in T)
            objects.append('<object id="%d" type="model"><mesh>'
                           "<vertices>%s</vertices><triangles>%s</triangles>"
                           "</mesh></object>" % (oid, verts, tris))
            items.append('<item objectid="%d" transform="1 0 0 0 1 0 0 0 1 '
                         '%.5f %.5f %.5f" printable="1"/>'
                         % (oid, ox + cx, oy + cy, size[2] / 2.0))
            extra = "".join('    <metadata key="%s" value="%s"/>\n' % kv
                            for kv in sorted(opts.items()))
            cfg_objects.append(
                ('  <object id="%d">\n'
                 '    <metadata key="name" value="%s.stl"/>\n'
                 '    <metadata key="extruder" value="1"/>\n'
                 % (oid, name))
                + extra +
                ('    <part id="%d" subtype="normal_part">\n'
                 '      <metadata key="name" value="%s"/>\n'
                 '      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 '
                 '0 0 0 1"/>\n'
                 '      <mesh_stat face_count="%d" edges_fixed="0" '
                 'degenerate_facets="0" facets_removed="0" '
                 'facets_reversed="0" backwards_edges="0"/>\n'
                 '    </part>\n'
                 '  </object>' % (oid, name, len(T))))
            instances.append('    <model_instance>\n'
                             '      <metadata key="object_id" value="%d"/>\n'
                             '      <metadata key="instance_id" value="0"/>\n'
                             '    </model_instance>' % oid)
            report.append((pindex, name, size, (x0, x1), (y0, y1), len(T),
                           bool(opts)))
            oid += 1

        cfg_plates.append('  <plate>\n'
                          '    <metadata key="plater_id" value="%d"/>\n'
                          '    <metadata key="plater_name" value="%s"/>\n'
                          '    <metadata key="locked" value="false"/>\n'
                          '%s\n  </plate>' % (pindex, pname,
                                              "\n".join(instances)))

    model = ('<?xml version="1.0" encoding="UTF-8"?>\n'
             '<model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n'
             ' <metadata name="Application">UCG_Fiber tools/plate.py</metadata>\n'
             ' <resources>%s</resources>\n'
             ' <build>%s</build>\n'
             '</model>\n' % ("".join(objects), "".join(items)))

    settings = ('<?xml version="1.0" encoding="UTF-8"?>\n<config>\n%s\n%s\n'
                '</config>\n' % ("\n".join(cfg_objects), "\n".join(cfg_plates)))

    ctypes = ('<?xml version="1.0" encoding="UTF-8"?>\n'
              '<Types xmlns="http://schemas.openxmlformats.org/package/2006/'
              'content-types">\n'
              ' <Default Extension="rels" ContentType="application/vnd.'
              'openxmlformats-package.relationships+xml"/>\n'
              ' <Default Extension="model" ContentType="application/vnd.'
              'ms-package.3dmanufacturing-3dmodel+xml"/>\n</Types>\n')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/'
            '2006/relationships">\n'
            ' <Relationship Target="/3D/3dmodel.model" Id="rel-1" '
            'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/'
            '3dmodel"/>\n</Relationships>\n')

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr("[Content_Types].xml", ctypes)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model)
        z.writestr("Metadata/model_settings.config", settings)

    print("%s  (%.0f kB)" % (os.path.relpath(OUT, ROOT),
                             os.path.getsize(OUT) / 1024.0))
    print("\n%-6s %-8s %-22s %-16s %-16s %-6s %s"
          % ("plate", "part", "size (mm)", "x on bed", "y on bed", "tris",
             "support"))
    for pi, name, size, xs, ys, nt, sup in report:
        print("%-6d %-8s %6.1f x %5.1f x %5.1f  %6.1f .. %6.1f  %6.1f .. %6.1f  "
              "%-6d %s" % (pi, name, size[0], size[1], size[2], xs[0], xs[1],
                           ys[0], ys[1], nt, "yes" if sup else "-"))
    if problems:
        print("\nPROBLEMS:")
        for p in problems:
            print("  " + p)
        return 1
    print("\nbed %.0f x %.0f, everything at least %.1f mm from the edge"
          % (BED, BED, MARGIN))
    return 0


if __name__ == "__main__":
    sys.exit(build())
