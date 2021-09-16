# docs - generate documentation

docs: docs-clean ## generate Sphinx HTML documentation, including API docs
	sphinx-apidoc -o docs/ cscli
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(browser) docs/_build/html/index.html

docs-clean: # clean up documentation files to regenerate
	rm -f docs/cscli.rst
	rm -f docs/modules.rst
	rm -f docs/cscli.commands.rst
	$(MAKE) -C docs clean

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .
