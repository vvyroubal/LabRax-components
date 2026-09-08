# FreeCAD ships here as a flatpak; override FREECAD if yours is on PATH.
FREECAD ?= flatpak run --command=freecadcmd --env=UCG_ROOT=$(ROOT) org.freecad.FreeCAD
ROOT    := $(CURDIR)

STL   := export/stl
STEP  := export/step
CAD   := cad/UCG_Fiber_LabRax.FCStd
PARTS := tray top_bar ear_l ear_r stop_l stop_r
STLS  := $(addprefix $(STL)/,$(addsuffix .stl,$(PARTS)))

.PHONY: all model verify images clean

all: model verify images

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

clean:
	rm -rf $(STL) $(STEP) images cad/*.FCStd cad/*.FCBak
