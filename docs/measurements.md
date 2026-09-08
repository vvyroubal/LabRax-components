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

## Horizontal spacing — 236.525 mm, and the 222.25 mm opening

The post is 30 mm across the mounting face by 35 mm deep. Its equipment holes
sit at x = 7.862 mm from the post centreline, i.e. **7.138 mm inboard of the
face that bounds the rack opening**.

That single number ties the two figures together:

```
236.525 / 2  -  222.25 / 2  =  118.2625 - 111.125  =  7.1375
```

So a 236.525 mm column spacing implies a 222.25 mm clear opening, and the post
measures 7.138 mm against that 7.1375 mm. The documentation's "222 mm" is
222.25 rounded.

Each hole is ⌀7.6 mm for the first 2 mm and ⌀11.65 mm for the next 4 mm — a
clearance hole with a counterbore for an M6 button head. The frame-assembly
holes on the post's other face are ⌀6.4 with a ⌀10.9 counterbore, which is the
same M6 hardware.

## Faceplate envelope — 254 × 44.45 mm

The reference mount measures exactly 254.00 × 44.45 × 134.00 mm. Its ears are
4.5 mm thick and its mounting holes are **slots, 11.4 × 7.4 mm**, centred
238.125 mm apart — 1.6 mm wider than nominal, which the slot width absorbs.
That a shipped, working Lab Rax part slots its holes this generously is why
this bracket slots its own, and why 3.2 mm of material outboard of the slot is
acceptable (the reference leaves 2.24 mm).

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
