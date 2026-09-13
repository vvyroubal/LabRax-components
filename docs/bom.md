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
| `export/3mf/UCG_Fiber_LabRax-A1mini.3mf` | 1–3 chassis, 4–6 UCG-Fiber | 258.9 g, 10 h 48 |
| `export/3mf/USW_Flex_LabRax-A1mini.3mf` | 1–3 chassis, 4–6 USW-Flex | 244.8 g, 10 h 28 |
| `export/3mf/TL_SG108E_LabRax-A1mini.3mf` | 1–3 chassis, 4–6 TL-SG108E | 252.1 g, 10 h 44 |

Every plate carries its own label in Bambu Studio — `Chassis 2 of 3 - right
side`, `UCG-Fiber 3 of 3 - faceplate` — so the tab tells you which kit a plate
belongs to without reference to this table.

| kit | parts | filament | time |
|---|---|---|---|
| chassis | `side_l`, `side_r`, `leg_l`, `leg_r` | 109.2 g | 5 h 28 |
| UCG-Fiber | `tray_ucg_l`, `tray_ucg_r`, `faceplate_ucg` | 149.7 g | 5 h 20 |
| USW-Flex-2.5G-5 | `tray_usw_l`, `tray_usw_r`, `faceplate_usw` | 135.7 g | 5 h 00 |
| TL-SG108E | `tray_sg108e_l`, `tray_sg108e_r`, `faceplate_sg108e` | 142.9 g | 5 h 16 |

**If you are building both**, print the chassis once — the three chassis
plates are identical in the two files.

Chassis plus one device is about **259 g / 10 h 48** for the gateway, or
**245 g / 10 h 28** for the switch. All nine plates, 394.6 g.

| plate | part | size (mm) | filament | time | support |
|---|---|---|---|---|---|
| 1 | `side_l` | 33 × 212.5 × 44.5 | 35.3 g | 1 h 56 | yes |
| 2 | `side_r` | 33 × 212.5 × 44.5 | 35.3 g | 1 h 56 | yes |
| 3 | `leg_l` + `leg_r` | 33 × 97.5 × 44.5 each | 38.6 g | 1 h 54 | yes |
| 4 | `tray_ucg_l` | 137 × 131.6 × 9 | 49.2 g | 1 h 45 | yes |
| 5 | `tray_ucg_r` | 137 × 131.6 × 9 | 57.5 g | 2 h 07 | yes |
| 6 | `faceplate_ucg` | 214 × 20 × 44.5 | 43.0 g | 1 h 46 | no |
| 4* | `tray_usw_l` | 137 × 94 × 19.6 | 41.4 g | 1 h 34 | yes |
| 5* | `tray_usw_r` | 137 × 94 × 19.6 | 54.2 g | 2 h 02 | yes |
| 6* | `faceplate_usw` | 214 × 20 × 44.5 | 40.1 g | 1 h 42 | no |

| 4† | `tray_sg108e_l` | 137 × 105 × 17.8 | 46.7 g | 1 h 37 | yes |
| 5† | `tray_sg108e_r` | 137 × 105 × 17.8 | 58.7 g | 2 h 05 | yes |
| 6† | `faceplate_sg108e` | 214 × 20 × 44.5 | 37.5 g | 1 h 34 | no |

\* in `USW_Flex_LabRax-A1mini.3mf`, † in `TL_SG108E_LabRax-A1mini.3mf`; the
rows with neither mark are in `UCG_Fiber_LabRax-A1mini.3mf`. Plates 1–3 are
the same chassis in all three.

PETG, 0.2 mm layers, and the plated 3MF already carries the orientations and
the per-part support and brim settings — see
[print-settings.md](print-settings.md).

## Keep what you already printed

**The sides are the only parts that have not changed.** `side_l` and `side_r`
are still byte-identical to the STLs published with "One faceplate instead of
two bars" (`50ea387`). If yours came from that version or later, reprint the
two trays, the two legs and the faceplate — about 188 g and 7 h 14. Only the
two sides carry over.

The gateway's tray and faceplate were renamed when the switch was added --
`tray_l` is now `tray_ucg_l`, `faceplate` is `faceplate_ucg` -- but the
geometry is byte-for-byte what it was. Plate numbers 1 to 6 are unchanged, so
anything already quoted against them still means the same thing.

| part | verdict |
|---|---|
| `side_l`, `side_r` | **keep**, if printed since `50ea387` |
| `leg_l`, `leg_r` | **reprint, both** — 11 mm shorter, and slotted so the splice adjusts twice as far |
| `faceplate` | **reprint** — the oval moves up: its top edge now sits 7.0 mm below the top bar |
| `tray_l`, `tray_r` | **reprint, both** — centre bolt tab deleted, four pegs instead of two, rear lip added |
| `top_bar`, bottom bar | **gone** — replaced by the faceplate |

**Reprint the trays as a pair.** An old half will not mate with a new one:
the old pair has two pegs and the bolt tab, the new pair has four pegs, no tab
and the rear lip. About 107 g and 3 h 50 for the two.

### Which sides do you have?

Two things tell them apart without a calliper on anything subtle:

- **The ear.** Measure from the outer edge of the ear inwards to where it
  stops. Current sides: **33 mm**. The older ones: **29 mm** — their ears
  reached in only to x = ±98 rather than ±94.
- **The notch.** The older sides have notches cut in the front for a separate
  top bar and bottom bar. The current ones have **none** — the faceplate stops
  at the rail's inner face instead.

If yours are the older ones you need the sides, legs and faceplate too, since
those sides expect two bars that no longer exist.

The tray-to-side joint itself has not moved: the new trays were tested against
the pre-faceplate sides and share 0.0 mm³ with them, sitting on the same
3096 mm³ of ledge. It is the rest of the assembly that would stop you, not the
tray.

## Buy

| qty | item |
|---|---|
| **20** | **M6 × 12 button head** |
| **8** | **M6 nut** (DIN 934, 10 mm across the flats, 5 mm thick) |
| **16** | **M6 washer** (DIN 125 form A, ⌀12.5, 1.6 thick) |

One screw length for the whole bracket. The twelve rack screws need no nuts —
the Lab Rax posts already hold them.

| qty | where | nut | washer |
|---|---|---|---|
| 12 | bracket to rack: 3 per ear, 4 ears | none — in the post | yes |
| 4 | faceplate, through the front ears | 4 × M6 | no |
| 4 | side to rear leg, through the splice slots | 4 × M6 | yes |

**The sixteen washers are not optional.** Every one of those screws goes
through a slot — 6.6 mm wide for the rack, 6.4 for the splice — and an M6
button head is 10.5 across. Without a washer the head lands on two thin
crescents beside the slot, about 25 mm² of PETG, and tightening will bury it.
A ⌀12.5 washer spreads that to 46–60 mm², which is what the six screws in
round counterbored holes already have.

`make assembly` measures this: it puts a real screw, nut and washer at all
twenty positions and reports the seat area at each.

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
| faceplate | head sunk 1 mm into the ear | 3.5 mm |
| side to leg | nothing — it already fitted | 5.8 mm |

The tray's two halves are not on this list: they take no fastener at all. The
tab that used to carry one hung off a 10 x 3 mm neck with the bolt 6.5 mm
above it, so nearly all the preload arrived as bending; CalculiX put it at
26 N against roughly 1700 N from an M6 at 2 N·m, and both tabs duly snapped
off on first tightening. The halves are now keyed by four ⌀5 pegs and held by
their 60 mm lap, the rails, the faceplate and the rear stops — see
[measurements.md](measurements.md).

The 1 mm counterbore for the faceplate screws is worth noticing: the
alternative was moving the nut 1 mm further back, into an 8 mm plate that
already has a window through it. Taking the millimetre out of the ear instead
keeps the nut pocket clear of the window.

`make verify` checks all of them, on every build: that each screw reaches its nut
with at least 3 mm of thread, and that the rack screw does not bottom out.
