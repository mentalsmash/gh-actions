# TODO update default base image
ARG BASE_IMAGE="ubuntu:22.04"
FROM ${BASE_IMAGE}

# TODO update labels to match project
LABEL org.opencontainers.image.source=https://example.com/johndoe/example-repository.git
LABEL org.opencontainers.image.licenses=Apache-2.0
LABEL org.opencontainers.image.vendor="John Doe"

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
    # TODO Install project dependencies
    # apt-get install -y --no-install-recommends ... ; \
    apt-get clean

ENV LANG en_US.UTF-8

