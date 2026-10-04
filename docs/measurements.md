# Where the numbers came from

The Lab Rax documentation quotes rounded figures ("222 mm between posts"), and
the rack is itself a 3D print, so the interface dimensions in
`common/src/params.py` — the ones tagged `[rack]` — were measured off the
published models instead. This records what was measured and how, so it can be
re-checked against a newer release of the rack.

## Reproducing it

The rack's files are not in this repository. Download the
[bolted 5U rack](https://makerworld.com/en/models/1464819-lab-rax-10-server-rack-bolted-version-5u)
from MakerWorld, then:

```sh
python3 common/tools/measure_rack.py <file.3mf | part.stl | object.model>
```

It needs Python 3 with NumPy. Holes are found by collecting triangles whose
normal is perpendicular to a candidate axis, grouping them by shared vertices,
and fitting a circle to each group. A group whose fit residual stays under
0.25 mm is a real hole rather than a rounded corner.

Three files were measured:

| file | what it is |
|---|---|
| the rack's A1 mini 3MF | the complete Lab Rax 5U rack, bolted version, plated for an A1 mini |
| its post joiner | the part that joins rack pieces too large for the bed |
| a Lab Rax 1U mount | a published mount for another device, as a second witness to the rack's interface |

The rack 3MF's `Metadata/model_settings.config` names each object. The posts
are `5U Vertical Post - A/B.stl`, the upper and lower halves of one post split
to fit a 180 mm bed. To measure one on its own, unpack the 3MF and point the
tool at its object file:

```sh
unzip -q rack.3mf -d rack/
python3 common/tools/measure_rack.py rack/3D/Objects/object_81.model
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

The 1U mount agrees: its three slots per side are centred 6.325 / 22.225 /
38.125 mm up from the bottom of its U.

## The posts hold the nuts

Each equipment hole is ⌀7.60 for the first 2 mm from the post's outer face and
⌀11.65 for the next 4 mm. That is not a counterbore for a screw head: slicing
the post across the wider zone gives boundary radii alternating 5.04 and 5.82
at 30° intervals, which is a **hexagon 10.09 mm across the flats and 11.65
across the corners** — an M6 nut pocket. The hole is blind at 6 mm.

So a rack screw goes in from **outside the rack** and threads into a nut the
post already holds. Equipment mounted in a Lab Rax needs clearance holes and
nothing else. The post joiner carries the same pocket.

## Width — 222.25 mm between the posts

The two columns of equipment holes are **236.525 mm** apart, and the posts
leave **222.25 mm** clear between them. The bracket's body is 220.4 mm wide,
0.925 mm clear of each post.

## Depth — 170.0 mm between the posts

Three separate frame members in the rack's 3MF are 170.0 mm long, and that is
the clear gap between the front posts and the rear ones.

Two things about depth are easy to get wrong:

- **The side panel is not the gap.** `Side Panel Half.stl` measures 175.9 mm
  front to back, but the panel is 3 mm thick and seats about 2.95 mm into a
  groove at each end: 170.0 + 2 × 2.95 is 175.9 exactly.
- **The post's depth is not settled by the mesh.** Its section is 30 × 35 mm
  and nothing in the print plate says which way it faces, so the distance
  over the outside of the posts is either **230** or **240 mm**.

The model takes the midpoint, 235 mm, as `RACK_D`. It has not been measured
on an assembled rack, and it does not need to be right: the joint between
each side and its rear leg slides, and covers 229 – 257 mm.

## Faceplate envelope — 254 × 44.45 mm

The 1U mount measures exactly 254.00 × 44.45 mm across its face. Its ears are
4.5 mm thick and its mounting holes are **slots, 11.4 × 7.4 mm**, centred
238.125 mm apart — 1.6 mm wider than the posts' 236.525, which the slots
absorb. That a working Lab Rax part slots its holes this generously is why
this bracket slots its own, 11.0 × 6.6 mm, and why 3.2 mm of material outboard
of the slot is acceptable (that mount leaves 2.24 mm).

## The devices

Case dimensions are the manufacturers' published figures:

| device | size (mm) | mass | source |
|---|---|---|---|
| UCG-Fiber | 212.8 × 127.6 × 30.0 | 734 g | Ubiquiti; mass with an SSD fitted |
| USW-Flex-2.5G-5 | 117.1 × 90.0 × 21.2 | 206 g | Ubiquiti |
| TL-SG108E | 158 × 101 × 25 | 250 g, estimated | TP-Link, who publish no weight |
| NUC6i7KYK | 211 × 116 × 28 | 700 g, estimated | Intel, who publish no weight |

The masses only feed the load checks, where the gateway's 734 g is the
heaviest case.

### The gateway's display

Measured on the device with callipers: the display is a **21.0 × 10.0 mm
stadium**, centred on the case's width. It is the only feature on the front
face — no reset button, and the power jack is at the back with the ports —
which is what lets the faceplate be solid apart from one window.

The window is 22.5 × 11.0 mm, larger all round, because the gateway can shift
0.6 mm either way between the rails and a window cut to the display's own
size could clip it.

Its height is given by a rule about the faceplate rather than by a
measurement of the case: **the window's top edge sits 7.0 mm below the
underside of the flange** that reaches back over the gateway. That puts the
window's centre 24.3 mm above the bottom of the U, or 18.3 mm above the
bottom of the case. `make verify` measures the 7.0 mm on the built solid.
If your unit's display sits elsewhere, change `top_gap` in
`ucg-fiber/device.py`.
