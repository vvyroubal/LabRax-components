#!/usr/bin/env python3
"""Re-measure the Lab Rax rack and a reference mount from their mesh files.

The rack interface numbers in src/params.py were taken from the shipped Lab
Rax models rather than from prose, because the published figures are rounded.
This reproduces that measurement so the numbers can be re-checked against a
newer release of the rack.

    python3 tools/measure_rack.py <file.3mf|file.stl> [...]

For a 3MF it reports each object; for an STL, the file. Holes are found by
collecting triangles whose normal is perpendicular to a candidate axis,
grouping them by connectivity and fitting a circle to each group.
"""

import re
import struct
import sys

import numpy as np

AXES = "XYZ"


def load(path):
    if path.lower().endswith(".stl"):
        return _load_stl(path)
    return _load_3mf_part(path)


def _weld(V, T):
    uniq, inv = np.unique(np.round(V, 4), axis=0, return_inverse=True)
    return uniq, inv[T]


def _load_stl(path):
    data = open(path, "rb").read()
    if data[:5].lower() == b"solid" and b"facet" in data[:2000]:
        vs = re.findall(rb"vertex\s+(\S+)\s+(\S+)\s+(\S+)", data)
        V = np.array(vs, dtype=float)
    else:
        n = struct.unpack("<I", data[80:84])[0]
        arr = np.frombuffer(data, dtype=np.uint8, count=n * 50, offset=84)
        arr = arr.reshape(n, 50)[:, 12:48].copy().view("<f4")
        V = arr.reshape(-1, 3).astype(float)
    return _weld(V, np.arange(len(V)).reshape(-1, 3))


def _load_3mf_part(path):
    txt = open(path, encoding="utf-8", errors="ignore").read()
    vs = re.findall(r'<vertex x="(\S+?)" y="(\S+?)" z="(\S+?)"', txt)
    ts = re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"', txt)
    return np.array(vs, dtype=float), np.array(ts, dtype=int)


def normals(V, T):
    a, b, c = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
    n = np.cross(b - a, c - a)
    L = np.linalg.norm(n, axis=1)
    ok = L > 1e-12
    n[ok] /= L[ok][:, None]
    return n


class _UF:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[rb] = ra


def _fit_circle(P):
    A = np.c_[2 * P[:, 0], 2 * P[:, 1], np.ones(len(P))]
    cx, cy, k = np.linalg.lstsq(A, (P ** 2).sum(1), rcond=None)[0]
    r = np.sqrt(max(k + cx * cx + cy * cy, 0.0))
    return cx, cy, r, np.abs(np.linalg.norm(P - [cx, cy], axis=1) - r).max()


def holes(V, T, ax, rmin=1.0, rmax=12.0, flat=0.06, fit=0.25):
    u, v = [i for i in range(3) if i != ax]
    cand = np.where(np.abs(normals(V, T)[:, ax]) < flat)[0]
    if not len(cand):
        return []
    uf = _UF(len(V))
    for t in T[cand]:
        uf.union(t[0], t[1])
        uf.union(t[0], t[2])
    groups = {}
    for i in cand:
        groups.setdefault(uf.find(T[i][0]), []).append(i)
    out = []
    for idx in groups.values():
        vids = np.unique(T[idx].ravel())
        if len(vids) < 8:
            continue
        cu, cv, r, err = _fit_circle(V[vids][:, [u, v]])
        if rmin <= r <= rmax and err <= fit:
            span = V[vids][:, ax]
            out.append((2 * r, cu, cv, span.min(), span.max()))
    return sorted(out, key=lambda h: (round(h[1], 2), h[2]))


def report(path):
    V, T = load(path)
    print("\n== %s" % path)
    print("   %d verts, %d tris, size %s"
          % (len(V), len(T), np.round(V.max(0) - V.min(0), 3)))
    for ax in range(3):
        hs = holes(V, T, ax)
        if not hs:
            continue
        u, v = [i for i in range(3) if i != ax]
        print("   holes about %s:" % AXES[ax])
        for d, cu, cv, a0, a1 in hs:
            print("     d=%7.3f  %s=%9.3f %s=%9.3f  %s=[%8.3f,%8.3f]"
                  % (d, AXES[u], cu, AXES[v], cv, AXES[ax], a0, a1))
        if len(hs) > 2:
            col = sorted(h[2] for h in hs)
            gaps = np.diff(col)
            print("     spacing along %s: %s" % (AXES[v], np.round(gaps, 3)))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    for f in sys.argv[1:]:
        report(f)
