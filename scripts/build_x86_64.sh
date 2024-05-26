#!/bin/bash
# Run this file from the root project directory.
# $ ./scripts/build_x86_64.sh

set -e -x

distname="eflexcan2mqtt_x86_64"

# Path where PyInstaller will output application files.
distdir="./dist/x86_64"

docker build -f Dockerfile_x86_64 -t eflexcan2mqtt_x86_64_builder .

# Run PyInstaller build
docker run --user $(id -u):$(id -g) --rm -it -v "$PWD:/src" eflexcan2mqtt_x86_64_builder eflexcan2mqtt.spec --distpath $distdir/$distname --workpath ./build/x86_64 --noconfirm

# Copy additional files to dist directory
cp ./conf/eflexcan2mqtt.ini.dist $distdir/$distname/eflexcan2mqtt.ini
cp ./scripts/eflexcan2mqtt.service $distdir/$distname
cp ./scripts/install.sh $distdir/$distname

# Create dist package
tar -czf ./dist/$distname.tgz -C $distdir .

# Clean up PyInstaller files
rm -rf $distdir

