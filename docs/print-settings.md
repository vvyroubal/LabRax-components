# Printing

Everything is plated for a **Bambu Lab A1 mini** (180 × 180 × 180 mm).

Each device's folder holds one 3MF. It is a full Bambu Studio project: six
plates, every part already turned the way it prints, supports and brims set
per part, and the A1 mini presets carried with it. Open it and print.

| plate | parts |
|---|---|
| 1 | `side_l` |
| 2 | `side_r` |
| 3 | `leg_l` and `leg_r` |
| 4 | the device's left tray half |
| 5 | the device's right tray half |
| 6 | the device's faceplate |

Filament and time for each plate are in [bom.md](bom.md).

## Material

**PETG.** The UCG-Fiber is fanless and dissipates its heat through its case;
with IDS/IPS running it gets warm enough that PLA creeping under a 734 g
device is a real risk. ASA or PC are fine too. PLA will work in a cool room
but is not the right choice here.

## Settings

The 3MFs carry Bambu Studio's stock `0.20mm Standard @BBL A1M` process with
`Generic PETG @BBL A1M`, and the figures in [bom.md](bom.md) are for exactly
that:

| | |
|---|---|
| Layer height | 0.2 mm |
| Walls | 2 |
| Infill | 15 %, grid |
| Brim | 5 mm, automatic; turned off for the trays and the faceplate |
| Support | on for the sides, the legs and the trays; off for the faceplate |
| Plate | textured PEI |

Sliced with Bambu Studio 2.8.2. Nothing stops you raising the wall count or
the infill in Bambu Studio before printing — four walls make the 3.2 mm side
rails solid — at the cost of more filament and time than the tables say.

## Orientation

All of this is already applied in the 3MFs. It matters only if you plate the
STLs yourself.

- **`side_l` / `side_r`** — standing on the rail's bottom edge, as exported,
  and turned 45°: at 212.5 mm a side only fits the bed cornerwise. Support
  is on, for the notch along the foot of the rail and the tops of the windows
  and slots.
- **`leg_l` / `leg_r`** — standing as exported, turned 90°, both on one
  plate. Support is on. The sprung catch at the foot of each leg prints flat
  on the bed, with the plate above it bridging a 1.2 mm slit: **check that
  slit is clear** when the print comes off, and pick out any support left in
  it, or the catch cannot move.
- **Tray halves** — flat, as exported, with no brim: they are large flat
  faces on the bed and a brim would reach the edge of the plate. Support is
  on, for the strip along each outer edge, which stands 3 mm off the bed so
  that it can land on the side's ledge, and under the right half's lap.
- **Faceplate** — stood on edge, **upside down**, and turned 45°. Lying flat
  it is 183 mm cornerwise and does not fit; on edge it is 165 mm and does.
  Upside down matters: the right way up, the flange that reaches back over
  the device is a 12 mm shelf hanging over nothing. Inverted, the flange lies
  on the bed and the part needs neither support nor brim.
- **Coupons** — standing as exported, like the side and leg they are cut
  from.

## Does it really fit the bed?

Fitting the bed is not the same as printing inside it: support and brim
reach past the part they belong to. `make plates` slices every plate with
Bambu Studio and reads the extents of what would actually be printed back out
of the G-code, ignoring the machine's own prime line.

| plate | X printed | Y printed | height | nearest bed edge |
|---|---|---|---|---|
| `side_l` | 9.4 – 172.5 | 6.1 – 174.0 | 44.4 | 6.0 mm |
| `side_r` | 6.0 – 173.9 | 7.5 – 170.6 | 44.4 | 6.0 mm |
| `leg_l` + `leg_r` | 42.0 – 138.0 | 38.7 – 141.3 | 44.4 | 38.7 mm |
| `tray_ucg_l` | 19.0 – 158.0 | 24.4 – 158.0 | 9.0 | 19.0 mm |
| `tray_ucg_r` | 19.0 – 161.0 | 24.4 – 160.6 | 9.0 | 19.0 mm |
| other tray halves | 19.0 – 161.0 | 21.9 – 158.1 | up to 19.6 | 19.0 mm |
| every faceplate | 7.7 – 172.3 | 7.7 – 172.3 | 44.4 | 7.7 mm |

Everything is inside 180 × 180 × 180. The sides are the tight ones.

## Fit adjustment

Printed fits depend on the printer. Every dimension is in
`common/src/params.py`; change it and rebuild with `make`.

| symptom | change |
|---|---|
| Side will not slide into its leg, or rattles in it | raise or lower `RUN_FIT` from 0.25 — try it on the two coupons in `common/stl/` first |
| Sides will not pass between the posts | lower `RAIL_T` from 3.2 |
| Rack screws will not line up | raise `SLOT_W` from 11.0 |
| Faceplate is tight between the sides | raise `PLATE_FIT` from 0.2 |
| Tray is tight between the rails | raise `TRAY_SIDE_FIT` from 0.2 |
| Tray halves will not close on each other | raise `LAP_FIT` from 0.3, `KEY_FIT` from 0.5 |
| Device is a tight push fit | raise `CLR_W` from 1.2 |
| Device rattles vertically | lower `CLR_H` from 0.8 |
| Catch is too stiff, or too weak | lengthen or shorten `CATCH_L` from 30 |
| Catch does not hold the frame | raise `CATCH_TOOTH` from 2.0 |
| Frame should draw out further before it stops | raise `CATCH_PULL` from 35; each millimetre leaves one less of tongue engaged |

## Slicing a 3MF from the command line

Two flags matter:

```sh
bambu-studio --arrange 0 --export-3mf out.3mf in.3mf   # keep the placement
bambu-studio --arrange 0 --slice 0 --outputdir out/ in.3mf
```

Without `--arrange 0` the CLI re-arranges everything on load whatever the
file says, which makes it look as though the plating had been ignored. It
also writes thumbnails and slice data back into the file it is given, so
slice a copy.

Three errors bite, none of which say what they mean:

- **"The 3mf file has invalid config, load geometry data only"** — the file
  is not a project. Bambu Studio keeps the meshes and throws the plates and
  the per-object settings away. It wants a complete
  `Metadata/project_settings.config`; `common/tools/a1mini_project.json` is
  one, and `common/tools/plate.py` embeds it.
- **"G-code conflicts detected after slicing"** — either a prime tower has
  landed on a part, or two parts' brims have run into each other. The project
  is cut to a single PETG slot with the tower off, and the plater keeps parts
  12 mm apart.
- **"Nothing to be sliced…"** or **"some objects are located over the
  boundary of the heated bed"** — the plate grid. Plates sit three to a row,
  216 mm apart each way; land outside that and parts are silently dropped or
  measured against the wrong origin. See `plate_origin()` in
  `common/tools/plate.py`.
