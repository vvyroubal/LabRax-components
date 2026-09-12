# Where the numbers came from

The Lab Rax documentation quotes rounded figures ("222 mm between posts"), and
the rack is itself a 3D print, so the interface dimensions in `src/params.py`
were measured off the shipped models instead. This records what was measured
and how, so it can be re-checked against a newer release of the rack.

Reproduce with:

```sh
python3 tools/measure_rack.py <object.model|part.stl>
```

Holes are found by collecting triangles whose normal is perpendicular to a
candidate axis, grouping them by shared vertices, and fitting a circle to each
group. A group whose fit residual stays under 0.25 mm is a real hole rather
than a rounded corner.

## Sources

Reference files live one level up, in `../` alongside this project:

| file | what it is |
|---|---|
| `../5U+Lab+Rax+Bolt+Together-A1Mini.3mf` | the complete Lab Rax 5U rack, bolted version, plated for an A1 mini |
| `../5U+Lab+Rax+Bolt+Together-A1Mini-Post-Joiner.3mf` | the joiner that splices rack parts too large for the bed |
| `~/Documents/cloud-gateway-1u-lab-rax.stl` | a known-good Lab Rax 1U gateway mount |

The 3MF's `Metadata/model_settings.config` names each object; the posts are
`5U Vertical Post - A/B.stl`, which are the upper and lower halves of one post
split to fit a 180 mm bed — the post joiner is what puts them back together.
Unpack the 3MF and point the tool at `3D/Objects/object_81.model`:

```sh
unzip -q ../5U+Lab+Rax+Bolt+Together-A1Mini.3mf -d /tmp/labrax
python3 tools/measure_rack.py /tmp/labrax/3D/Objects/object_81.model
```

## Vertical hole spacing — EIA-310

The post carries seven holes over an 88.90 mm span, which is exactly 2U. Their
measured gaps:

```
15.902   15.902   12.646   15.902   15.902   12.646
```

against EIA-310's `15.875 / 15.875 / 12.700`. The 0.03 mm difference is the
mesh's circle discretisation, not the design. Within one 44.45 mm U that puts
holes at **6.35 / 22.225 / 38.1 mm** from the bottom of the U.

Confirmed independently on the reference faceplate, whose three slots per side
are centred 6.325 / 22.225 / 38.125 mm up from the bottom of its U.

## The posts hold the nuts

Each equipment hole is ⌀7.60 for the first 2 mm from the post's outer face and
⌀11.65 for the next 4 mm. That is not a counterbore for a screw head — slicing
the post across the wider zone gives boundary radii alternating 5.04 and 5.82
at 30° intervals, which is a **hexagon 10.09 mm across the flats and 11.65
across the corners**: an M6 nut pocket, 5 mm deep.

So a rack screw goes in from **outside the rack** and threads into a nut the
post already holds. Equipment mounted in a Lab Rax needs clearance holes and
nothing else. `Bolted+Version+Post+Joiner.stl` carries the same trap, which is
where the figures above were first read off.

An earlier version of this bracket got that wrong, read the pocket as a
counterbore, and carried nut traps of its own that duplicated the rack's.

## Front posts to rear posts — 175.9 mm

Taken from `Side Panel Half.stl`, which spans the frame front to back and
measures 175.9 mm. It is the one interface number here that has **not** been
confirmed against an assembled rack: the 3MF is a print plate, so there is no
assembled geometry to measure and no rear-post placement to read. The rear
ears land on this figure; `RACK_D` in `src/params.py` is the single place to
change it.

## Faceplate envelope — 254 × 44.45 mm

The reference mount measures exactly 254.00 × 44.45 × 134.00 mm. Its ears are
4.5 mm thick and its mounting holes are **slots, 11.4 × 7.4 mm**, centred
238.125 mm apart — 1.6 mm wider than nominal, which the slot width absorbs.
That a shipped, working Lab Rax part slots its holes this generously is why
this bracket slots its own, and why 3.2 mm of material outboard of the slot is
acceptable (the reference leaves 2.24 mm).

## The gateway's display

Measured on the device with callipers, not taken from a datasheet: the front
window is a **21.0 x 10.0 mm stadium**, centred on the case's width, with its
**centre 14.0 mm above the case's bottom**. It is the only feature on the
front face -- no reset button, and the power jack is at the back with the
ports, which is what lets the faceplate be solid apart from the window.

The bracket's window is 22.5 x 11.0, larger all round. The gateway can shift
0.6 mm either way between the rails, so a window cut to the display's own size
could clip it. Its height needs no such allowance: the case sits on the tray,
so `DEV_Z0` fixes it.

## Why the tray's bolt tab went

Both tabs snapped off when their M6 was tightened. `make fem` meshes the rear
of each tray half and loads the fastener where it actually bears; the analysis
is saved as `cad/fem_tray_l.FCStd` and `cad/fem_tray_r.FCStd`, which open in
the FEM workbench with the result colour map on them.

| | tray_l | tray_r |
|---|---|---|
| peak von Mises at 100 N a bolt | 191.4 MPa | 152.0 MPa |
| where | (-10, 136.6, 3) | (10, 136.6, 6) |
| preload at which PETG yields | 26 N | 33 N |
| an M6 at 2 N·m, about 1700 N | 65x over | 52x over |

The peak sits exactly where both parts broke: Y = 136.6, the plane where the
tab meets the plate, at the outer corner. The tab hung off a 10 x 3 mm neck,
30 mm², with the bolt 6.5 mm above it and up to 22 mm behind, so nearly all of
the preload arrived as bending. At 100 N a bolt the model deflects 4.2 mm.

26 N of preload is about 0.03 N·m at the key. That is not a part that was
over-tightened; it is a part that could not be tightened at all.

## A note on `cloud-gateway-1u-lab-rax.stl`

This file is a Lab Rax gateway mount, but **not for the UCG-Fiber.** Measured:

- front bezel window **122.98 × 24.0 mm**
- internal side walls with inner faces at x = ±65, so a cavity ~130 mm wide
- no floor at mid-depth at all; the device is carried at its ends

A 130 mm cavity behind a 123 mm lipped window fits a **Cloud Gateway Ultra**
(129.6 × 89.6 × 27.4 mm). The UCG-Fiber is 212.8 mm wide — 83 mm wider than
that cavity — so this mount cannot hold one, and neither can anything derived
from it by scaling the shell.

It is still a good source for the *rack* interface, which is what it is used
for above.
