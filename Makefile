# Liberty Lamp lantern frame — STL build
OPENSCAD ?= openscad
BED      ?= 250
SRC      := src/lantern.scad
PARTS    := body roof
VIEWS    := $(PARTS) assembly
STLS     := $(PARTS:%=build/stl/%.stl)
PNGS     := $(VIEWS:%=build/png/%.png)

.PHONY: all stl check png test clean pcb pcb-test stencils stencils-test
.DELETE_ON_ERROR:
all: check png

stl: $(STLS)

build/stl/%.stl: $(SRC)
	@mkdir -p $(@D)
	$(OPENSCAD) -q -o $@ -D 'part="$*"' --export-format binstl $<

build/png/%.png: $(SRC)
	@mkdir -p $(@D)
	$(OPENSCAD) -q -o $@ -D 'part="$*"' --render --imgsize=800,800 --autocenter --viewall --colorscheme=Tomorrow $<

check: stl
	node scripts/check-stl.mjs --bed $(BED) $(STLS)

png: $(PNGS)

test:
	node --test scripts/*.test.mjs

# ---- Candle PCB (KiCad) ----
KICAD_CLI ?= $(shell command -v kicad-cli || echo /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli)
BOARDS    := candle-driver led-disc

pcb-test:
	cd pcb/gen && KICAD_CLI=$(KICAD_CLI) python3 -m unittest -v test_kisch test_boards

pcb: pcb-test
	@mkdir -p build
	python3 pcb/gen/boards.py
	@for b in $(BOARDS); do \
	  $(KICAD_CLI) sch erc --severity-error --exit-code-violations -o build/$$b-erc.rpt pcb/$$b/$$b.kicad_sch || { cat build/$$b-erc.rpt; exit 1; }; \
	  $(KICAD_CLI) sch export pdf -o pcb/$$b/$$b-schematic.pdf pcb/$$b/$$b.kicad_sch; \
	done

# ---- Bird stencils ----
PY := stencils/.venv/bin/python

stencils/.venv:
	python3 -m venv stencils/.venv && $(PY) -m pip install -q opencv-python-headless numpy

stencils-test: stencils/.venv
	cd stencils/gen && ../.venv/bin/python -m unittest -v test_check

stencils: stencils-test
	$(PY) -I stencils/gen/fetch.py
	$(PY) -I stencils/gen/stencil.py

clean:
	rm -rf build
