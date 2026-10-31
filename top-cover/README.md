# Top cover

A vented top cover for the [Lab Rax 10" rack](https://makerworld.com/en/models/1464819-lab-rax-10-server-rack-bolted-version-5u),
in two halves that each print on a Bambu Lab A1 mini, bolted together under
the seam by the rack's own post joiner.

It takes the place of the rack's top panel: the same 228.05 × 171.5 × 3 mm,
cut on the centreline like the rack's own Bottom Panel Halves, and seated by
its edges in the top frame's grooves.

| | |
|---|---|
| vents | two 92 mm fan grilles, honeycomb, 56 cells each, ~31 cm² open, with screw holes on a 92 mm fan's 82.5 mm square should you fit fans under them |
| joint | two post joiners under the seam, between the grilles, each an M6 into each half |
| logo  | optional, raised 0.6 mm in two colours on the front half — see [The logo](#the-logo) |

## What to print

| file | plates | filament, time |
|---|---|---|
| `TopCover_LabRax-A1mini.3mf` | 1: left half + a joiner, 2: right half + a joiner | 87.4 g, 3 h 29 |
| `TopCover_Skynet_LabRax-A1mini.3mf` | the same, with the logo — made locally, see below | ~98 g, 4 h 13, three colours |

Figures from a real Bambu Studio slice of each file, PETG at 0.2 mm. The
halves print top up and flat, the joiners flat face down so their nut traps
open upward; neither needs support.

## Hardware

- 4 × M6 × 12 button head screws
- 4 × M6 nuts
- 4 × M6 washers, optional, under the heads

## Assembly

1. Drop an M6 nut into each trap of the two joiners.
2. Lay the two halves face down, butted on the seam.
3. Set each joiner over the seam, flat face down on the halves, its holes over
   the halves' holes — the nut traps facing you.
4. From the top, a screw through each hole into its nut. Tighten.
5. Seat the cover in the rack's top frame as you would the rack's own panel.

The joiners sit under the seam between y = 8.7 and 59.5 mm from the middle of
the panel, inside the 120 mm the rack's own panel joint uses, so they clear
the frame's front and back members.

## The logo

The cover can carry Krafty3D's "Skynet Logo - Plate (Terminator)" artwork,
from MakerWorld, on its front half. That artwork is under MakerWorld's Standard Digital
File License — fine to print for yourself, not to share — so **it is not in
this repository**. To build the cover with it:

1. Download the project from MakerWorld and put it at
   `top-cover/assets/Skynet.3mf`.
2. `make cover`

The build reads the artwork's pieces straight out of the 3MF, scales them to
fit the band in front of the grilles (0.695 ×, 98.9 × 68.2 mm), raises them
0.6 mm above the cover, and splits the few that cross the seam between the
two halves. A 0.4 mm nozzle cannot lay a line much under 0.45 mm, so pieces
that would come out thinner are left out: at any scale that fits, that is the
red CYBERDYNE SYSTEMS CORPORATION line and the comma in the white one. The
thinnest line kept is 0.49 mm.

It writes `TopCover_Skynet_LabRax-A1mini.3mf`, with the logo as parts of each
half on filaments 2 (white) and 3 (red) and the cover on filament 1, and a
FreeCAD document with it in. All of it is ignored by git.

## Building

    make cover

runs `top-cover/build.py` in FreeCAD — the FreeCAD document, STEP and STLs,
and 33 checks: every part one valid solid that fits the bed, the cover the
rack panel's size, each bolt clear through panel and joiner into its trap, the
joiners inside the clear run under the seam, the panel solid over them, and
the logo printable, in its band and on its own half — then
`top-cover/plate_cover.py` for the 3MFs.

Everything is set in `top-cover/cover.py`.

## Credits

- The **post joiner** is the Lab Rax rack's own Bolted Version Post Joiner by
  mklements, drawn again to its dimensions: 39.7 × 23.85 × 7, two M6 nut traps
  20 mm apart. It matches the original's mesh to 0.03% of its volume.
- **Where the vents go** follows Flying4T's "Lab Rax - Top Dual 92mm or 80mm
  Fan Panel" on MakerWorld (CC BY-NC-SA): two 92 mm fans 110 mm
  apart toward one end. The grille here is its own; that panel's is not used.
- The **logo** is Krafty3D's, used as described above and not distributed.
