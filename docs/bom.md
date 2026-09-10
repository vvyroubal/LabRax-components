# What to print, what to keep, what to buy

Everything here is measured off the built solids or read out of a real slice —
nothing is estimated. Regenerate the print figures with `make plates`, and the
screw lengths with the arithmetic set out at the bottom.

## Print

Seven plates, eight parts, about **248 g** and **11½ hours** in total.

| plate | part | size (mm) | filament | time | support |
|---|---|---|---|---|---|
| 1 | `side_l` | 29 × 214 × 44.5 | 34.7 g | 1 h 54 | yes |
| 2 | `side_r` | 29 × 214 × 44.5 | 34.7 g | 1 h 54 | yes |
| 3 | `leg_l` + `leg_r` | 29 × 110 × 44.5 each | 40.8 g | 1 h 59 | yes |
| 4 | `tray_l` | 137 × 159 × 16 | 51.3 g | 1 h 56 | yes |
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
| `side_l`, `side_r` | reprint | 22 mm longer, rear ear removed, splice slots added, ledge nib gone, ears chamfered |
| `tray_l`, `tray_r` | reprint | 8 mm shorter at the front — the bottom bar occupies that space now — and the locating pegs moved back into the lap |
| `leg_l`, `leg_r` | print | new: they carry the rear ears to the back posts |
| `bottom_bar` | print | new |

So of the five parts on your bench, **one is still good**. That leaves
**7 plates minus plate 6** — about 230 g and 10½ hours.

The old sides and trays are not adjustable into the new ones; the sides are
short by the amount that put them 27 mm clear of the rear posts, and the trays
would foul the bottom bar.

## Buy

**22 × M6 screws and 10 × M6 nuts.** The twelve rack screws need no nuts — the
Lab Rax posts already hold them.

| qty | size | where | nut |
|---|---|---|---|
| 12 | **M6 × 14** | bracket to rack: 3 per ear, 4 ears | none — in the post |
| 2 | **M6 × 16** | top bar, through each front ear | 2 × M6 |
| 2 | **M6 × 16** | bottom bar, through each front ear | 2 × M6 |
| 2 | **M6 × 20** | tray halves to each other, at the rear tab | 2 × M6 |
| 4 | **M6 × 12** | side to rear leg, through the splice slots | 4 × M6 |

Button heads everywhere except the four splice screws, whose heads sit against
the outside of the rail where nothing sees them. All nuts are plain M6 (DIN
934, 10 mm across the flats, 5 mm thick) — the same nut the rack itself uses.

### Where the lengths come from

Measured under the head, from the geometry:

- **Rack, 14 mm.** 8 mm of ear, then the post: 2 mm of ⌀7.6 clearance, then
  its hex pocket from 2 to 6 mm. The hole is **blind at 6 mm**, so 8 + 6 = 14
  is both what full engagement needs and the longest that will go in. An
  M6 × 16 bottoms out on the end of the hole and never clamps; an M6 × 12
  leaves 2 mm of thread in the nut, which is two turns.
- **Bars, 16 mm.** 8 mm of ear, 3 mm of bar before the nut pocket, 5 mm of
  nut. Behind the top bar's nut is the flange, so 16 is also the maximum.
- **Tray, 20 mm.** 10 mm through the left half's tab, 2 mm to the slot, 5 mm
  of nut; 20 puts the tip level with the far face of the right half's tab.
- **Splice, 12 mm.** 3.2 mm of rail, 3.4 mm of boss, 5 mm of nut.

### One thing worth changing first

**M6 × 14 is an awkward size to buy**, and it is forced by the ears being 8 mm
thick against a post hole only 6 mm deep. Lab Rax's own faceplates are 4.5 mm
and its documentation calls for M6 × 10 throughout.

Thinning the ears to **5 mm** would make the rack screws **M6 × 10** and the
bar screws **M6 × 12** — both stock sizes, both what you probably already have
from building the rack. It costs nothing to do now, because the sides and legs
are being reprinted anyway. It would take the front reveal from 8 mm to 5 mm,
still even all the way round.
