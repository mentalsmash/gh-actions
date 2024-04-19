# TODO update default base image
ARG BASE_IMAGE="ubuntu:22.04"
FROM ${BASE_IMAGE}

# TODO update labels to match project
LABEL org.opencontainers.image.source=https://example.com/johndoe/example-repository.git
LABEL org.opencontainers.image.licenses=Apache-2.0
LABEL org.opencontainers.image.vendor="John Doe"

ARG TEST=
ARG DEV=

RUN set -xe; \
    export DEBIAN_FRONTEND=noninteractive; \
    apt-get update; \
    apt-get upgrade -y --no-install-recommends; \
    # - Make sure locale is en_US.UTF-8
    if [ "$(. /etc/os-release && echo $ID)" = ubuntu ]; then \
      apt-get install -y --no-install-recommends \
        locales;  \
      locale-gen en_US en_US.UTF-8; \
      update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8; \
    else \
      apt-get install -y --no-install-recommends \
        locales \
        locales-all; \
      update-locale LC_ALL=en_US.utf8 LANG=en_US.utf8; \
    fi; \
    # Install optional dependencies:
    if [ -n "${TEST}${DEV}" ]; then \
      apt-get install -y --no-install-recommends \
        sudo \
        openssh-server \
        openssh-client \
        curl; \
    fi; \
    if [ -n "${DEV}" ]; then \
      apt-get install -y --no-install-recommends \
        build-essential \
        vim; \
    fi; \
    # TODO Install project dependencies
    # apt-get install -y --no-install-recommends ... ; \
    apt-get clean

ENV LANG en_US.UTF-8

###############################################################################
# Create a non-root user and give it passwordless sudo and SSH login
###############################################################################
ARG TEST_USER=tester

RUN set -xe; \
    if [ -n "${TEST}${DEV}" ]; then \
      adduser ${TEST_USER} --shell /bin/bash; \
      echo ${TEST_USER} ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/${TEST_USER}; \
      chmod 0440 /etc/sudoers.d/${TEST_USER}; \
      adduser ${TEST_USER} sudo; \
      # Initialize ~/.ssh
      mkdir -p /home/${TEST_USER}/.ssh; \
      touch /home/${TEST_USER}/.ssh/authorized_keys; \
      # Generate a private key and configure it as an authorized key
      ssh-keygen -t ed25519 -N '' -C uno@test -f /home/${TEST_USER}/.ssh/id_ed25519; \
      cat /home/${TEST_USER}/.ssh/id_ed25519.pub >> /home/${TEST_USER}/.ssh/authorized_keys; \
      # Adjust permissions
      chown -R ${TEST_USER}:${TEST_USER} /home/${TEST_USER}/.ssh; \
    fi


