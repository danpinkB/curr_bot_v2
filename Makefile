PATH_ROUTES = $(CURDIR)/external_dependencies/smart-order-router

# Targets
.PHONY: clone_sor help
# Default target
clone_sor:
	@git clone $(GIT_REPO) $(PATH_ROUTES)

# Prepare the Docker build context directory
# Clean up the Docker build context
# Run a container based on the built image (example)

# Help target to display available Makefile targets
help:
	@echo "Available targets:"
	@echo "  clone_sor pulling and building smart order router repo"

# Ensure that the 'build' target is the default when 'make' is invoked without arguments.
.DEFAULT_GOAL := build