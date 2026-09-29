#!/usr/bin/env python3
"""Slice every plate for real and measure what the printer would actually do.

The plater checks where the parts sit. That is not the same as what gets
printed: support does not stay inside the part it holds up, and on the trays it
reaches about 5 mm past the overhanging edge. The only way to know is to slice
and read the toolpaths back.

    python3 common/tools/checkplates.py

Each plate is written out as a one-plate project and sliced on its own, because
Bambu Studio's CLI will not slice a project with more than two plates. Extents
are taken between the machine's own start and end blocks -- the A1 mini primes
at X = -13.5, which is outside the bed and none of our business.

Exits non-zero if anything would be printed outside the build volume.

Scratch files go under the project, not /tmp: Bambu Studio runs in a flatpak
here, which has a /tmp of its own and cannot see the host's.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "common", "tools"))

import plate  # noqa: E402

SLICER = os.environ.get(
    "BAMBU", "flatpak run com.bambulab.BambuStudio").split()
BED_X = BED_Y = BED_Z = 180.0
WANT_MARGIN = 3.0  # below this the first layer is on the lip of the plate


def extents(gcode):
    """(xmin, xmax, ymin, ymax, zmax) of everything actually extruded."""
    xs, ys, zs = [], [], []
    x = y = z = None
    started = False
    for line in open(gcode, errors="ignore"):
        if not started:
            started = "MACHINE_START_GCODE_END" in line
            continue
        if "MACHINE_END_GCODE_START" in line:
            break
        # G2/G3 too: Bambu fits arcs, and an arc that is not counted is a
        # part of the print that never gets measured.
        if line[:2] not in ("G0", "G1", "G2", "G3"):
            continue
        # Bambu writes values with no leading zero -- "E.08133" -- so a
        # pattern that insists on a digit before the point silently drops
        # most of the print.
        mx = re.search(r"\bX(-?\d*\.?\d+)", line)
        my = re.search(r"\bY(-?\d*\.?\d+)", line)
        mz = re.search(r"\bZ(-?\d*\.?\d+)", line)
        me = re.search(r"\bE(-?\d*\.?\d+)", line)
        if mx:
            x = float(mx.group(1))
        if my:
            y = float(my.group(1))
        if mz:
            z = float(mz.group(1))
        if me and float(me.group(1)) > 0 and x is not None and y is not None:
            xs.append(x)
            ys.append(y)
            if z is not None:
                zs.append(z)
    if not xs:
        return None
    return min(xs), max(xs), min(ys), max(ys), max(zs)


def main():
    tmp = tempfile.mkdtemp(prefix=".plates-", dir=ROOT)
    every = plate.PLATES
    bad = []
    print("%-6s %-26s %-18s %-18s %7s %8s"
          % ("plate", "parts", "X printed", "Y printed", "max Z", "margin"))
    for i, (title, parts) in enumerate(every, start=1):
        one = os.path.join(tmp, "plate%d.3mf" % i)
        plate.PLATES = [(title, parts)]
        plate.OUT = one
        _quiet(plate)
        out = os.path.join(tmp, "out%d" % i)
        os.makedirs(out, exist_ok=True)
        subprocess.run(SLICER + ["--arrange", "0", "--slice", "0",
                                 "--outputdir", out, one],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=600)
        g = os.path.join(out, "plate_1.gcode")
        if not os.path.exists(g):
            print("%-6d %-26s  did not slice" % (i, title))
            bad.append("plate %d did not slice" % i)
            continue
        x0, x1, y0, y1, z1 = extents(g)
        margin = min(x0, y0, BED_X - x1, BED_Y - y1)
        names = ", ".join(p[0] for p in parts)
        ok = margin >= 0 and z1 <= BED_Z
        tight = ok and margin < WANT_MARGIN
        print("%-6d %-26s %6.2f .. %6.2f  %6.2f .. %6.2f %7.2f %8.2f  %s"
              % (i, names, x0, x1, y0, y1, z1, margin,
                 "off the bed" if not ok else ("tight" if tight else "ok")))
        if not ok:
            bad.append("%s prints outside the bed (margin %.2f)" % (names, margin))
        elif tight:
            bad.append("%s comes %.2f mm from the plate edge" % (names, margin))
    plate.PLATES = every
    shutil.rmtree(tmp, ignore_errors=True)
    print("\nbed %.0f x %.0f x %.0f" % (BED_X, BED_Y, BED_Z))

    bad += slice_whole_files()

    for b in bad:
        print("  PROBLEM %s" % b)
    return 1 if bad else 0


def slice_whole_files():
    """Slice each exported 3MF as it stands, every plate in one go.

    The per-plate pass above rewrites each plate as its own single-plate
    project, so it only ever exercises plate 1's origin and says nothing about
    whether the real file's plate grid is right. It was wrong for a long time
    -- two plates to a row where Bambu Studio wants three -- and every plate
    from the second row on came back "Nothing to be sliced". Nothing noticed,
    because nothing had ever asked the slicer to open the file it ships.
    """
    print("\nthe exported files, sliced whole")
    bad = []
    for kit in plate.KITS:
        f = plate.kit_path(kit)
        if not os.path.exists(f):
            bad.append("%s missing -- run make plate" % kit["out"])
            continue
        out = tempfile.mkdtemp(prefix=".whole-", dir=ROOT)
        try:
            # Slice a COPY. Bambu Studio writes back to the file it is given
            # -- thumbnails, per-object meshes, slice_info, plate previews --
            # which took a 96 kB export to 217 kB and left the working tree
            # dirty every time these checks ran.
            copy = os.path.join(out, os.path.basename(f))
            shutil.copy2(f, copy)
            r = subprocess.run(SLICER + ["--arrange", "0", "--slice", "0",
                                         "--outputdir", out, copy],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               timeout=1800)
            log = r.stdout.decode("utf-8", "replace")
            want = len(plate.CHASSIS_PLATES) + len(kit["plates"])
            got = len([n for n in os.listdir(out) if n.endswith(".gcode")])
            trouble = [l.split("]")[-1].strip()
                       for l in log.splitlines()
                       if "Nothing to be sliced" in l or "boundary" in l]
            ok = r.returncode == 0 and got == want and not trouble
            print("  %-34s %d of %d plates  %s"
                  % (kit["out"], got, want,
                     "ok" if ok else (trouble[0][:48] if trouble
                                      else "exit %d" % r.returncode)))
            if not ok:
                bad.append("%s: %s" % (kit["out"],
                                       trouble[0] if trouble
                                       else "%d of %d plates sliced"
                                       % (got, want)))
        finally:
            shutil.rmtree(out, ignore_errors=True)
    return bad


def _quiet(mod):
    import io
    import contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        mod.build()


if __name__ == "__main__":
    sys.exit(main())
