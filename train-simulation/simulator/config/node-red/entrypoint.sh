#!/bin/sh

# Commit of node-red.trainsim repository
TRAINSIM_COMMIT="b4a68f144e33fba3b053ff92503e352426f2fdc8"
REPOSITORY="node-red.trainsim"

DIR=`pwd`

cd /data

wget "https://github.com/edgefarm/${REPOSITORY}/archive/${TRAINSIM_COMMIT}.zip"
unzip ${TRAINSIM_COMMIT}.zip
cp ${REPOSITORY}-${TRAINSIM_COMMIT}/* .
rm ${TRAINSIM_COMMIT}.zip
rm -r ${REPOSITORY}-${TRAINSIM_COMMIT}
mv flows_cred.json flow_cred.json

npm install

cd "$DIR"
npm start -- --userDir /data