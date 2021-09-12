# common - initialization, variables, functions

project != basename $$(pwd)
version != awk <$(project)/__init__.py -F\' '/^__version__/{print $$2}'
python_src != find . -name \*.py
other_src := $(call makefiles) LICENSE README.rst setup.cfg tox.ini
src := $(python_src) $(other_src)

# list make targets with descriptions
help:	
	@set -e;\
	(for file in $(call makefiles); do\
	  echo "$$(head -1 $$file)";\
	  sed <$$file -n -E \
	  '/^#.*/{h;d}; s/^([[:alnum:]_-]+:).*/\1/; /^[[:alnum:]_-]+:/{G;s/:\n/\t/p}'; \
	done) | awk -F'#' \
	  'BEGIN{ first=1; print ".TS"; print "tab(#),box,nowarn;" } \
	  /^#/{ if(first){ first=0; } else { print ".T&"; print "_ _"; } \
	  print "cw(1i) s"; print "_ _"; print "c | l ."; print $$2; next; } \
	  {print} END{print ".TE";}' |\
	tbl | groff  -T utf8 | awk 'NF';

# break with an error if there are uncommited changes
gitclean:
	$(if $(shell git status --porcelain),$(error "git status dirty, commit and push first"))


# require user confirmation   example: $(call verify_action,do something destructive)
define verify_action =
	$(if $(shell \
	  read -p 'Ready to $(1). Confirm? [no] :' OK;\
	  echo $$OK|grep '^[yY][eE]*[sS]*$$'
	),$(info Confirmed),$(error Cowardy refusing))
endef

# generate a list of makefiles
makefiles = Makefile $(wildcard make.include/*.mk)

# return a list of matching include makefile targets
included = $(foreach file,$(makefiles),$(shell sed <$(file) -n 's/^\([[:alnum:]_-]*-$(1)\):.*/\1/p;'))
