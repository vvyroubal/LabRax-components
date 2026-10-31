#!/usr/bin/env python3
"""Plate the top cover for the A1 mini: two 3MFs, two plates each.

    python3 top-cover/plate_cover.py

Each plate is one half of the cover and one joiner. Two files:

  TopCover_LabRax-A1mini.3mf         the cover alone, in one filament, PETG
                                     as the rest of the rack
  TopCover_Skynet_LabRax-A1mini.3mf  the same, with the logo's pieces as
                                     parts of each half on filaments 2 and 3.
                                     Built only when the logo's asset is
                                     there, and ignored by git: see logo.py

The halves print as they sit, top up, which puts the logo on the top layers;
the joiners print flat face down, so the nut traps open upward and need no
support. Everything else -- the bed, the margins, the plate grid, the A1 mini
profile -- is common/tools/plate.py's.
"""

import json
import os
import sys
import zipfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "common", "tools"))
import plate as P  # noqa: E402

STL = os.path.join(HERE, "stl")
TITLE = "Lab Rax 10 inch rack top cover"
FLAT = {"enable_support": "0", "brim_type": "no_brim"}
# The logo project's own three colours: its backdrop, white and red.
COLOURS = ["#353535", "#FFFFFF", "#EF5051"]


def plates(with_logo):
    """[(plate name, [(object name, (cx, cy), rotations, opts, parts)])], where
    parts is [(stl name, extruder)] and the first part names the object."""
    out = []
    for i, side in enumerate(("l", "r"), start=1):
        cover = [("cover_" + side, 1)]
        if with_logo:
            cover += [("logo_white_" + side, 2), ("logo_red_" + side, 3)]
        out.append(("Top cover %d of 2 - %s half and a joiner"
                    % (i, "left" if side == "l" else "right"), [
                        ("cover_" + side, (62.0, 90.0), [], FLAT, cover),
                        ("joiner", (151.5, 90.0), [("x", 180)], FLAT,
                         [("joiner", 1)]),
                    ]))
    return out


def multi_filament(cfg, n_out, keep=2):
    """The A1 mini profile with n_out filament slots, all of them slot `keep`
    (PETG), coloured as COLOURS. As plate._single_filament, lists that are
    per-filament are cut or repeated to match; the flush matrix gets the
    profile's own largest flush between any two different slots."""
    n = len(cfg.get("filament_type", []))
    out = {}
    for k, v in cfg.items():
        if isinstance(v, list) and len(v) == n:
            out[k] = [v[keep]] * n_out
        elif isinstance(v, list) and len(v) == n * n:
            flush = max(float(x) for i, x in enumerate(v) if i % (n + 1))
            out[k] = ["0" if r == c else "%g" % flush
                      for r in range(n_out) for c in range(n_out)]
        elif isinstance(v, list) and len(v) and len(v) % n == 0 and len(v) != n:
            per = len(v) // n
            out[k] = v[keep * per:(keep + 1) * per] * n_out
        else:
            out[k] = v
    out["filament_colour"] = COLOURS[:n_out]
    # A1 mini purges into its chute; a tower would only crowd the plate.
    out["enable_prime_tower"] = "0"
    return out


def write(path, layout, n_filaments):
    objects, items, cfg_objects, cfg_plates, problems = [], [], [], [], []
    oid = 1
    for pindex, (pname, entries) in enumerate(layout, start=1):
        problems += P.check_name("plate name", pname)
        ox, oy = P.plate_origin(pindex, len(layout))
        instances, placed = [], []
        for name, (cx, cy), ops, opts, parts in entries:
            meshes = []
            for stl, ext in parts:
                f = os.path.join(STL, stl + ".stl")
                if not os.path.exists(f):
                    problems.append("%s: no STL, run make cover first" % stl)
                    continue
                V, T = P.load_stl(f)
                meshes.append((stl, ext, P.rotate(V, ops), T))
            if not meshes:
                continue
            # Every part of an object shares its frame: centre the lot on the
            # object's bounding box, as Bambu Studio does.
            lo = np.min([m[2].min(0) for m in meshes], 0)
            hi = np.max([m[2].max(0) for m in meshes], 0)
            mid, size = (lo + hi) / 2.0, hi - lo
            x0, x1 = cx - size[0] / 2, cx + size[0] / 2
            y0, y1 = cy - size[1] / 2, cy + size[1] / 2
            if (x0 < P.MARGIN or y0 < P.MARGIN
                    or x1 > P.BED - P.MARGIN or y1 > P.BED - P.MARGIN):
                problems.append("%s comes within %.1f mm of the plate edge on "
                                "plate %d" % (name, P.MARGIN, pindex))
            for oname, a0, a1, b0, b1 in placed:
                if x0 - P.GAP < a1 and a0 - P.GAP < x1 and y0 - P.GAP < b1 and b0 - P.GAP < y1:
                    problems.append("%s is within %.0f mm of %s on plate %d"
                                    % (name, P.GAP, oname, pindex))
            placed.append((name, x0, x1, y0, y1))

            first = oid
            comps, cparts = [], []
            for stl, ext, V, T in meshes:
                V = V - mid
                objects.append(
                    '<object id="%d" type="model"><mesh><vertices>%s</vertices>'
                    '<triangles>%s</triangles></mesh></object>'
                    % (oid, "".join('<vertex x="%.5f" y="%.5f" z="%.5f"/>' % tuple(v)
                                    for v in V),
                       "".join('<triangle v1="%d" v2="%d" v3="%d"/>' % tuple(t)
                               for t in T)))
                comps.append('<component objectid="%d" transform="1 0 0 0 1 0 '
                             '0 0 1 0 0 0"/>' % oid)
                cparts.append(
                    '    <part id="%d" subtype="normal_part">\n'
                    '      <metadata key="name" value="%s"/>\n'
                    '      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 '
                    '0 0 0 1"/>\n'
                    '      <metadata key="extruder" value="%d"/>\n'
                    '      <mesh_stat face_count="%d" edges_fixed="0" '
                    'degenerate_facets="0" facets_removed="0" '
                    'facets_reversed="0" backwards_edges="0"/>\n'
                    '    </part>\n' % (oid, stl, ext, len(T)))
                oid += 1
            asm = oid
            oid += 1
            objects.append('<object id="%d" type="model"><components>%s'
                           '</components></object>' % (asm, "".join(comps)))
            items.append('<item objectid="%d" transform="1 0 0 0 1 0 0 0 1 '
                         '%.5f %.5f %.5f" printable="1"/>'
                         % (asm, ox + cx, oy + cy, size[2] / 2.0))
            cfg_objects.append(
                '  <object id="%d">\n'
                '    <metadata key="name" value="%s"/>\n'
                '    <metadata key="extruder" value="1"/>\n' % (asm, name)
                + "".join('    <metadata key="%s" value="%s"/>\n' % kv
                          for kv in sorted(opts.items()))
                + "".join(cparts) + '  </object>')
            instances.append('    <model_instance>\n'
                             '      <metadata key="object_id" value="%d"/>\n'
                             '      <metadata key="instance_id" value="0"/>\n'
                             '    </model_instance>' % asm)
            print("  plate %d  %-10s %6.1f x %5.1f x %4.1f  x %5.1f..%5.1f  "
                  "y %5.1f..%5.1f  %s" % (pindex, name, size[0], size[1], size[2],
                                          x0, x1, y0, y1,
                                          " + ".join(m[0] for m in meshes)))
            assert asm > first
        cfg_plates.append('  <plate>\n'
                          '    <metadata key="plater_id" value="%d"/>\n'
                          '    <metadata key="plater_name" value="%s"/>\n'
                          '    <metadata key="locked" value="false"/>\n'
                          '%s\n  </plate>' % (pindex, pname, "\n".join(instances)))

    model = ('<?xml version="1.0" encoding="UTF-8"?>\n'
             '<model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
             'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021">\n'
             ' <metadata name="Application">BambuStudio-02.08.02.61</metadata>\n'
             ' <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
             ' <metadata name="Title">%s</metadata>\n'
             ' <resources>%s</resources>\n <build>%s</build>\n</model>\n'
             % (TITLE, "".join(objects), "".join(items)))
    settings = ('<?xml version="1.0" encoding="UTF-8"?>\n<config>\n%s\n%s\n'
                '</config>\n' % ("\n".join(cfg_objects), "\n".join(cfg_plates)))
    base = json.load(open(P.PROJECT_SETTINGS))
    project = json.dumps(P._single_filament(base) if n_filaments == 1
                         else multi_filament(base, n_filaments), indent=1)
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
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, body in (("[Content_Types].xml", ctypes), ("_rels/.rels", rels),
                           ("3D/3dmodel.model", model),
                           ("Metadata/project_settings.config", project),
                           ("Metadata/model_settings.config", settings)):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, body)
    print("%s  (%.0f kB)" % (os.path.relpath(path, ROOT), os.path.getsize(path) / 1024.0))
    for p in problems:
        print("  PROBLEM " + p)
    return 1 if problems else 0


def main():
    rc = write(os.path.join(HERE, "TopCover_LabRax-A1mini.3mf"), plates(False), 1)
    if os.path.exists(os.path.join(STL, "logo_white_l.stl")):
        rc |= write(os.path.join(HERE, "TopCover_Skynet_LabRax-A1mini.3mf"),
                    plates(True), 3)
    return rc


if __name__ == "__main__":
    sys.exit(main())
