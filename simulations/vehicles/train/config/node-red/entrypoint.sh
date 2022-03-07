#!/bin/sh

DIR=`pwd`

cd /data

mkdir -p tmp
wget "https://github.com/edgefarm/${REPOSITORY_NAME:-node-red.trainsim}/archive/${REPOSITORY_COMMIT:-refs/heads/main}.zip" -P tmp
unzip -o tmp/*.zip -d tmp/

rm -rf projects/trainsim/data/ | true
mkdir -p projects/trainsim/data/
mv -f tmp/${REPOSITORY_NAME:-node-red.trainsim}-${REPOSITORY_COMMIT:-main}/data/* projects/trainsim/data/
rm -r tmp/${REPOSITORY_NAME:-node-red.trainsim}-${REPOSITORY_COMMIT:-main}/data
mv -f tmp/${REPOSITORY_NAME:-node-red.trainsim}-${REPOSITORY_COMMIT:-main}/* .

rm -r tmp
mv -f flows_cred.json flow_cred.json

npm install

cd "$DIR"
npm start -- --userDir /data
