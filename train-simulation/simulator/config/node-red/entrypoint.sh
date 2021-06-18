#!/bin/sh

# Commit of node-red.trainsim repository
TRAINSIM_COMMIT="55175d378c71921a1e1ce0e391d2a7735d198b58"
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