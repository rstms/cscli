# lint / source format
fmt:  ## blacken python source
	black $(project) tests

lint: fmt  ## check style with flake8
	isort $(project) tests
	flake8 $(project) tests

# vim:ft=make
