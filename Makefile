###############################################################################
# Global Project Configuration
###############################################################################
# [IMPLEMENTME] Change project name
PROJECT := ref-project-debdocker
REPO := mentalsmash/$(PROJECT)
# Local repo clone, assumed to be the current directory.
REPO_DIR ?= $(shell pwd)
# Directory where to perform local build operations/
BUILD_DIR ?= build
# Directory where to install build artifacts
DIST_DIR ?= dist
###############################################################################
# Debian Package Configuration
###############################################################################
# Name of the Debian Source Package
DSC_NAME := $(shell dpkg-parsechangelog -S Source)
# Debian package version (<upstream>-<inc>)
DEB_VERSION := $(shell dpkg-parsechangelog -S Version)
# Debian package upstream version (<upstream>)
UPSTREAM_VERSION := $(shell echo $(DEB_VERSION) | rev | cut -d- -f2- | rev)
# Original upstream archive (generated from git repo)
UPSTREAM_TARBALL := $(DSC_NAME)_$(UPSTREAM_VERSION).orig.tar.xz
# Docker image for the Debian Builder container
DEB_BUILDER ?= $(REPO)-debian-builder:latest
# Docker image for the Debian Tester container
DEB_TESTER ?= $(REPO)-debian-tester:latest
###############################################################################
# Testing Configuration
###############################################################################
# Directory where to generate test logs
# When running inside a container it must be a subdirectory of REPO_DIR
LOCAL_TESTER_RESULTS ?= $(REPO_DIR)/test-results
# A unique ID for the test run. This variable is automatically set by CI workflows
TEST_ID ?= local
# The date when the tests were run. This variable is automatically set by CI workflows
TEST_DATE ?= $(shell date +%Y%m%d-%H%M%S)

.PHONY: \
  build \
  changelog \
	clean \
  code-check \
  tarball \
  test-ci \
  test-release

# Build project
build:
	@echo "Building $(REPO)..."
	# [IMPLEMENTME] Replace with actual build steps
	mkdir -p $(BUILD_DIR)
	echo $$(date) > $(BUILD_DIR)/build_id

# Update changelog entry and append build codename to version
# Requires the Debian Builder image.
changelog:
	# Try to make sure changelog is at a clean version
	git checkout debian/changelog || true
	docker run --rm \
		-v $(REPO_DIR)/:/repo \
		-w /repo \
		$(DEB_BUILDER)  \
		/repo/scripts/debian/update_changelog.sh $(DEB_VERSION)

# Clean up build 
clean:
	@echo "Cleaning build for $(REPO)..."
	# [IMPLEMENTME] Perform additional clean up operations.
	rm -rf $(BUILD_DIR)

# Perform code validations (e.g. run linter, check format, etc...)
code-check:
	@echo "Validating $(REPO)'s code changes..."
	# [IMPLEMENTME] Trigger code validation.

# Validate generated Debian package
debtest:
	@echo "Running test for Debian build of $(REPO) with image $(TEST_IMAGE)..."
	mkdir -p ${LOCAL_TESTER_RESULTS}
	echo "Test run id ${TEST_DATE}" > ${LOCAL_TESTER_RESULTS}/${TEST_ID}.log
	# [IMPLEMENTME] Trigger tests to validate Debian build

# Build uno's debian packages.
# Requires the Debian Builder image.
debuild:
	docker run --rm \
		-v $(REPO_DIR)/:/repo \
		-w /repo \
		$(DEB_BUILDER)  \
		/repo/scripts/debian/build.sh $(PROJECT) /repo

# Build images required for development and CI administration.
dockerimages: \
  dockerimage-debian-builder \
	dockerimage-admin;

# Convenience target to build an image with `docker compose build`
dockerimage-%:
	docker compose build $*

# Copy build file to an install location
install:
	mkdir -p $(DIST_DIR)
	install $(BUILD_DIR)/build_id $(DIST_DIR)/

# Run tests for CI (a.k.a. PR) build.
test-ci:
	@echo "Running test for CI build of $(REPO)..."
	mkdir -p ${LOCAL_TESTER_RESULTS}
	echo "Test run id ${TEST_DATE}" > ${LOCAL_TESTER_RESULTS}/${TEST_ID}.log
	# [IMPLEMENTME] Trigger tests to validate CI build

# Run tests for a Release build
test-release:
	@echo "Running test for Release build of $(REPO)..."
	mkdir -p ${LOCAL_TESTER_RESULTS}
	echo "Test run id ${TEST_DATE}" > ${LOCAL_TESTER_RESULTS}/${TEST_ID}.log
	# [IMPLEMENTME] Trigger tests to validate release build

# Generate upstream archive for Debian packaging
tarball: ../$(UPSTREAM_TARBALL) ;

# Generate upstream archive from git HEAD
../$(UPSTREAM_TARBALL):
	git ls-files --recurse-submodules | tar -cvaf $@ -T-
