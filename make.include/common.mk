# common - initialization, variables, functions

project != basename $$(pwd)
version != cat VERSION
python_src != find setup.py $(project) tests -name \*.py
other_src := LICENSE Makefile README.md VERSION pyproject.toml setup.cfg tox.ini
src := $(python_src) $(other_src)

# list make targets with descriptions
help:	
	@set -e;\
	for file in $(call makefiles); do\
	  echo "##$$(head -1 $$file)";\
	  sed <$$file -n -E '/^#.*/{h;d}; s/^([[:alnum:]_-]+:).*/\1/; /^[[:alnum:]_-]+:/{G;s/\n/\t/p }';\
	done

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
makefiles := Makefile $(wildcard make.include/*.mk)

# return a list of matching include makefile targets
define included =
$(foreach file,$(makefiles),$(shell sed <$(file) -n 's/^\([[:alnum:]_-]*-$(1)\):.*/\1/p;'))
endef
