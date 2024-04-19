#!/bin/sh
set -ex

PKG_NAME=${1:?missing required argument PKG_NAME}
BUILD_DIR=${2:-$(cd $(dirname $0)/../.. && pwd)}

git config --global --add safe.directory ${BUILD_DIR}
make -C ${BUILD_DIR} tarball
(cd ${BUILD_DIR} && debuild)
mkdir -p ${BUILD_DIR}/debian-dist
mv -v \
 ${BUILD_DIR}/../${PKG_NAME}*.deb \
 ${BUILD_DIR}/../${PKG_NAME}*.debian.tar.xz \
 ${BUILD_DIR}/../${PKG_NAME}*.dsc \
 ${BUILD_DIR}/../${PKG_NAME}*.changes \
 ${BUILD_DIR}/../${PKG_NAME}*.orig.tar.xz \
 ${BUILD_DIR}/debian-dist/
