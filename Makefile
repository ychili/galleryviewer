PYTHON ?= python3
DOCSDIR = docs
DATADIR = data
DOC_SOURCES = $(DOCSDIR)/galleryviewer.1.in
PKG_VERSION_SOURCE = src/galleryviewer/__init__.py
render = $(PYTHON) scripts/render.py $(PKG_VERSION_SOURCE)
grohtml = groff -man -Thtml -P-l
git_available = $(shell git rev-parse --is-inside-work-tree 2>/dev/null)
ifeq ($(git_available),true)
  get_epoch = git log -1 --pretty=format:%ct --
else
  get_epoch = stat -c %Y --
endif

docs: man

man: $(DATADIR)/galleryviewer.1.gz

html: $(DATADIR)/galleryviewer.1.html

%.gz: %
	gzip -9 -c $< > $@

$(DATADIR)/galleryviewer.1.html: $(DATADIR)/galleryviewer.1
	SOURCE_DATE_EPOCH=$$($(get_epoch) $(DOCSDIR)/galleryviewer.1.in) \
		$(grohtml) $< > $@

$(DATADIR)/galleryviewer.1: $(DOC_SOURCES) $(PKG_VERSION_SOURCE) | $(DATADIR)
	$(render) $$($(get_epoch) $(DOC_SOURCES)) \
		< $(DOCSDIR)/galleryviewer.1.in > $@

$(DATADIR):
	mkdir -p $(DATADIR)

clean:
	rm -rf $(DATADIR)

test:
	sh test/test_cli.sh
	$(PYTHON) test/test_doctest.py

.PHONY: clean test docs man html
