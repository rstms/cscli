# test - testing with pytest and tox

ifdef CLOUDSIGMA_PASSWORD
$(info cloudsigma password present; recording tests)
vcr := --vcr-record=all
else
$(info cloudsigma password not found; testing with recorded API sessions)
vcr := --vcr-record=none
endif

options ?= -x $(vcr)
testfiles ?= $(wildcard tests/test_*.py)
options := $(if $(test),$(options) -k $(test),$(options))



test: ## run pytest;  example: make options=-svvvx test=cli test 
	pytest $(options) $(testfiles)

debug: ## run pytest, dropping into pdb on exceptions or breakpoints
	${MAKE} options="$(options) -xvvvs --pdb" test

coverage: ## check code coverage quickly with the default Python
	coverage run --source cscli -m pytest
	coverage report -m
	coverage html
	@$(browser) htmlcov/index.html

testls: ## show available test cases 
	@echo $$($(foreach test,$(testfiles),grep '^def test_' $(test);)) |\
	  tr ' ' '\n' | grep -v def | awk -F\( 'BEGIN{xi=0} {printf("%s",$$1);\
	  if(++xi==3){xi=0; printf("\n");} else {printf("\t");}}' |\
	  awk 'BEGIN{print ".TS\nbox,nowarn;\nl | l | l ." } {print} END{print ".TE";}' |\
	  tbl | groff  -T utf8 | awk 'NF';

.PHONY: tox
tox: .tox ## test with tox if sources have changed
.tox: $(src)
	@echo Changed files: $?
	tox
	@touch $@

test-clean: # remove test and coverage artifacts
	rm -f pytest.log
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache
	rm -rf tests/cassettes/*
