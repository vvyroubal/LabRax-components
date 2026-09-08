# Printing

Sliced for a **Bambu Lab A1 mini** (180 × 180 × 180).

```sh
make plate      # export/3mf/UCG_Fiber_LabRax-A1mini.3mf
```

That file is a full Bambu Studio project: two plates, parts rotated into the
orientation they print in, supports already switched on for the two ears, and
the A1 mini presets carried with it. Everything sits at least 3 mm from the bed
edge.

| plate | parts | filament |
|---|---|---|
| 1 | `tray` — 172 × 152 mm, it fills the bed on its own | 59.9 g |
| 2 | `ear_l`, `ear_r` | 74.9 g |
| 3 | `top_bar`, `stop_l`, `stop_r` | 18.9 g |

Figures are from slicing it with Bambu Studio 2.8.2.61 at its stock
`0.20mm Standard @BBL A1M`. Both plates return `Success` with no warnings and
every object reports as manifold.

### It has to be a project, not just geometry

A 3MF carrying only meshes and a `model_settings.config` is not enough. Bambu
Studio answers **"The 3mf file has invalid config, load geometry data only"**
and drops the plates and the per-object settings on the floor. What it wants
is a complete `Metadata/project_settings.config`; `tools/a1mini_project.json`
is one, taken from the stock Lab Rax rack project, and `tools/plate.py` embeds
it. It carries the A1 mini presets and five filament slots — change the
filament to taste once it is open.

Two flags matter when checking this from the command line:

```sh
bambu-studio --arrange 0 --export-3mf out.3mf in.3mf   # keep the placement
bambu-studio --arrange 0 --slice 0 --outputdir /tmp in.3mf
```

Without `--arrange 0` the CLI re-arranges everything on load whatever the file
says, which makes it look as though the plating had been ignored.

The CLI will not slice a project with more than one plate — every plate after
the first comes back "some objects are located over the boundary of the heated
bed", and Bambu Studio's *own* exports fail the same way, so it is the CLI and
not the file. The GUI is fine with it; the stock Lab Rax rack project has
eleven plates. To check the geometry from the command line, build a one-plate
file per plate and slice those, which is what was done for the figures above.

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
| Supports | none needed |
| Brim | 5 mm on `tray`, which is 172 mm of thin flat plate |

## Orientation

All of this is already applied in the plated 3MF; it matters only if you plate
the STLs yourself.

- `tray` — floor down. Flat, 8 mm tall, no overhangs.
- `top_bar` — **upside down**. The right way up, its rear flange starts
  2.8 mm above the bed with nothing beneath it; inverted, the flat face that
  is the top of the 1U lies on the bed and everything builds upward.
- `ear_l` / `ear_r` — standing on the floor face, turned 90° in plan to fit
  the bed. **These need support** — see below.
- `stop_l` / `stop_r` — as modelled. Upright and foot both start at the floor
  line, so the part builds straight off the bed. It is tall for its footprint,
  so give it a brim. The hold-down flange is a 3 mm overhang, short enough to
  bridge.

With those orientations and support on the ears, Bambu Studio slices both
plates with no warnings at all.

## The ears need support

Printed floor-down, an ear grows a 200 mm² ledge that starts in mid-air at
z = 34 mm and reaches 32 mm inboard. It is the part of the faceplate above the
window: the window is 26 mm of empty space directly beneath it, and the only
full-height material to build up from is the faceplate outboard of x = ±104.
Bambu Studio flags it as a "floating cantilever".

The support column stands inside the window opening and lifts straight out, so
this costs a little filament and no finished surface. `tools/plate.py` turns it
on for both ears.

The alternative is a design change: extend `top_bar` out to x = ±112, where the
ear is full height, so the ear carries no faceplate above the window at all.
That needs `top_bar` split into two lapped halves, because at 224 mm it no
longer fits the bed. Worth doing if you would rather not print supports.

Print **one ear first** and offer it up to the rack before committing to the
rest. The 0.925 mm per side between the side rails and the posts is the
tightest dimension in the design, and a printed rack's post spacing varies.

## Fit adjustment

Everything is in `src/params.py`; rebuild with `make`.

| symptom | change |
|---|---|
| Device is a tight push fit | raise `CLR_W` from 1.2 |
| Ears will not pass between the posts | lower `RAIL_T` from 3.2 |
| Rack screws will not line up | raise `SLOT_W` from 11.0 |
| Device rattles vertically | lower `CLR_H` from 0.8 |
