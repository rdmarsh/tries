# Makefile for build_tries

.PHONY: all help gallery tests clean

all: gallery tests

help:
	@echo "Available targets:"
	@echo
	@echo "  make            Run gallery + tests (default)"
	@echo "  make gallery    Generate theme PDFs into EXAMPLES/"
	@echo "  make tests      Generate feature tests into EXAMPLES/tests/"
	@echo "  make clean      Remove all generated output"
	@echo

gallery:
	./generate-gallery.sh

tests:
	./generate-tests.sh

clean:
	$(RM) -r EXAMPLES
