#!/usr/bin/env python3
"""Plate the exported STLs into a Bambu Studio 3MF for the A1 mini.

The bracket needs two plates: the tray fills a 180 mm bed almost exactly on
its own, and everything else goes on the second.

    python3 tools/plate.py        # writes export/3mf/UCG_Fiber_LabRax-A1mini.3mf

Meshes are centred on their own origin and the build transform carries the
placement, which is Bambu Studio's own convention. See plate_origin() for how
the plates are laid out in that global space.

Note that `bambu-studio --export-3mf` re-arranges everything on load whatever
the input says, so it cannot be used to check that the placement survives; it
is still worth running `--slice 0` over the result, which is what proves the
plates are well formed and printable.
"""

import json
import os
import re
import struct
import sys
import zipfile

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STL = os.path.join(ROOT, "export", "stl")
OUT = os.path.join(ROOT, "export", "3mf", "UCG_Fiber_LabRax-A1mini.3mf")
# A complete A1 mini configuration, lifted from the stock Lab Rax rack project.
# Without a valid one of these Bambu Studio refuses the whole config -- "The
# 3mf file has invalid config, load geometry data only" -- and throws away the
# plates and the per-object settings along with it.
PROJECT_SETTINGS = os.path.join(ROOT, "tools", "a1mini_project.json")

BED = 180.0           # A1 mini, and there are no excluded areas on it
PLATE_STRIDE = 216.0  # see plate_origin()
# The stock A1 mini process puts a 5 mm brim on, and the brim has to land on
# the bed too, so parts want ~6 mm of clearance. The tray and the top bar are
# 172 mm wide and can only ever have 4 mm, which Bambu Studio accepts; nothing
# else is allowed closer than this.
MARGIN = 4.0
# Parts get a 5 mm brim each, and two brims that run into one another make
# Bambu Studio report "G-code conflicts detected after slicing".
GAP = 12.0

# Each entry: part, (in-plate centre x, y), rotations baked into the mesh as
# (axis, degrees) applied in order, and any per-object slicer settings.
#
# The ears need support. Above the faceplate window there is nothing to build
# on, so the top rail starts as a ledge hanging in mid-air at z = 34, reaching
# inboard from the only full-height part of the faceplate. The support column
# stands inside the window opening and lifts straight out.
SUPPORT = {"enable_support": "1", "support_type": "normal(auto)"}

PLATES = [
    # A side is 192 mm long, so it only goes on the bed turned 45 degrees.
    ("Left side", [("side_l", (90.0, 90.0), [("z", 45)], SUPPORT)]),
    ("Right side", [("side_r", (90.0, 90.0), [("z", 45)], SUPPORT)]),
    # A tray half leaves a strip down one side, which is where its top bar
    # goes, stood on end.
    ("Left tray and top bar", [
        # The lap strip along each edge stands 3 mm off the bed, so the tray
        # wants support under its rim. It comes away from the underside.
        ("tray_l", (66.0, 90.0), [], SUPPORT),
        ("top_bar_l", (153.0, 90.0), [("x", 180), ("z", 90)], {}),
    ]),
    ("Right tray and top bar", [
        ("tray_r", (66.0, 90.0), [], SUPPORT),
        ("top_bar_r", (153.0, 90.0), [("x", 180), ("z", 90)], {}),
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


PLATES_PER_ROW = 2


def plate_origin(index):
    """Bottom-left of plate `index` (1-based) in Bambu Studio's global layout.

    Plates sit on a grid, two to a row, stepping +250 mm across a row and
    -250 mm down to the next. Both numbers were read back out of Bambu Studio
    itself: load a file, let it arrange, export, and see where it put things.

    Getting this wrong fails in two different ways, neither of which mentions
    coordinates. Land outside the grid entirely and the plate comes back empty
    -- "one of the plate is empty or has no object fully inside it". Land near
    enough that the parts are assigned to the right plate but not exactly on
    it, and they are placed relative to the wrong origin -- "some objects are
    located over the boundary of the heated bed".
    """
    col = (index - 1) % PLATES_PER_ROW
    row = (index - 1) // PLATES_PER_ROW
    return col * PLATE_STRIDE, -row * PLATE_STRIDE


def _single_filament(cfg, keep=2):
    """Cut the project down to one filament -- the PETG slot.

    The profile arrives with the A1 mini's five slots. With more than one,
    Bambu Studio plants a wipe tower on every plate, and on a plate packed
    this tightly it lands on top of a part: "G-code conflicts detected after
    slicing". This is a single-material print, so the other four go.

    Anything that is a list as long as the filament count is per-filament;
    a few keys hold n^2 or k*n entries and are cut to match. The prime tower
    is switched off with them.
    """
    n = len(cfg.get("filament_type", []))
    if n <= 1:
        return cfg
    out = {}
    for k, v in cfg.items():
        if isinstance(v, list) and len(v) == n:
            out[k] = [v[keep]]
        elif isinstance(v, list) and len(v) == n * n:      # flush matrix
            out[k] = [v[keep * n + keep]]
        elif isinstance(v, list) and len(v) and len(v) % n == 0 and len(v) != n:
            per = len(v) // n
            out[k] = v[keep * per:(keep + 1) * per]
        else:
            out[k] = v
    # With one filament there is nothing to purge, and the tower's parked
    # position (15, 141) sits on top of a part.
    out["enable_prime_tower"] = "0"
    return out


def build():
    objects, items, cfg_objects, cfg_plates = [], [], [], []
    report, problems = [], []
    oid = 1

    for pindex, (pname, parts) in enumerate(PLATES, start=1):
        ox, oy = plate_origin(pindex)
        instances = []
        placed = []   # (name, x0, x1, y0, y1) already put on this plate
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
            for oname, ox0, ox1, oy0, oy1 in placed:
                if (x0 - GAP < ox1 and ox0 - GAP < x1
                        and y0 - GAP < oy1 and oy0 - GAP < y1):
                    problems.append("%s is within %.0f mm of %s on plate %d"
                                    % (name, GAP, oname, pindex))
            placed.append((name, x0, x1, y0, y1))
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
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
             'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021">\n'
             ' <metadata name="Application">BambuStudio-02.08.02.61</metadata>\n'
             ' <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
             ' <metadata name="Title">UCG-Fiber Lab Rax bracket</metadata>\n'
             ' <metadata name="Designer"></metadata>\n'
             ' <metadata name="Description">1U bracket, plated for an A1 mini'
             '</metadata>\n'
             ' <metadata name="CreationDate">2026-09-08</metadata>\n'
             ' <metadata name="ModificationDate">2026-09-08</metadata>\n'
             ' <metadata name="Copyright"></metadata>\n'
             ' <metadata name="LicenseTerms"></metadata>\n'
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

    project = json.dumps(_single_filament(json.load(open(PROJECT_SETTINGS))),
                         indent=1)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, body in (("[Content_Types].xml", ctypes),
                           ("_rels/.rels", rels),
                           ("3D/3dmodel.model", model),
                           ("Metadata/project_settings.config", project),
                           ("Metadata/model_settings.config", settings)):
            # A fixed timestamp keeps rebuilds byte-identical, so an unchanged
            # model does not show up as a modified file.
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, body)

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
