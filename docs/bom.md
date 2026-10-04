# What to print and what to buy

The print figures here are read out of a real slice and the sizes off the
built solids — nothing is estimated. `make plates` re-slices every plate.

## Print

**Four parts are the chassis and serve every device; three more are that
device's own.** There is one 3MF per device, and each carries the chassis as
well, so whichever you open is a complete build: print all six plates.

| file | plates | filament, time |
|---|---|---|
| `ucg-fiber/UCG_Fiber_LabRax-A1mini.3mf` | 1–3 chassis, 4–6 UCG-Fiber | 261.0 g, 11 h 23 |
| `usw-flex-mini/USW_Flex_LabRax-A1mini.3mf` | 1–3 chassis, 4–6 USW-Flex | 248.7 g, 11 h 09 |
| `tl-sg108e/TL_SG108E_LabRax-A1mini.3mf` | 1–3 chassis, 4–6 TL-SG108E | 254.7 g, 11 h 22 |
| `nuc6i7kyk/NUC6i7KYK_LabRax-A1mini.3mf` | 1–3 chassis, 4–6 NUC6i7KYK | 245.8 g, 11 h 21 |

Every plate carries its own label in Bambu Studio — `Chassis 2 of 3 - right
side`, `UCG-Fiber 3 of 3 - faceplate` — so the tab tells you which kit a plate
belongs to.

| kit | parts | filament | time |
|---|---|---|---|
| chassis | `side_l`, `side_r`, `leg_l`, `leg_r` | 112.1 g | 5 h 46 |
| UCG-Fiber | `tray_ucg_l`, `tray_ucg_r`, `faceplate_ucg` | 149.0 g | 5 h 37 |
| USW-Flex-2.5G-5 | `tray_usw_l`, `tray_usw_r`, `faceplate_usw` | 136.7 g | 5 h 22 |
| TL-SG108E | `tray_sg108e_l`, `tray_sg108e_r`, `faceplate_sg108e` | 142.7 g | 5 h 35 |
| NUC6i7KYK | `tray_nuc_l`, `tray_nuc_r`, `faceplate_nuc` | 133.7 g | 5 h 34 |

**Each bracket needs a chassis of its own.** Plates 1–3 are identical in all
four files, so for a second device print them again from whichever file is
open, then that device's plates 4–6.

Plate by plate:

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
| 6† | `faceplate_sg108e` | 213.6 × 20 × 44.5 | 36.2 g | 1 h 38 | no |
| 4‡ | `tray_nuc_l` | 136.5 × 128.4 × 11.2 | 44.4 g | 1 h 45 | yes |
| 5‡ | `tray_nuc_r` | 136.5 × 128.4 × 11.2 | 55.4 g | 2 h 12 | yes |
| 6‡ | `faceplate_nuc` | 213.6 × 20 × 44.5 | 33.9 g | 1 h 37 | no |

\* in `USW_Flex_LabRax-A1mini.3mf`, † in `TL_SG108E_LabRax-A1mini.3mf`,
‡ in `NUC6i7KYK_LabRax-A1mini.3mf`; the rows with no mark are in
`UCG_Fiber_LabRax-A1mini.3mf`.

Figures are for PETG at 0.2 mm layers with the profile the 3MFs carry — see
[print-settings.md](print-settings.md).

**Print the two runner coupons first.** `common/stl/coupon_tongue.stl` and
`common/stl/coupon_groove.stl` are 25 mm of the joint between a side and its
leg, and small. They are not in the 3MFs: drop the two STLs
onto a plate in Bambu Studio as they are. The README says what to do with
them.

## Buy

| qty | item |
|---|---|
| **16** | **M6 × 12 button head** |
| **4** | **M6 nut** (DIN 934, 10 mm across the flats, 5 mm thick) |
| **12** | **M6 washer** (DIN 125 form A, ⌀12.5, 1.6 thick) |

That is for one bracket. One screw length does for all of it.

| qty | where | nut | washer |
|---|---|---|---|
| 12 | bracket to rack: 3 per ear, 4 ears | none — in the post | yes |
| 4 | faceplate, through the front ears | 4 × M6 | no |

The twelve rack screws need no nuts: the Lab Rax posts already hold them. The
side and the rear leg take no screw, because the side's tongue slides into
the leg's groove, and neither does the tray, whose halves are keyed by four
pegs.

**The twelve washers are not optional.** Every one of the rack screws goes
through a slot 6.6 mm wide, and an M6 button head is 10.5 across. Without a
washer the head lands on two thin crescents beside the slot, about 25 mm² of
PETG, and tightening will bury it. A ⌀12.5 washer spreads that to 46–60 mm²,
which is what the four faceplate screws, in round counterbored holes, already
have.

### Why 12 mm

The binding constraint is the rack post. Its equipment hole is **blind at
6 mm**: 2 mm of ⌀7.6 clearance, then a 4 mm hex pocket holding the nut. A
screw that goes in more than 6 mm past the ear hits the end of the hole and
never clamps; one that goes in less than about 5 mm barely catches the nut.

That fixes the ear thickness. At **6.5 mm**, a 12 mm screw enters the post
5.5 mm — half a millimetre clear of the bottom — with 3.5 mm of thread in the
nut. Thicker ears and the screw cannot reach; thinner and it bottoms out.

The faceplate is arranged around the same screw:

| joint | how it is made to fit | thread in the nut |
|---|---|---|
| rack | ear 6.5 mm, into the post's own nut | 3.5 mm |
| faceplate | head sunk 1 mm into the ear, nut 1.5 mm behind the plate's front face | 5.0 mm |

`make verify` checks both on every build: that each screw reaches its nut
with at least 3 mm of thread, and that the rack screw does not bottom out.
`make assembly` goes further and puts a real screw, nut and washer at all
sixteen positions, reporting the seat area under each head.
