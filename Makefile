# FreeCAD ships here as a flatpak; override FREECAD if yours is on PATH.
FREECAD ?= flatpak run --command=freecadcmd --env=UCG_ROOT=$(ROOT) org.freecad.FreeCAD
ROOT    := $(CURDIR)

STL   := export/stl
STEP  := export/step
CAD   := cad/UCG_Fiber_LabRax.FCStd
PARTS := side_l side_r leg_l leg_r tray_l tray_r top_bar bottom_bar
STLS  := $(addprefix $(STL)/,$(addsuffix .stl,$(PARTS)))

.PHONY: all model verify assembly images plate plates clean

all: model verify assembly images plate

model: $(CAD)

# One build produces the document and every export, so they share a rule.
$(CAD) $(STLS): build.py src/model.py src/params.py
	$(FREECAD) build.py

# Check the built solids against the rack interface and the device envelope.
verify: $(CAD)
	$(FREECAD) tools/verify.py

# FreeCAD is headless here, so previews are rendered from the STLs.
images: $(STLS)
	python3 tools/preview.py

# Arranged onto A1 mini plates, ready to open in Bambu Studio.
plate: $(STLS)
	python3 tools/plate.py

# Put a real M6 x 12 and a real nut at all 22 positions and see if they fit.
assembly: $(CAD)
	$(FREECAD) tools/assembly.py

# Slice every plate for real and measure what the printer would actually do.
# Slow (it runs the slicer five times) and needs Bambu Studio, so it is not
# part of `all`.
plates: plate
	python3 tools/checkplates.py

clean:
	rm -rf $(STL) $(STEP) export/3mf images cad/*.FCStd cad/*.FCBak
