# Makefile for tries.py

.PHONY: all help gallery examples test clean install uninstall

# Default target
all: gallery examples

help:
	@echo "Available targets:"
	@echo
	@echo "  make            Run gallery + examples (default)"
	@echo "  make gallery    Generate theme PDFs into EXAMPLES/"
	@echo "  make examples   Render feature examples into EXAMPLES/tests/"
	@echo "  make test       Run the behaviour test suite (no Graphviz needed)"
	@echo "  make clean      Remove all generated output"
	@echo "  make install    Install tries into $${PREFIX:-$$HOME}/bin"
	@echo "  make uninstall  Remove installed tries binary"
	@echo
	@echo "Environment variables:"
	@echo "  PREFIX=DIR      Override install prefix (default: $$HOME)"

gallery: EXAMPLES
	./generate-gallery.sh

examples: EXAMPLES/tests
	./generate-examples.sh

EXAMPLES:
	mkdir -p EXAMPLES

EXAMPLES/tests:
	mkdir -p EXAMPLES/tests

test:
	python3 test_tries.py -v

clean:
	$(RM) -r EXAMPLES

# Installation variables
PREFIX ?= $(HOME)
BINDIR := $(PREFIX)/bin

ifeq ($(PREFIX),$(HOME))
    SHAREDIR := $(HOME)/.local/share/tries
else
    SHAREDIR := $(PREFIX)/share/tries
endif

install:
	mkdir -p "$(BINDIR)"
	mkdir -p "$(SHAREDIR)"

	# Install main executable
	install -m 755 tries.py "$(BINDIR)/tries"

	# Support files
	install -m 644 themes.py  "$(SHAREDIR)/themes.py"

	@echo "Installed tries to $(BINDIR)/tries"
	@echo "Installed support files to $(SHAREDIR)"

uninstall:
	$(RM) "$(BINDIR)/tries"
	$(RM) "$(SHAREDIR)/themes.py"
	@echo "Removed tries and support files"
