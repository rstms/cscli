# version - automatic version management
 
# - Prevent version changes with uncommited changes
# - tag and commit version changes
# - Configure files to be edited in `setup.cfg`

# bump patch level
bump-patch:
	bumpversion patch

# bump minor version, reset patch to zero
bump-minor:
	bumpversion minor 

# bump version, reset minor and patch to zero
bump-major:
	bumpversion major 

# update timestamp if sources have changed
timestamp: .timestamp

.timestamp: $(src)
	@sed -i  -E repeat/version.py -e "s/(.*__timestamp__.*=).*/\\1 '$(date -Isec)'/"
	@touch $@
	@echo "Timestamp Updated."

version-clean:
	rm -f .timestamp
