# FreeCAD ships here as a flatpak; override FREECAD if yours is on PATH.
FREECAD ?= flatpak run --command=freecadcmd --env=UCG_ROOT=$(ROOT) org.freecad.FreeCAD
ROOT    := $(CURDIR)

# The chassis and the code are in common/; each device has a folder of its own
# holding its profile (device.py), its STLs, its 3MF and its renders.
TOOLS := common/tools
SRC   := common/src
CAD   := common/cad/UCG_Fiber_LabRax.FCStd
DEVICES := ucg usw sg108e nuc
DEVICE_DIRS := ucg-fiber usw-flex-mini tl-sg108e nuc6i7kyk

# A device's three prints, from its folder and its key.
kit = $(1)/stl/tray_$(2)_l.stl $(1)/stl/tray_$(2)_r.stl $(1)/stl/faceplate_$(2).stl
STLS  := $(addprefix common/stl/,$(addsuffix .stl,side_l side_r leg_l leg_r)) \
         $(call kit,ucg-fiber,ucg) \
         $(call kit,usw-flex-mini,usw) \
         $(call kit,tl-sg108e,sg108e) \
         $(call kit,nuc6i7kyk,nuc)
# Each device's own document and STEP: the chassis plus its three parts.
DEVICE_CAD := $(foreach s,ucg-fiber/UCG_Fiber_LabRax usw-flex-mini/USW_Flex_LabRax \
                tl-sg108e/TL_SG108E_LabRax nuc6i7kyk/NUC6i7KYK_LabRax,$(s).FCStd $(s).step)

.PHONY: all model verify assembly images plate plates clean

all: model verify assembly images plate

model: $(CAD)

# One build produces the document and every export, so they share a rule.
$(CAD) $(STLS) $(DEVICE_CAD): build.py $(wildcard $(SRC)/*.py) $(addsuffix /device.py,$(DEVICE_DIRS))
	$(FREECAD) build.py

# Check the built solids against the rack interface and each device envelope.
# One process per device: the chassis is shared, so it has to be shown to work
# with each of them, and one document holding every part of every device is
# more solid than the boolean kernel will carry.
verify: $(CAD)
	@for d in $(DEVICES); do \
	  UCG_DEVICE=$$d $(FREECAD) $(TOOLS)/verify.py || exit 1; \
	done

# FreeCAD is headless here, so previews are rendered from the STLs.
images: $(STLS)
	python3 $(TOOLS)/preview.py

# Arranged onto A1 mini plates, ready to open in Bambu Studio.
plate: $(STLS)
	python3 $(TOOLS)/plate.py

# Put a real M6 x 12 and a real nut at all 20 positions and see if they fit.
assembly: $(CAD)
	@for d in $(DEVICES); do \
	  UCG_DEVICE=$$d $(FREECAD) $(TOOLS)/assembly.py || exit 1; \
	done

# Slice every plate for real and measure what the printer would actually do.
# Slow (it runs the slicer five times) and needs Bambu Studio, so it is not
# part of `all`.
plates: plate
	python3 $(TOOLS)/checkplates.py

clean:
	rm -rf common/stl common/step common/cad/*.FCStd common/cad/*.FCBak
	rm -rf $(addsuffix /stl,$(DEVICE_DIRS)) $(addsuffix /images,$(DEVICE_DIRS))
	rm -f $(addsuffix /*.3mf,$(DEVICE_DIRS)) $(DEVICE_CAD)
	rm -f $(addsuffix /*.FCBak,$(DEVICE_DIRS))
