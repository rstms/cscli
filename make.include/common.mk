# common - initialization, variables, functions

project != basename $$(pwd)
version != awk <$(project)/__init__.py -F"[\"']" '/^__version__/{print $$2}'
python_src != find . -name \*.py
other_src := $(MAKEFILE_LIST) LICENSE README.rst setup.cfg tox.ini
src := $(python_src) $(other_src)

help: ## makefile help 
	@(for file in $(MAKEFILE_LIST); do \
	  awk <$$file -F: 'BEGIN{first=1;}\
	    /^#/{if(first){first=0;title=$$0;}}\
	    /^[a-zA-Z0-9_-]+:.*##/{if(length(title)){print title; title=""};\
	      printf("%s\t%s\n", $$1, gensub(/.*##(.*)$$/,"\\1",1));}';\
	done) | awk -F'#' \
	  'BEGIN{ first=1; print ".TS"; print "box,nowarn;" } \
	  /^#/{ if(first){first=0;} else { print ".T&"; print "_ _"; } \
	  print "cz sz"; print "_ _"; print "l | l ."; print $$2; next; } \
	  {print} END{print ".TE";}' |\
	tbl | groff  -T utf8 | awk 'NF';
	  

gitclean: ## break with an error if there are uncommited changes
	$(if $(shell git status --porcelain),$(error "git status dirty, commit and push first"))


# require user confirmation   example: $(call verify_action,do something destructive)
define verify_action =
	$(if $(shell \
	  read -p 'Ready to $(1). Confirm? [no] :' OK;\
	  echo $$OK|grep '^[yY][eE]*[sS]*$$'
	),$(info Confirmed),$(error Cowardy refusing))
endef

# return a list of matching include makefile targets
included = $(foreach file,$(MAKEFILE_LIST),$(shell sed <$(file) -n 's/^\([[:alnum:]_-]*-$(1)\):.*/\1/p;'))

common-clean: # clean up python cruft
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
