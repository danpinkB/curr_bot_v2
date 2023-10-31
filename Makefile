# Targets
.PHONY: help
# Default target
# Prepare the Docker build context directory
# Clean up the Docker build context
# Run a container based on the built image (example)

# Help target to display available Makefile targets
help:
	@echo "be nice:)"

# Ensure that the 'build' target is the default when 'make' is invoked without arguments.
.DEFAULT_GOAL := build