# TODO update base image to match project
ARG BASE_IMAGE="mentalsmash/gh-actions:latest"
FROM ${BASE_IMAGE}

# TODO update labels to match project
LABEL org.opencontainers.image.source=https://example.com/johndoe/example-repository.git
LABEL org.opencontainers.image.licenses=Apache-2.0
LABEL org.opencontainers.image.vendor="John Doe"

# Name of non-root user created for testing
ARG TEST_USER="tester"

# Enable DEV mode
ARG DEV=

RUN set -xe; \
    export DEBIAN_FRONTEND="noninteractive"; \
    apt-get update; \
    # TODO Install packages required by tests, e.g.:
    apt-get install -y --no-install-recommends \
      sudo \
      openssh-server \
      openssh-client \
      curl; \
    # TODO Install extras packages to help with local development, e.g.:
    if [ -n "${DEV}" ]; then \
      apt-get install -y --no-install-recommends \
        build-essential \
        vim; \
    fi; \
    apt-get clean; \
    # create a non-root user and give it passwordless sudo
    adduser ${TEST_USER} --shell /bin/bash; \
    echo ${TEST_USER} ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/${TEST_USER}; \
    chmod 0440 /etc/sudoers.d/${TEST_USER}; \
    adduser ${TEST_USER} sudo; \
    # reinstall uno in "editable" mode
    if [ -n "${DEV}" ]; then \
      pip3 install -e ${UNO_DIR}; \
    fi; \
    # Initialize ~/.ssh
    mkdir -p /home/${TEST_USER}/.ssh; \
    touch /home/${TEST_USER}/.ssh/authorized_keys; \
    # Generate a private key and configure it as an authorized key
    ssh-keygen -t ed25519 -N '' -C uno@test -f /home/${TEST_USER}/.ssh/id_ed25519; \
    cat /home/${TEST_USER}/.ssh/id_ed25519.pub >> /home/${TEST_USER}/.ssh/authorized_keys; \
    # Adjust permissions
    chown -R ${TEST_USER}:${TEST_USER} /home/${TEST_USER}/.ssh

