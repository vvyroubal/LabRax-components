# Printing

Sliced for a **Bambu Lab A1 mini** (180 × 180 × 180).

```sh
make plate      # export/3mf/UCG_Fiber_LabRax-A1mini.3mf
```

That file is plated and ready to open in Bambu Studio: two plates, parts
rotated into the orientation they print in, and supports already switched on
for the two ears. Everything sits at least 3 mm from the bed edge.

| plate | parts |
|---|---|
| 1 | `tray` — 172 × 149 mm, it fills the bed on its own |
| 2 | `ear_l`, `ear_r`, `top_bar`, `stop_l`, `stop_r` |

Verified by slicing it headlessly with Bambu Studio 2.8.2.61: both plates
return `Success`, and every object reports as manifold.

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
- `top_bar` — as exported, flat.
- `ear_l` / `ear_r` — standing on the floor face, turned 90° in plan to fit.
  **These need support** — see below.
- `stop_l` / `stop_r` — laid on their backs, so the upright is loaded across
  the layers rather than being peeled apart.

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
