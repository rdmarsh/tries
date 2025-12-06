# Makefile for tries.py

.PHONY: all help gallery tests clean install uninstall

# Default target
all: gallery tests

help:
	@echo "Available targets:"
	@echo
	@echo "  make            Run gallery + tests (default)"
	@echo "  make gallery    Generate theme PDFs into EXAMPLES/"
	@echo "  make tests      Generate feature tests into EXAMPLES/tests/"
	@echo "  make clean      Remove all generated output"
	@echo "  make install    Install tries into $${PREFIX:-$$HOME}/bin"
	@echo "  make uninstall  Remove installed tries binary"
	@echo
	@echo "Environment variables:"
	@echo "  PREFIX=DIR      Override install prefix (default: $$HOME)"

gallery: EXAMPLES
	./generate-gallery.sh

tests: EXAMPLES/tests
	./generate-tests.sh

EXAMPLES:
	mkdir -p EXAMPLES

EXAMPLES/tests:
	mkdir -p EXAMPLES/tests

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
	install -m 644 samples.py "$(SHAREDIR)/samples.py"

	@echo "Installed tries to $(BINDIR)/tries"
	@echo "Installed support files to $(SHAREDIR)"

uninstall:
	$(RM) "$(BINDIR)/tries"
	$(RM) "$(SHAREDIR)/themes.py"
	$(RM) "$(SHAREDIR)/samples.py"
	@echo "Removed tries and support files"
