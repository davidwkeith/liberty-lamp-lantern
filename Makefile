# Liberty Lamp lantern frame — STL build
OPENSCAD ?= openscad
BED      ?= 250
SRC      := src/lantern.scad
PARTS    := body roof
VIEWS    := $(PARTS) assembly
STLS     := $(PARTS:%=build/stl/%.stl)
PNGS     := $(VIEWS:%=build/png/%.png)

.PHONY: all stl check png test clean
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

clean:
	rm -rf build
