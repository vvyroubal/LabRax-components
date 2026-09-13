# FreeCAD ships here as a flatpak; override FREECAD if yours is on PATH.
FREECAD ?= flatpak run --command=freecadcmd --env=UCG_ROOT=$(ROOT) org.freecad.FreeCAD
ROOT    := $(CURDIR)

STL   := export/stl
STEP  := export/step
CAD   := cad/UCG_Fiber_LabRax.FCStd
DEVICES := ucg usw
PARTS := side_l side_r leg_l leg_r \
         tray_ucg_l tray_ucg_r faceplate_ucg \
         tray_usw_l tray_usw_r faceplate_usw
STLS  := $(addprefix $(STL)/,$(addsuffix .stl,$(PARTS)))

.PHONY: all model verify assembly images plate plates clean

all: model verify assembly images plate

model: $(CAD)

# One build produces the document and every export, so they share a rule.
$(CAD) $(STLS): build.py src/model.py src/params.py
	$(FREECAD) build.py

# Check the built solids against the rack interface and each device envelope.
# One process per device: the chassis is shared, so it has to be shown to work
# with each of them, and one document holding every part of every device is
# more solid than the boolean kernel will carry.
verify: $(CAD)
	@for d in $(DEVICES); do \
	  UCG_DEVICE=$$d $(FREECAD) tools/verify.py || exit 1; \
	done

# FreeCAD is headless here, so previews are rendered from the STLs.
images: $(STLS)
	python3 tools/preview.py

# Arranged onto A1 mini plates, ready to open in Bambu Studio.
plate: $(STLS)
	python3 tools/plate.py

# Put a real M6 x 12 and a real nut at all 22 positions and see if they fit.
assembly: $(CAD)
	@for d in $(DEVICES); do \
	  UCG_DEVICE=$$d $(FREECAD) tools/assembly.py || exit 1; \
	done

# Slice every plate for real and measure what the printer would actually do.
# Slow (it runs the slicer five times) and needs Bambu Studio, so it is not
# part of `all`.
plates: plate
	python3 tools/checkplates.py

clean:
	rm -rf $(STL) $(STEP) export/3mf images cad/*.FCStd cad/*.FCBak
