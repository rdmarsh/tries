# Makefile for build_tries

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
	@echo "  make install    Install tries into \$${PREFIX:-\$$HOME}/bin"
	@echo "  make uninstall  Remove installed tries binary"
	@echo

gallery:
	./generate-gallery.sh

tests:
	./generate-tests.sh

clean:
	$(RM) -r EXAMPLES

# Installation variables
PREFIX ?= $(HOME)
BINDIR := $(PREFIX)/bin

install:
	mkdir -p "$(BINDIR)"
	install -m 755 build_tries.py "$(BINDIR)/tries"
	@echo "Installed to $(BINDIR)/tries"

uninstall:
	$(RM) "$(BINDIR)/tries"
	@echo "Removed $(BINDIR)/tries"
