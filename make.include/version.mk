# version - automatic version management
 
# - Prevent version changes with uncommited changes
# - tag and commit version changes
# - Configure files to be edited in `setup.cfg`
# - Use 'lightweight tags'

bump-patch: ## bump patch level
	bumpversion patch --tag-message ''

bump-minor: ## bump minor version, reset patch to zero
	bumpversion minor --tag-message ''

bump-major: ## bump version, reset minor and patch to zero
	bumpversion major --tag-message ''

timestamp: .timestamp ## update timestamp if sources have changed
.timestamp: $(src)
	sed -E -i $(project)/__init__.py -e "s/(.*__timestamp__.*=).*/\1 \"$$(date -Isec)\"/"
	@touch $@
	@echo "Timestamp Updated."

version-clean: # clean up version tempfiles
	rm -f .timestamp
