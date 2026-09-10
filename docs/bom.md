# What to print, what to keep, what to buy

Everything here is measured off the built solids or read out of a real slice —
nothing is estimated. Regenerate the print figures with `make plates`, and the
screw lengths with the arithmetic set out at the bottom.

## Print

Seven plates, eight parts, about **247 g** and **11½ hours** in total.

| plate | part | size (mm) | filament | time | support |
|---|---|---|---|---|---|
| 1 | `side_l` | 29 × 212.5 × 44.5 | 34.9 g | 1 h 55 | yes |
| 2 | `side_r` | 29 × 212.5 × 44.5 | 34.8 g | 1 h 56 | yes |
| 3 | `leg_l` + `leg_r` | 29 × 108 × 44.5 each | 38.6 g | 1 h 55 | yes |
| 4 | `tray_l` | 137 × 159 × 16 | 51.5 g | 1 h 57 | yes |
| 5 | `tray_r` | 137 × 159 × 16 | 58.8 g | 2 h 18 | yes |
| 6 | `top_bar` | 220 × 20 × 21 | 18.1 g | 55 m | no |
| 7 | `bottom_bar` | 220 × 8 × 21 | 10.1 g | 40 m | no |

PETG, 0.2 mm layers, and the plated 3MF already carries the orientations and
the per-part support and brim settings — see
[print-settings.md](print-settings.md).

## Keep what you already printed

Comparing the STLs you printed against the current ones, byte for byte:

| part | verdict | why |
|---|---|---|
| `top_bar` | **keep** | identical, not touched since |
| `side_l`, `side_r` | reprint | 21 mm longer, rear ear removed, splice slots added, ledge nib gone, ears chamfered and thinned to 6.5 mm |
| `tray_l`, `tray_r` | reprint | 8 mm shorter at the front — the bottom bar occupies that space now — and the locating pegs moved back into the lap |
| `leg_l`, `leg_r` | print | new: they carry the rear ears to the back posts |
| `bottom_bar` | print | new |

So of the five parts on your bench, **one is still good**. That leaves
**7 plates minus plate 6** — about 229 g and 10½ hours.

The old sides and trays are not adjustable into the new ones; the sides are
short by the amount that put them 27 mm clear of the rear posts, and the trays
would foul the bottom bar.

## Buy

| qty | item |
|---|---|
| **22** | **M6 × 12 button head** |
| **10** | **M6 nut** (DIN 934, 10 mm across the flats, 5 mm thick) |
| **16** | **M6 washer** (DIN 125 form A, ⌀12.5, 1.6 thick) |

One screw length for the whole bracket. The twelve rack screws need no nuts —
the Lab Rax posts already hold them.

| qty | where | nut | washer |
|---|---|---|---|
| 12 | bracket to rack: 3 per ear, 4 ears | none — in the post | yes |
| 2 | top bar, through each front ear | 2 × M6 | no |
| 2 | bottom bar, through each front ear | 2 × M6 | no |
| 2 | tray halves to each other, at the rear tab | 2 × M6 | no |
| 4 | side to rear leg, through the splice slots | 4 × M6 | yes |

**The sixteen washers are not optional.** Every one of those screws goes
through a slot — 6.6 mm wide for the rack, 6.4 for the splice — and an M6
button head is 10.5 across. Without a washer the head lands on two thin
crescents beside the slot, about 25 mm² of PETG, and tightening will bury it.
A ⌀12.5 washer spreads that to 46–60 mm², which is what the six screws in
round counterbored holes already have.

`make assembly` measures this: it puts a real screw, nut and washer at all
twenty-two positions and reports the seat area at each.

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
| top and bottom bar | head sunk 1 mm into the ear | 3.5 mm |
| tray halves | head sunk 5 mm into the left tab | 5.0 mm |
| side to leg | nothing — it already fitted | 5.8 mm |

The 1 mm counterbore for the bar screws is worth noticing: the alternative was
moving the nut 1 mm forward in the bar, which would have made every top bar
already printed wrong. Taking the millimetre out of the ear instead — a part
that had to be reprinted anyway — leaves the bar untouched.

`make verify` checks all five, on every build: that each screw reaches its nut
with at least 3 mm of thread, and that the rack screw does not bottom out.
