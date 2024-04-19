#!/bin/sh
set -ex

PKG_NAME=${1:?missing required argument PKG_NAME}
BUILD_DIR=${2:-$(cd $(dirname $0)/../.. && pwd)}

git config --global --add safe.directory ${BUILD_DIR}
make -C ${BUILD_DIR} tarball
(cd ${BUILD_DIR} && debuild)
mkdir -p ${BUILD_DIR}/debian-dist
mv -v \
 ${BUILD_DIR}/../uno*.deb \
 ${BUILD_DIR}/../uno*.debian.tar.xz \
 ${BUILD_DIR}/../uno*.dsc \
 ${BUILD_DIR}/../uno*.changes \
 ${BUILD_DIR}/../uno*.orig.tar.xz \
 ${BUILD_DIR}/debian-dist/
