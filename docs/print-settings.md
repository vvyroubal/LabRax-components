# Printing

Sliced for a **Bambu Lab A1 mini** (180 × 180 × 180). Every part is modelled in
the orientation it prints in — floor down, faceplate standing at the front — so
the STLs need no rotating.

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

- `tray` — as exported. Flat, 8 mm tall, no overhangs.
- `top_bar` — as exported.
- `ear_l` / `ear_r` — as exported, standing on the floor face. The rack ear is
  a vertical plate; the side rail's top lip is a 4 mm overhang at 36.8 mm, which
  bridges cleanly at 0.2 mm layers. If your printer struggles with it, a 45°
  chamfer under the lip is a one-line change in `src/model.py`.
- `stop_l` / `stop_r` — as exported.

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
