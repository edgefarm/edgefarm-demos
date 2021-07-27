#!/bin/sh

DIR=`pwd`

cd /data

mkdir -p tmp
wget "https://github.com/edgefarm/${REPOSITORY}/archive/${TRAINSIM_COMMIT}.zip" -P tmp
unzip -o tmp/${TRAINSIM_COMMIT}.zip -d tmp/

mkdir -p projects/trainsim/data/
mv -f tmp/${REPOSITORY}-${TRAINSIM_COMMIT}/data/* projects/trainsim/data/
mv -f tmp/${REPOSITORY}-${TRAINSIM_COMMIT}/* .

rm -r tmp


mv -f flows_cred.json flow_cred.json

npm install

cd "$DIR"
npm start -- --userDir /data
