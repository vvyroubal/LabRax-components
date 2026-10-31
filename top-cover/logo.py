"""The logo on the top cover, read from a Bambu Studio project at build time.

The artwork is Krafty3D's "Skynet Logo - Plate", under MakerWorld's Standard
Digital File License: fine to print for yourself, not to redistribute. So it
is never copied into this repository. top-cover/assets/Skynet.3mf is read when
the cover is built, and everything made from it -- the logo's STLs and the 3MF
that carries them -- is ignored by git.

The project is a dark backdrop with 84 coloured pieces standing 1 mm proud of
it: a red striped triangle, SKYNET in white, a line of white small print and a
line of red smaller print. Here the backdrop is the cover itself, and each
piece is scaled to fit the band in front of the grilles and stands LOGO_H
proud of the panel. Pieces whose strokes would come out under MIN_STROKE are
left out, which at any scale that fits loses the red CYBERDYNE line and one
speck of the white one; the scale is worked out from what is left.
"""

import os
import re
import zipfile
from collections import Counter

import numpy as np

import cover as C

ASSET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets",
                     "Skynet.3mf")
# The project's own extruders: 1 the backdrop, 2 white, 3 red.
COLOURS = {"2": "white", "3": "red"}
ART_Z0, ART_Z1 = 2.0, 3.0    # where the pieces sit in the project


def available():
    return os.path.exists(ASSET)


def _pieces():
    """Every piece but the backdrop: (colour, vertices, triangles)."""
    z = zipfile.ZipFile(ASSET)
    cfg = z.read("Metadata/model_settings.config").decode("utf8", "replace")
    ext = {pid: re.findall(r'key="extruder" value="(\d+)"', body)[0]
           for pid, _sub, body in re.findall(
               r'<part id="(\d+)" subtype="([^"]+)">(.*?)</part>', cfg, re.S)}
    root = z.read("3D/3dmodel.model").decode("utf8", "replace")
    comps = re.findall(r'<component p:path="([^"]+)" objectid="(\d+)"'
                       r'[^>]*?transform="([^"]*)"', root)
    files = {}
    out = []
    for k, (path, mid, tr) in enumerate(comps):
        colour = COLOURS.get(ext.get(str(k + 1)))
        if colour is None:
            continue                       # the backdrop
        if path not in files:
            s = z.read(path.lstrip("/")).decode("utf8", "replace")
            files[path] = {
                i: (np.array(re.findall(r'<vertex x="([-\d.e]+)" y="([-\d.e]+)"'
                                        r' z="([-\d.e]+)"', b), float),
                    np.array(re.findall(r'<triangle v1="(\d+)" v2="(\d+)"'
                                        r' v3="(\d+)"', b), int))
                for i, b in re.findall(r'<object id="(\d+)"[^>]*>(.*?)</object>',
                                       s, re.S)}
        v, t = files[path][mid]
        m = np.array(tr.split(), float).reshape(4, 3)
        out.append((colour, v @ m[:3] + m[3], t))
    return out


def stroke(v, t):
    """A piece's line width: twice its top face's area over its perimeter."""
    top = [tri for tri in t
           if np.cross(v[tri[1]] - v[tri[0]], v[tri[2]] - v[tri[0]])[2] > 1e-9]
    area = sum(0.5 * abs(np.cross(v[b] - v[a], v[c] - v[a])[2]) for a, b, c in top)
    edges = Counter()
    for a, b, c in top:
        for e in ((a, b), (b, c), (c, a)):
            edges[tuple(sorted(e))] += 1
    perim = sum(np.linalg.norm(v[a][:2] - v[b][:2])
                for (a, b), n in edges.items() if n == 1)
    return 2.0 * area / perim if perim else 0.0, area


def layout():
    """The pieces placed on the cover: (colour, vertices, triangles), and a
    report: the scale, what was dropped and the thinnest stroke kept."""
    pieces = []
    for colour, v, t in _pieces():
        w, area = stroke(v, t)
        if area > 0.01:                    # the project carries empty specks
            pieces.append((colour, v, t, w))

    band_w = 2.0 * C.LOGO_X1
    band_h = C.LOGO_Y1 - C.LOGO_Y0

    def fit(keep):
        lo = np.min([p[1].min(0) for p in keep], 0)
        hi = np.max([p[1].max(0) for p in keep], 0)
        return lo, hi, min(band_w / (hi[0] - lo[0]), band_h / (hi[1] - lo[1]))

    # Leave out the fewest, thinnest pieces that let everything else print.
    # Leaving pieces out can only shrink the artwork and so raise the scale,
    # so try each stroke width as the cut-off, thinnest first, and take the
    # first that works. Doing it the other way -- scale to everything, then
    # drop what is thin at that scale -- throws away lines that would have
    # been fine once the thinnest had gone.
    for cut in sorted(set(p[3] for p in pieces)):
        keep = [p for p in pieces if p[3] >= cut]
        lo, hi, scale = fit(keep)
        if cut * scale >= C.MIN_STROKE:
            break

    centre = (lo + hi) / 2.0
    cy = (C.LOGO_Y0 + C.LOGO_Y1) / 2.0
    placed = []
    for colour, v, t, w in keep:
        p = np.empty_like(v)
        p[:, 0] = (v[:, 0] - centre[0]) * scale
        p[:, 1] = (v[:, 1] - centre[1]) * scale + cy
        p[:, 2] = C.PANEL_T + (v[:, 2] - ART_Z0) / (ART_Z1 - ART_Z0) * C.LOGO_H
        placed.append((colour, p, t))
    report = {
        "scale": scale,
        "size": ((hi[0] - lo[0]) * scale, (hi[1] - lo[1]) * scale),
        "kept": len(keep),
        "dropped": len(pieces) - len(keep),
        "thinnest": min(p[3] for p in keep) * scale,
    }
    return placed, report


def solids(placed):
    """The pieces as FreeCAD solids, cut at the seam: {(colour, side): shape}.

    side is -1 for the left half, +1 for the right. A piece that straddles the
    seam is cut there, so each half carries exactly its own share.
    """
    import FreeCAD as App
    import Mesh
    import Part

    big = 500.0
    halves = {-1: Part.makeBox(big, big, big, App.Vector(-big, -big / 2, -big / 2)),
              +1: Part.makeBox(big, big, big, App.Vector(0, -big / 2, -big / 2))}
    out = {}
    for colour, v, t in placed:
        m = Mesh.Mesh([[App.Vector(*v[i]) for i in tri] for tri in t])
        sh = Part.Shape()
        sh.makeShapeFromMesh(m.Topology, 0.01)
        solid = Part.makeSolid(sh).removeSplitter()
        for side in (-1, 1):
            if side * v[:, 0].max() <= 0 and side * v[:, 0].min() <= 0:
                continue                   # wholly on the other half
            piece = solid
            if v[:, 0].min() < 0 < v[:, 0].max():
                piece = solid.common(halves[side])
                if not piece.Solids:
                    continue
            out.setdefault((colour, side), []).append(piece)
    return {k: Part.makeCompound(v) for k, v in out.items()}
