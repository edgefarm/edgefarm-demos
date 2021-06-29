#!/bin/sh

DIR=`pwd`

cd /data

wget "https://github.com/edgefarm/${REPOSITORY}/archive/${TRAINSIM_COMMIT}.zip"
unzip -jo ${TRAINSIM_COMMIT}.zip "${REPOSITORY}-${TRAINSIM_COMMIT}/*" -d .
rm ${TRAINSIM_COMMIT}.zip
mv flows_cred.json flow_cred.json

npm install

cd "$DIR"
npm start -- --userDir /data