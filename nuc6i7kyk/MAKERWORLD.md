# MakerWorld listing: NUC6i7KYK_LabRax-A1mini.3mf

Text to post with `NUC6i7KYK_LabRax-A1mini.3mf`. Paste each part into the matching field.

## Title

Lab Rax 1U bracket for Intel NUC6i7KYK (Skull Canyon), A1 mini

## Summary

A 1U bracket that carries an Intel NUC6i7KYK (Skull Canyon) in a Lab Rax 10 inch rack, bolted to the front and rear posts, on a slotted tray that lets it breathe. Every part fits an A1 mini.

## Tags

Lab Rax, 10 inch rack, 1U, Intel NUC, NUC6i7KYK, Skull Canyon, rack mount, homelab, A1 mini

## Pictures

Isometric views from FreeCAD, in `images/`, 1200 x 1600 (3:4) on white:

1. `makerworld-nuc-assembled.png` — cover picture: the bracket with the
   device in place and all sixteen screws fitted.
2. `makerworld-nuc-empty.png` — the bracket without the device, showing the
   tray and the runners at the back.
3. `makerworld-nuc-exploded.png` — the seven printed parts and the device,
   drawn apart to show how they go together.

The device is shown as a plain translucent block the size of its case.

## Description

**A 1U bracket for the Intel NUC6i7KYK, "Skull Canyon", for a Lab Rax 10 inch rack.**

It bolts to the front and the rear posts, so the device is carried at four
points rather than hung off the front. It goes in like a drawer: two legs
bolt to the rear posts, and the rest is built on the bench and slid in from
the front. No screw has to be reached from inside the rack.

The rack itself is not included. It is the Lab Rax bolted 5U rack:
https://makerworld.com/en/models/1464819-lab-rax-10-server-rack-bolted-version-5u
and the rest of the system is in the Lab Rax collection:
https://makerworld.com/en/collections/5813742-lab-rax

**The device**

Intel NUC6i7KYK, "Skull Canyon", 211 x 116 x 28 mm.

The NUC's front USB ports and audio jack face the front through an open frame in the faceplate, 179 x 18 mm, with a rounded front edge. Everything else is at the back.

The NUC fills the bay, so the bracket's own side rails hold it straight. It draws its cooling air through its underside, so the tray under it is slotted from front to back.

**What is in the file**

Six plates, already arranged for a Bambu Lab A1 mini (180 x 180 mm bed):

- Plate 1: left side
- Plate 2: right side
- Plate 3: both rear legs
- Plate 4: left half of the tray
- Plate 5: right half of the tray
- Plate 6: faceplate

Every part is already turned the way it prints, and supports and brims are
set per part. Open the file and print all six plates.

Plates 1 to 3 are a chassis that is the same for every device in this series.
Plates 4 to 6 are made for this device.

**Printing**

- Material: PETG. PLA will work in a cool room, but a warm device makes it a
  poor choice.
- Profile: 0.20 mm Standard for the A1 mini, as carried in the file. 2 walls,
  15% infill.
- Filament: about 246 g for all six plates.
- Time: about 11 h 21 min for all six plates.

Each rear leg has a small sprung catch at its foot, printed flat on the bed
with a thin slit above it. When the legs come off the plate, check that slit
is clear and pick out any support left in it, or the catch cannot move.

**Hardware to buy**

- 16 x M6 x 12 button head screws
- 4 x M6 nuts
- 12 x M6 washers (12.5 mm outside diameter)

The rack's posts already hold the nuts for the twelve rack screws. The four
loose nuts are for the faceplate. The washers are needed: the rack screws go
through slots, and a bare screw head will sink into the plastic.

**Assembly**

1. Bolt each rear leg to its rear post from behind, three screws with
   washers. Leave them finger-tight. The grooves face forward.
2. Slide a nut into each of the four slots in the ends of the faceplate.
3. On the bench, stand the two sides facing each other and lay the tray
   across their ledges: the left half first, then the right half onto it.
4. Set the device down onto the tray.
5. Lower the faceplate from above, behind the ears and in front of the
   device, and put four screws through the ears into its nuts. The faceplate
   goes on after the device, not before.
6. Slide the whole frame into the rack from the front. Each side runs into
   the groove of its leg. About 35 mm from home the two catches click.
7. Put six screws with washers through the front ears, then tighten the six
   at the back.

To take it out again, undo the six front screws and draw the frame forward.
It stops after about 35 mm. To remove it completely, reach in from the back
of the rack and push the two tabs at the foot of the legs towards the middle.

**Good to know**

- The sides slide into the legs on a printed dovetail, and how freely that
  runs depends on the printer. Two small test pieces for it are on GitHub
  (`common/stl/coupon_tongue.stl` and `coupon_groove.stl`). Print those first:
  they are small, and they tell you whether the fit suits your printer before
  you print a two-hour side.
- The rack's depth sets itself. The joint between side and leg slides, and
  covers 229 to 257 mm over the outside of the posts.
- The gap between the bracket and the rack's posts is under a millimetre a
  side. Print one side first and offer it up to your rack.
- The outer 7 mm at each end of the NUC's back panel sits behind the
  bracket's rear stops. Keep plugs out of that last 7 mm.
- Before printing the faceplate, check the front ports on your unit against
  the 179 x 18 mm opening. Case dimensions are Intel's published figures.

**Source, other devices and full documentation**

https://github.com/vvyroubal/LabRax-components

The parts are generated by a FreeCAD script, so every dimension can be
changed and the files rebuilt. The repository also has the STL, STEP and
FreeCAD files, brackets for other devices on the same chassis, and what to
change if a fit is tight on your printer. MIT licence.
