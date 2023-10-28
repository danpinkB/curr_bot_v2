DOCKERFILE := $(CURDIR)/Dockerfile
DOCKER_BUILD_ARGS := --build-arg PATH_TO_IGNORE_FILE=$(CURDIR)/.dockerignore
#--no-cache

$(eval GIT_REPO=$(shell grep GIT_REPO .env | cut -d '=' -f2))

DIRS := $(shell cat build_directories.config)

PATH_ROUTES = $(CURDIR)/other_builds/smart_router

# Targets
.PHONY: build build_sor run stop
DC=docker-compose
# Default target
build:
	@docker compose build

build_sor:
	@git clone $(GIT_REPO) $(PATH_ROUTES)
	@docker build $(PATH_ROUTES) -t smart-order-router
run:
	@docker compose up

stop:
	@docker compose down

# Prepare the Docker build context directory
# Clean up the Docker build context
# Run a container based on the built image (example)

# Help target to display available Makefile targets
help:
	@echo "Available targets:"
	@echo "  build        docker env"
	@echo "  build_sor pulling and building smart order router repo"
	@echo "  run          Run app."
	@echo "  stop         Stop app"
	@echo "  run          Run app."
	@echo "  stop         Stop app"
	@echo "  help         Display this help message."

# Ensure that the 'build' target is the default when 'make' is invoked without arguments.
.DEFAULT_GOAL := build