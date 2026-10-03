# What to print, what to keep, what to buy

Everything here is measured off the built solids or read out of a real slice —
nothing is estimated. Regenerate the print figures with `make plates`, and the
screw lengths with the arithmetic set out at the bottom.

## Print

**Four parts are the chassis and serve either device; three more are that
device's own.** Print the chassis once, then the kit for what you are racking.

**There is one 3MF per device, and each carries the chassis as well**, so
whichever you open is a complete build. Open it, print all six plates, done.

| file | plates | |
|---|---|---|
| `ucg-fiber/UCG_Fiber_LabRax-A1mini.3mf` | 1–3 chassis, 4–6 UCG-Fiber | 261.0 g, 11 h 23 |
| `usw-flex-mini/USW_Flex_LabRax-A1mini.3mf` | 1–3 chassis, 4–6 USW-Flex | 248.7 g, 11 h 09 |
| `tl-sg108e/TL_SG108E_LabRax-A1mini.3mf` | 1–3 chassis, 4–6 TL-SG108E | 255.6 g, 11 h 23 |
| `nuc6i7kyk/NUC6i7KYK_LabRax-A1mini.3mf` | 1–3 chassis, 4–6 NUC6i7KYK | 246.3 g, 11 h 21 |

Every plate carries its own label in Bambu Studio — `Chassis 2 of 3 - right
side`, `UCG-Fiber 3 of 3 - faceplate` — so the tab tells you which kit a plate
belongs to without reference to this table.

| kit | parts | filament | time |
|---|---|---|---|
| chassis | `side_l`, `side_r`, `leg_l`, `leg_r` | 112.1 g | 5 h 46 |
| UCG-Fiber | `tray_ucg_l`, `tray_ucg_r`, `faceplate_ucg` | 149.0 g | 5 h 37 |
| USW-Flex-2.5G-5 | `tray_usw_l`, `tray_usw_r`, `faceplate_usw` | 136.7 g | 5 h 22 |
| TL-SG108E | `tray_sg108e_l`, `tray_sg108e_r`, `faceplate_sg108e` | 143.6 g | 5 h 36 |
| NUC6i7KYK | `tray_nuc_l`, `tray_nuc_r`, `faceplate_nuc` | 134.3 g | 5 h 35 |

**If you are building both**, print the chassis once — the three chassis
plates are identical in the two files.

Chassis plus one device is about **261 g / 11 h 23** for the gateway, or
**249 g / 11 h 09** for the switch. All fifteen plates, 675.5 g.

| plate | part | size (mm) | filament | time | support |
|---|---|---|---|---|---|
| 1 | `side_l` | 33 × 212.5 × 44.5 | 36.1 g | 1 h 56 | yes |
| 2 | `side_r` | 33 × 212.5 × 44.5 | 36.1 g | 1 h 56 | yes |
| 3 | `leg_l` + `leg_r` | 33 × 91.5 × 44.5 each | 40.0 g | 1 h 55 | yes |
| 4 | `tray_ucg_l` | 136.5 × 131.4 × 9 | 49.0 g | 1 h 45 | yes |
| 5 | `tray_ucg_r` | 136.5 × 131.4 × 9 | 57.3 g | 2 h 07 | yes |
| 6 | `faceplate_ucg` | 213.6 × 20 × 44.5 | 42.7 g | 1 h 45 | no |
| 4* | `tray_usw_l` | 136.5 × 128.4 × 19.6 | 42.5 g | 1 h 37 | yes |
| 5* | `tray_usw_r` | 136.5 × 128.4 × 19.6 | 55.5 g | 2 h 05 | yes |
| 6* | `faceplate_usw` | 213.6 × 20 × 44.5 | 38.6 g | 1 h 40 | no |
| 4† | `tray_sg108e_l` | 136.5 × 128.4 × 17.7 | 47.3 g | 1 h 45 | yes |
| 5† | `tray_sg108e_r` | 136.5 × 128.4 × 17.7 | 59.2 g | 2 h 12 | yes |
| 6† | `faceplate_sg108e` | 213.6 × 20 × 44.5 | 37.1 g | 1 h 39 | no |
| 4‡ | `tray_nuc_l` | 136.5 × 128.4 × 11.2 | 44.4 g | 1 h 45 | yes |
| 5‡ | `tray_nuc_r` | 136.5 × 128.4 × 11.2 | 55.4 g | 2 h 12 | yes |
| 6‡ | `faceplate_nuc` | 213.6 × 20 × 44.5 | 34.4 g | 1 h 38 | no |

\* in `USW_Flex_LabRax-A1mini.3mf`, † in `TL_SG108E_LabRax-A1mini.3mf`,
‡ in `NUC6i7KYK_LabRax-A1mini.3mf`; the rows with no mark are in
`UCG_Fiber_LabRax-A1mini.3mf`. Plates 1–3 are the same chassis in all four.

PETG, 0.2 mm layers, and the plated 3MF already carries the orientations and
the per-part support and brim settings — see
[print-settings.md](print-settings.md).

## Keep what you already printed

**Nothing carries over from the version with a bolted splice.** The joint
between each side and its rear leg is now a runner, which changes both of
them, and the faceplate and the trays were given the clearance they never
had. A full chassis and one kit is about 261 g and 11 h 23.

Plate numbers 1 to 6 are unchanged, so anything already quoted against them
still means the same thing.

| part | verdict |
|---|---|
| `side_l`, `side_r` | **reprint, both** — the splice slots are gone and a dovetail tongue runs along the inside of the rail; the ledge starts 0.3 mm further back |
| `leg_l`, `leg_r` | **reprint, both** — no bosses, no nuts: a grooved runner the side slides into, with a sprung catch at its foot for the end stop |
| `faceplate` | **reprint** — 0.4 mm narrower, and its nuts now go in from the ends |
| `tray_l`, `tray_r` | **reprint, both** — 0.2 mm of room a side, 0.3 in the lap, looser pegs |
| `top_bar`, bottom bar | **gone** — replaced by the faceplate |

An old side has no tongue for a new leg to run on, and an old leg has no
groove. Print the two runner coupons in `common/stl/` first — see the
README's caveats.

**Reprint the trays as a pair.** An old half will not mate with a new one:
the peg sockets and the lap are a different size.

## Buy

| qty | item |
|---|---|
| **16** | **M6 × 12 button head** |
| **4** | **M6 nut** (DIN 934, 10 mm across the flats, 5 mm thick) |
| **12** | **M6 washer** (DIN 125 form A, ⌀12.5, 1.6 thick) |

One screw length for the whole bracket. The twelve rack screws need no nuts —
the Lab Rax posts already hold them.

| qty | where | nut | washer |
|---|---|---|---|
| 12 | bracket to rack: 3 per ear, 4 ears | none — in the post | yes |
| 4 | faceplate, through the front ears | 4 × M6 | no |

The side and the rear leg take no screw: the side's tongue slides into the
leg's groove.

**The twelve washers are not optional.** Every one of the rack screws goes
through a slot 6.6 mm wide, and an M6 button head is 10.5 across. Without a washer the head lands on two thin
crescents beside the slot, about 25 mm² of PETG, and tightening will bury it.
A ⌀12.5 washer spreads that to 46–60 mm², which is what the four screws in
round counterbored holes already have.

`make assembly` measures this: it puts a real screw, nut and washer at all
sixteen positions and reports the seat area at each.

### Why 12 mm, and how the design was made to suit it

The binding constraint is the rack post. Its equipment hole is **blind at
6 mm**: 2 mm of ⌀7.6 clearance, then a 4 mm hex pocket holding the nut. A
screw that goes in more than 6 mm past the ear hits the end of the hole and
never clamps; one that goes in less than about 5 mm barely catches the nut.

That fixes the ear thickness. At **6.5 mm**, a 12 mm screw enters the post
5.5 mm — half a millimetre clear of the bottom — with **3.5 mm of thread in
the nut**. Thicker ears and the screw cannot reach; thinner and it bottoms
out. The 8 mm ears this bracket had before wanted an M6 × 14, which is a
nuisance to buy.

Everything else was then arranged around the same 12 mm:

| joint | how it is made to fit | engagement |
|---|---|---|
| rack | ear 6.5 mm, into the post's own nut | 3.5 mm |
| faceplate | head sunk 1 mm into the ear, nut 1.5 mm into the plate | 5.0 mm |

The tray's two halves are not on this list: they take no fastener at all. The
tab that used to carry one hung off a 10 x 3 mm neck with the bolt 6.5 mm
above it, so nearly all the preload arrived as bending; CalculiX put it at
26 N against roughly 1700 N from an M6 at 2 N·m, and both tabs duly snapped
off on first tightening. The halves are now keyed by four ⌀5 pegs and held by
their 60 mm lap, the rails, the faceplate and the rear stops — see
[measurements.md](measurements.md).

The faceplate's nut sits in a slot cut in from the end of the plate, 1.5 mm
behind its front face, so a 12 mm screw with its head sunk 1 mm into the ear
ends flush with the far side of the nut.

`make verify` checks all of them, on every build: that each screw reaches its nut
with at least 3 mm of thread, and that the rack screw does not bottom out.
