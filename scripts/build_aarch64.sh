#!/bin/bash
#
# If running the build on an x86_64 machine, install the QEMU emulator dependencies
# and run the multiarch/qemu-user-static image.
# 
# $ sudo apt-get install qemu binfmt-support qemu-user-static
# $ docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
#
# Run this file from the root project directory.
# $ ./scripts/build_aarch64.sh

set -e -x

distname="eflexcan2mqtt_aarch64"

# Path where PyInstaller will output application files.
distdir="./dist/aarch64"

docker build -f Dockerfile_aarch64 -t eflexcan2mqtt_aarch64_builder .

# Run PyInstaller build
docker run --user $(id -u):$(id -g) --rm -it -v "$PWD:/src" eflexcan2mqtt_aarch64_builder eflexcan2mqtt.spec --distpath $distdir/$distname --workpath ./build/x86_64 --noconfirm

# Copy additional files to dist directory
cp ./conf/eflexcan2mqtt.ini.dist $distdir/$distname/eflexcan2mqtt.ini
cp ./scripts/eflexcan2mqtt.service $distdir/$distname
cp ./scripts/install.sh $distdir/$distname

# Create dist package
tar -czf ./dist/$distname.tgz -C $distdir .

# Clean up PyInstaller files
rm -rf $distdir