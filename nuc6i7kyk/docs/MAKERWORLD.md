# MakerWorld listing: NUC6i7KYK_LabRax-A1mini.3mf

Text to post with `../NUC6i7KYK_LabRax-A1mini.3mf`. Paste each part into the matching field.

## Title

Lab Rax 1U bracket for Intel NUC6i7KYK (Skull Canyon), A1 mini

## Summary

A 1U bracket that carries an Intel NUC6i7KYK (Skull Canyon) in a Lab Rax 10 inch rack, bolted to the front and rear posts. The NUC stands on the bracket's own seats, face forward, with nothing under it to block its air. Three plates, all on an A1 mini.

## Tags

Lab Rax, 10 inch rack, 1U, Intel NUC, NUC6i7KYK, Skull Canyon, rack mount, homelab, A1 mini

## Pictures

Rendered from the STLs, in `../images/`: `assembly-nuc-iso.png`,
`assembly-nuc-front.png` and `assembly-nuc-top.png`. The 3:4 MakerWorld
pictures (`makerworld-nuc-*.png`) still show the earlier bracket with a tray
and faceplate and need rendering again.

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

Intel NUC6i7KYK, "Skull Canyon", 233 x 143 x 40 mm measured whole (Intel quote 211 x 116 x 28 for the case alone).

That is wider than the space between the bracket's side rails and too tall for a tray in one rack unit, so the NUC goes in bare: it stands on a 19.2 mm wide, 3.5 mm thick seat on each side, between the rack's posts, with about half a millimetre to spare at each end. Its face is half a millimetre behind the front ears, which overlap its ends and stop it coming forward; the runners at the back stop it going back. Its whole front face shows between the ears. It draws its cooling air through its underside, and there is nothing under it but the rack unit below.

**What is in the file**

Three plates, already arranged for a Bambu Lab A1 mini (180 x 180 mm bed):

- Plate 1: left side, the NUC's own: a seat where the NUC stands, joined into the ear at the front and into a yoke round the leg at the back
- Plate 2: right side, the same
- Plate 3: both rear legs

The rear legs are the same as for every other device in this series, so if you already have a pair, plates 1 and 2 are all you need.

**Printing**

- Material: PETG. PLA will work in a cool room, but a warm device makes it a
  poor choice.
- Profile: 0.20 mm Standard for the A1 mini, as carried in the file. 2 walls,
  15% infill.
- Filament: about 109 g for all three plates.
- Time: about 5 h 28 min for all three plates.

Each rear leg has a small sprung catch at its foot, printed flat on the bed
with a thin slit above it. When the legs come off the plate, check that slit
is clear and pick out any support left in it, or the catch cannot move.

**Hardware to buy**

- 12 x M6 x 12 button head screws
- 12 x M6 washers (12.5 mm outside diameter)

The rack's posts already hold the nuts. The washers are needed: the rack
screws go through slots, and a bare screw head will sink into the plastic.

**Assembly**

1. Bolt each rear leg to its rear post from behind, three screws with
   washers. Leave them finger-tight. The grooves face forward.
2. On the bench, stand the two sides facing each other and set the NUC on
   their seats, its front face against the backs of the ears.
3. Slide the sides and the NUC into the rack from the front together. Each
   side runs into the groove of its leg. About 35 mm from home the two
   catches click. The ears overlap the NUC's ends, so it cannot go in after
   the sides.
4. Put six screws with washers through the front ears, then tighten the six
   at the back.

To take it out again, undo the six front screws and draw it forward. It
stops after about 35 mm. To remove it completely, reach in from the back of
the rack and push the two tabs at the foot of the legs towards the middle.

**Good to know**

- The sides slide into the legs on a printed dovetail, and how freely that
  runs depends on the printer. Two small test pieces for it are on GitHub
  (`common/stl/coupon_tongue.stl` and `coupon_groove.stl`).
- The rack's depth sets itself. The joint between side and leg slides, and
  covers 229 to 257 mm over the outside of the posts.
- Measure your NUC and your rack before printing: the case has to pass
  between the posts, and it is 233 mm wide.
- The front rack screws go into the posts right beside the NUC's front
  corners. Check that their tips do not stand out of the posts' inner faces
  before you tighten them.

**Source, other devices and full documentation**

https://github.com/vvyroubal/LabRax-components

The parts are generated by a FreeCAD script, so every dimension can be
changed and the files rebuilt. The repository also has the STL, STEP and
FreeCAD files, brackets for other devices on the same chassis, and what to
change if a fit is tight on your printer. MIT licence.
