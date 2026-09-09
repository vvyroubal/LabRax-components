# Printing

Sliced for a **Bambu Lab A1 mini** (180 × 180 × 180).

```sh
make plate      # export/3mf/UCG_Fiber_LabRax-A1mini.3mf
```

That file is a full Bambu Studio project: four plates, parts rotated into the
orientation they print in, supports already switched on where they are needed,
and the A1 mini presets carried with it. Everything sits at least 4 mm from
the bed edge.

| plate | parts | filament |
|---|---|---|
| 1 | `side_l` | 36.7 g |
| 2 | `side_r` | 36.7 g |
| 3 | `tray_l`, `top_bar_l` | 57.5 g |
| 4 | `tray_r`, `top_bar_r` | 61.3 g |

About 192 g and eight or nine hours all told. Figures are from slicing with
Bambu Studio 2.8.2.61 at its stock `0.20mm Standard @BBL A1M`; every plate
returns `Success` with no warnings.

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
| Brim | 5 mm, which the stock profile puts on automatically |

## Orientation

All of this is already applied in the plated 3MF; it matters only if you plate
the STLs yourself.

- `side_l` / `side_r` — as exported, standing on the rail's bottom edge. At
  192 mm long a side only fits the bed turned 45°. **Needs support**: the
  ledge the tray lands on stands 3 mm off the bed on a 11 mm arm.
- `tray_l` / `tray_r` — flat, as exported. **Needs support**: the lap strip
  along each edge stands 3 mm off the bed so it can land on the side's ledge.
  The support is a thin rim on the underside and comes away cleanly.
- `top_bar_l` / `top_bar_r` — **upside down**, and turned 90° in plan to fit
  beside the tray. The right way up, the bar's rear flange starts 2.8 mm above
  the bed with nothing beneath it; inverted, the flat face that is the top of
  the 1U lies on the bed and everything builds upward.

Print **one side first** and offer it up to the rack before committing to the
rest. The 0.925 mm per side between the side rails and the posts is the
tightest dimension in the design, and a printed rack's post spacing varies.

## Fit adjustment

Everything is in `src/params.py`; rebuild with `make`.

| symptom | change |
|---|---|
| Device is a tight push fit | raise `CLR_W` from 1.2 |
| Sides will not pass between the posts | lower `RAIL_T` from 3.2 |
| Rack screws will not line up | raise `SLOT_W` from 11.0 |
| Rear ears miss the rear posts | change `RACK_D` from 175.9 |
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
  `Metadata/project_settings.config`; `tools/a1mini_project.json` is one, and
  `tools/plate.py` embeds it.
- **"G-code conflicts detected after slicing"** — either a prime tower has
  landed on a part, or two parts' 5 mm brims have run into each other. The
  project is cut to a single PETG slot with the tower off, and the plater
  keeps parts 12 mm apart.
- **"One of the plate is empty…"** or **"some objects are located over the
  boundary of the heated bed"** — the plate grid. Plates sit two to a row,
  216 mm apart; land outside it and parts are silently dropped or measured
  against the wrong origin. See `plate_origin()` in `tools/plate.py`.

The CLI will not slice a project with more than two plates. To check the
geometry, build a one-plate file per plate and slice those, which is what was
done for the figures above.
