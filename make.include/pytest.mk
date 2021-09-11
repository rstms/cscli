# pytest - testing

options?=-x
testfiles?=$(wildcard tests/test_*.py)

# pytest   example: make options='-svvvx' test='cli' test 
test:
	set -e;\
	[ -n "$$test" ] && options="$$options -k $$test";\
	pytest $(options) $(testfiles)

# run pytest, breaking into pdb on exceptions or breakpoints
debug:
	${MAKE} options="$(options) -xvvvs --pdb" test

# show available test cases 
testls:
	@echo Test cases:
	@$(foreach test,$(testfiles),grep '^def test_' $(test);)
