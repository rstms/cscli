# version - automatic version management
 
# - Prevent version changes with uncommited changes
# - tag and commit version changes
# - Configure files to be edited in `setup.cfg`

bump-patch: ## bump patch level
	bumpversion patch

bump-minor: ## bump minor version, reset patch to zero
	bumpversion minor 

bump-major: ## bump version, reset minor and patch to zero
	bumpversion major 

timestamp: .timestamp ## update timestamp if sources have changed
.timestamp: $(src)
	@sed -i  -E repeat/version.py -e "s/(.*__timestamp__.*=).*/\\1 '$(date -Isec)'/"
	@touch $@
	@echo "Timestamp Updated."

version-clean: # clean up version tempfiles
	rm -f .timestamp
