SHELL := /bin/bash
NOTES := notes
RESULTS := results
MD := $(RESULTS)/math-in-it.md
PDF := $(RESULTS)/math-in-it.pdf
PREAMBLE := scripts/preamble.tex
HEADING_FILTER := scripts/heading-ids.py
CALLOUT_FILTER := scripts/callouts.lua
CAT := scripts/cat.py
PDF_ENGINE := xelatex

.PHONY: md pdf all clean

md:
	@mkdir -p $(RESULTS)
	python3 $(CAT) -o $(MD)

pdf: md
	@mkdir -p $(RESULTS)
	TMP=$$(mktemp -d) && \
	cp -R images $$TMP/ && \
	pandoc $(MD) -o $$TMP/math-in-it.tex \
		--resource-path=$(CURDIR) \
		--include-in-header=$(PREAMBLE) \
		--filter=$(HEADING_FILTER) \
		--lua-filter=$(CALLOUT_FILTER) 2>/dev/null && \
	cd $$TMP && \
	$(PDF_ENGINE) -interaction=nonstopmode math-in-it.tex > /dev/null 2>&1 && \
	$(PDF_ENGINE) -interaction=nonstopmode math-in-it.tex > /dev/null 2>&1 && \
	cp math-in-it.pdf $(CURDIR)/$(PDF) && \
	rm -rf $$TMP && \
	rm -f $(CURDIR)/*.log $(CURDIR)/*.aux $(CURDIR)/*.out

all: md pdf

clean:
	rm -f $(MD) $(PDF)
	rm -f scripts/*.log scripts/*.bak*
