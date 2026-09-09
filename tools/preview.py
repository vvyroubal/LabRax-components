#!/usr/bin/env python3
"""Render the exported STLs to flat-shaded orthographic PNGs.

FreeCAD runs headless here, so there is no GUI to take a screenshot from.
This projects the meshes itself -- triangles sorted back-to-front and filled
with a shade taken from the face normal, which is enough to read the shape.

    python3 tools/preview.py            # writes images/*.png
"""

import os
import struct
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STL = os.path.join(ROOT, "export", "stl")
OUT = os.path.join(ROOT, "images")

# part -> fill hue, so the pieces stay distinguishable in the assembly views
COLOUR = {
    "side_l": (0.72, 0.44, 0.24),
    "side_r": (0.72, 0.44, 0.24),
    "top_bar_l": (0.30, 0.44, 0.62),
    "top_bar_r": (0.30, 0.44, 0.62),
}

VIEWS = {
    # name: (right vector, up vector) -- the camera looks along right x up
    "front": ((1, 0, 0), (0, 0, 1)),
    "top": ((1, 0, 0), (0, -1, 0)),
    "iso": None,  # built below
}


def load_stl(path):
    """Return an (n, 3, 3) array of triangle vertices. FreeCAD writes ASCII."""
    data = open(path, "rb").read()
    if data[:5].lower() == b"solid" and b"facet" in data[:2000]:
        import re
        vs = re.findall(rb"vertex\s+(\S+)\s+(\S+)\s+(\S+)", data)
        return np.array(vs, dtype=float).reshape(-1, 3, 3)
    n = struct.unpack("<I", data[80:84])[0]
    arr = np.frombuffer(data, dtype=np.uint8, count=n * 50, offset=84)
    tri = arr.reshape(n, 50)[:, 12:48].copy().view("<f4").astype(float)
    return tri.reshape(n, 3, 3)


def iso_basis():
    # 30 deg around X after 45 deg around Z: the usual isometric-ish view
    az, el = np.radians(35.0), np.radians(22.0)
    right = np.array([np.cos(az), -np.sin(az), 0.0])
    fwd = np.array([np.sin(az) * np.cos(el), np.cos(az) * np.cos(el), -np.sin(el)])
    up = np.cross(fwd, right)
    return right, up / np.linalg.norm(up)


def _png(path, img):
    """Write an HxWx3 uint8 array as a PNG, using only the stdlib."""
    import binascii
    import zlib
    h, w, _ = img.shape
    raw = np.concatenate(
        [np.zeros((h, 1), np.uint8), img.reshape(h, w * 3)], axis=1).tobytes()

    def chunk(tag, data):
        c = tag + data
        return (struct.pack(">I", len(data)) + c
                + struct.pack(">I", binascii.crc32(c) & 0xFFFFFFFF))

    open(path, "wb").write(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b""))


def render(tris_by_part, right, up, path, width=1100, pad=18, ss=2):
    """Flat-shaded orthographic view, painter's algorithm, supersampled."""
    right = np.array(right, dtype=float)
    up = np.array(up, dtype=float)
    view = np.cross(right, up)  # depth axis; larger = nearer the camera
    light = np.array([-0.35, -0.55, 0.76])
    light /= np.linalg.norm(light)

    pts, cols, depth = [], [], []
    for name, tris in tris_by_part.items():
        base = np.array(COLOUR.get(name, (0.5, 0.5, 0.5)))
        n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
        ln = np.linalg.norm(n, axis=1)
        ok = ln > 1e-12
        n[ok] /= ln[ok][:, None]
        vis = (n @ view) > 0
        t, nn = tris[vis], n[vis]
        if not len(t):
            continue
        shade = 0.42 + 0.58 * np.clip(nn @ light, 0.0, None)
        pts.append(np.stack([t @ right, t @ up], axis=-1))
        cols.append(base[None, :] * shade[:, None])
        depth.append((t @ view).mean(axis=1))
    P2 = np.concatenate(pts)
    C = np.concatenate(cols)
    D = np.concatenate(depth)
    order = np.argsort(D)
    P2, C = P2[order], C[order]

    lo, hi = P2.reshape(-1, 2).min(0), P2.reshape(-1, 2).max(0)
    span = hi - lo
    W = width * ss
    scale = (W - 2 * pad * ss) / span[0]
    H = int(span[1] * scale + 2 * pad * ss)
    H += (-H) % ss  # the supersample fold needs whole blocks

    sx = (P2[:, :, 0] - lo[0]) * scale + pad * ss
    sy = H - ((P2[:, :, 1] - lo[1]) * scale + pad * ss)

    img = np.empty((H, W, 3), np.float32)
    img[:] = np.array((0.07, 0.086, 0.11), np.float32)

    for i in range(len(P2)):
        x, y = sx[i], sy[i]
        x0 = max(int(np.floor(x.min())), 0)
        x1 = min(int(np.ceil(x.max())) + 1, W)
        y0 = max(int(np.floor(y.min())), 0)
        y1 = min(int(np.ceil(y.max())) + 1, H)
        if x1 <= x0 or y1 <= y0:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
        d = ((y[1] - y[2]) * (x[0] - x[2]) + (x[2] - x[1]) * (y[0] - y[2]))
        if abs(d) < 1e-12:
            continue
        a = ((y[1] - y[2]) * (gx - x[2]) + (x[2] - x[1]) * (gy - y[2])) / d
        b = ((y[2] - y[0]) * (gx - x[2]) + (x[0] - x[2]) * (gy - y[2])) / d
        inside = (a >= 0) & (b >= 0) & (a + b <= 1)
        if inside.any():
            img[y0:y1, x0:x1][inside] = C[i]

    img = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    img = img.reshape(H // ss, ss, W // ss, ss, 3).mean(axis=(1, 3))
    _png(path, img.astype(np.uint8))
    return W // ss, H // ss


def main():
    os.makedirs(OUT, exist_ok=True)
    parts = {}
    for name in COLOUR:
        p = os.path.join(STL, name + ".stl")
        if os.path.exists(p):
            parts[name] = load_stl(p)
    if not parts:
        print("no STLs in %s -- run make first" % STL)
        return 1

    VIEWS["iso"] = iso_basis()
    for view, (right, up) in VIEWS.items():
        f = os.path.join(OUT, "assembly-%s.png" % view)
        w, h = render(parts, right, up, f)
        print("%-28s %d x %d" % (os.path.relpath(f, ROOT), w, h))

    # the two big parts on their own, in the orientation they are printed
    for name in ("tray", "ear_r"):
        if name in parts:
            f = os.path.join(OUT, "part-%s.png" % name)
            render({name: parts[name]}, *iso_basis(), path=f, width=700)
            print("%-28s" % os.path.relpath(f, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
