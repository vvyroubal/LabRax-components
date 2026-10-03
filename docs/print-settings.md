# Printing

Sliced for a **Bambu Lab A1 mini** (180 × 180 × 180).

```sh
make plate      # one 3MF in each device's folder
```

That file is a full Bambu Studio project: five plates, parts rotated into the
orientation they print in, supports already switched on where they are needed,
and the A1 mini presets carried with it. Everything sits at least 4 mm from
the bed edge.

| plate | parts | filament |
|---|---|---|
| 1 | `side_l` | 36.7 g |
| 2 | `side_r` | 36.7 g |
| 3 | `tray_l` | 52.5 g |
| 4 | `tray_r` | 60.6 g |
| 5 | `top_bar` | 33 g |

About 208 g all told. Figures are from slicing with
Bambu Studio 2.8.2.61 at its stock `0.20mm Standard @BBL A1M`; every plate
returns `Success` with no warnings.

## Is it really printable?

Fitting the bed is not the same as printing inside it: support does not stay
within the part it holds up, and on the trays it reaches about 5 mm past the
overhanging edge. `common/tools/plate.py` only knows where the parts sit.

```sh
make plates     # slices all five and measures the toolpaths
```

That writes each plate out on its own, slices it with Bambu Studio, and reads
the extents back out of the G-code, ignoring the machine's own prime routine
(the A1 mini primes at X = -13.5, outside the bed and none of our business).
Measured:

| plate | X printed | Y printed | max Z | nearest edge |
|---|---|---|---|---|
| `side_l` | 12.20 – 169.62 | 12.20 – 167.80 | 44.40 | 10.4 mm |
| `side_r` | 12.20 – 167.80 | 10.38 – 167.80 | 44.40 | 10.4 mm |
| `tray_l` | 19.01 – 158.29 | 9.21 – 175.79 | 16.00 | 4.2 mm |
| `tray_r` | 19.01 – 160.99 | 4.25 – 175.79 | 16.00 | 4.2 mm |
| `top_bar` | 6.43 – 173.57 | 6.43 – 173.57 | 20.80 | 6.4 mm |

Everything is inside 180 × 180 × 180. The trays are the tight ones — 167 mm
deep on a 180 mm bed, with support spreading past the front edge — which is
why they are placed 2.5 mm back of centre and print without a brim.

## Material

**PETG.** The UCG-Fiber is fanless and dissipates its heat through the case;
with IDS/IPS running it gets warm enough that PLA creeping under the load of a
734 g device is a real risk. ASA or PC are fine too. PLA will work in a cool
room but is not the right choice here.

## Settings

| | |
|---|---|
| Layer height | 0.2 mm |
| Walls | 4 (the side rails are 3.2 mm — this makes them solid) |
| Infill | 25 %, gyroid |
| Brim | 5 mm from the stock profile; turned off for the trays, which are large flat faces and would otherwise reach the edge of the plate |

## Orientation

All of this is already applied in the plated 3MF; it matters only if you plate
the STLs yourself.

- `side_l` / `side_r` — as exported, standing on the rail's bottom edge. At
  192 mm long a side only fits the bed turned 45°. **Needs support**: the
  ledge the tray lands on stands 3 mm off the bed on a 11 mm arm.
- `tray_l` / `tray_r` — flat, as exported. **Needs support**: the lap strip
  along each edge stands 3 mm off the bed so it can land on the side's ledge.
  The support is a thin rim on the underside and comes away cleanly.
- `top_bar` — **upside down and turned 45°**. At 220 mm it only fits the bed
  cornerwise, and inverted the face that was the top of the 1U lies flat on
  the bed: full contact, no support, no brim. The right way up, its
  rear flange starts 2.8 mm above
  the bed with nothing beneath it; inverted, the flat face that is the top of
  the 1U lies on the bed and everything builds upward.

Print **one side first** and offer it up to the rack before committing to the
rest. The 0.925 mm per side between the side rails and the posts is the
tightest dimension in the design, and a printed rack's post spacing varies.

## Fit adjustment

Everything is in `common/src/params.py`; rebuild with `make`.

| symptom | change |
|---|---|
| Device is a tight push fit | raise `CLR_W` from 1.2 |
| Sides will not pass between the posts | lower `RAIL_T` from 3.2 |
| Rack screws will not line up | raise `SLOT_W` from 11.0 |
| Side will not slide into its leg, or rattles in it | raise or lower `RUN_FIT` from 0.25 — try it on the two coupons in `common/stl/` first |
| Faceplate is tight between the sides | raise `PLATE_FIT` from 0.2 |
| Tray is tight between the rails | raise `TRAY_SIDE_FIT` from 0.2 |
| Tray halves will not close on each other | raise `LAP_FIT` from 0.3, `KEY_FIT` from 0.5 |
| Device rattles vertically | lower `CLR_H` from 0.8 |

## Checking a 3MF from the command line

Two flags matter:

```sh
bambu-studio --arrange 0 --export-3mf out.3mf in.3mf   # keep the placement
bambu-studio --arrange 0 --slice 0 --outputdir /tmp in.3mf
```

Without `--arrange 0` the CLI re-arranges everything on load whatever the file
says, which makes it look as though the plating had been ignored.

Three things bite, none of which say what they mean:

- **"The 3mf file has invalid config, load geometry data only"** — the file is
  not a project. Bambu Studio keeps the meshes and throws the plates and the
  per-object settings away. It wants a complete
  `Metadata/project_settings.config`; `common/tools/a1mini_project.json` is one, and
  `common/tools/plate.py` embeds it.
- **"G-code conflicts detected after slicing"** — either a prime tower has
  landed on a part, or two parts' 5 mm brims have run into each other. The
  project is cut to a single PETG slot with the tower off, and the plater
  keeps parts 12 mm apart.
- **"One of the plate is empty…"** or **"some objects are located over the
  boundary of the heated bed"** — the plate grid. Plates sit two to a row,
  216 mm apart; land outside it and parts are silently dropped or measured
  against the wrong origin. See `plate_origin()` in `common/tools/plate.py`.

The CLI will not slice a project with more than two plates. To check the
geometry, build a one-plate file per plate and slice those, which is what was
done for the figures above.
