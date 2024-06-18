PYTHON ?= python3
DOCSDIR = docs
DATADIR = data
DOC_SOURCES = $(DOCSDIR)/galleryviewer.1.in $(DOCSDIR)/galleryviewer.conf.5.in
PKG_VERSION_SOURCE = src/galleryviewer/__init__.py
render = $(PYTHON) scripts/render.py $(PKG_VERSION_SOURCE) $(DOC_SOURCES)
grohtml = groff -man -Thtml -P-l

docs: man

man: $(DATADIR)/galleryviewer.1.gz $(DATADIR)/galleryviewer.conf.5.gz

html: $(DATADIR)/galleryviewer.1.html $(DATADIR)/galleryviewer.conf.5.html

%.gz: %
	gzip -9 -c $< > $@

$(DATADIR)/galleryviewer.1.html: $(DATADIR)/galleryviewer.1
	SOURCE_DATE_EPOCH=$$(stat -c %Y $(DOCSDIR)/galleryviewer.1.in) \
		$(grohtml) $< > $@

$(DATADIR)/galleryviewer.conf.5.html: $(DATADIR)/galleryviewer.conf.5
	SOURCE_DATE_EPOCH=$$(stat -c %Y $(DOCSDIR)/galleryviewer.conf.5.in) \
		$(grohtml) $< > $@

$(DATADIR)/galleryviewer.1: $(DOC_SOURCES) $(PKG_VERSION_SOURCE) | $(DATADIR)
	$(render) < $(DOCSDIR)/galleryviewer.1.in > $@

$(DATADIR)/galleryviewer.conf.5: $(DOC_SOURCES) $(PKG_VERSION_SOURCE) | $(DATADIR)
	$(render) < $(DOCSDIR)/galleryviewer.conf.5.in > $@

$(DATADIR):
	mkdir -p $(DATADIR)

clean:
	rm -rf $(DATADIR)

test:
	sh test/test_cli.sh
	$(PYTHON) test/test_doctest.py

.PHONY: clean test docs man html
