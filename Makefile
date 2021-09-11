# top-level Makefile 

# testing target
d2:
	@echo '$(call included,clean)'

# remove module from the local python environment
uninstall:
	pip uninstall -y $(project)

# install to the local environment from the source directory
install:
	pip install --use-feature=in-tree-build --upgrade .

# local install in editable mode for development
devinstall: uninstall build
	#$(shell [ -e pyproject.toml ] && mv pyproject.toml .pyproject.toml)
	pip install --use-feature=in-tree-build --upgrade -e .[dev]
	#$(shell [ -e .pyproject.toml ] && mv .pyproject.toml pyproject.toml)

# delete temporary development files
clean: $(call included,clean) 
	rm -rf .pytest_cache
	rm -rf ./build
	find . -type d -name __pycache__ | xargs -r rm -rf
	find . -type d -name \*.egg-info | xargs -r rm -rf
	find . -type f -name \*.pyc | xargs -r rm

include $(wildcard make.include/*.mk)
