#!/bin/bash

<<<<<<< HEAD
# For each concourse pipeline, create an entry in IMAGES and a corresponding entry in CONTEXTS
#  entry in IMAGES = the name of the docker image to build, without specifying the repository and tag.
#                    This also defines the name of the pipeline in concourse (demo-<image-name>)
#  entry in CONTEXTS = The docker build context (path to the directory within this repo)
#

IMAGES=(
  gps-to-ads-app
  train-simulator-edge-app
  )

CONTEXTS=(
  GPS-demo/gps-to-ads-app/src
  train-simulation/edge/src
)

for i in "${!IMAGES[@]}"; do
  IMAGE_BASENAME=${IMAGES[i]}
  CONTEXT=${CONTEXTS[i]}
  echo "***********"
  echo "setting pipelines for ${IMAGE_BASENAME}, context=${CONTEXT}"
  echo "***********"

  fly -t prod set-pipeline -p demo-${IMAGE_BASENAME} -c pipeline.yaml -l ci/config.yaml  -l ci/credentials.yaml  \
    -v docker-image-basename=${IMAGE_BASENAME} -v docker-context=${CONTEXT}

  fly -t prod set-pipeline -p demo-${IMAGE_BASENAME}-pull-requests -c pipeline-pullrequests.yaml -l ci/config.yaml  -l ci/credentials-pullrequests.yaml \
    -v docker-image-basename=${IMAGE_BASENAME} -v docker-context=${CONTEXT}

done
=======
IMAGE_BASENAME=gps-to-ads-app
CONTEXT=GPS-demo/gps-to-ads-app/src
fly -t prod set-pipeline -p demo-${IMAGE_BASENAME} -c pipeline.yaml -l ci/config.yaml  -l ci/credentials.yaml  \
  -v docker-image-basename=${IMAGE_BASENAME} -v docker-context=${CONTEXT}

fly -t prod set-pipeline -p demo-${IMAGE_BASENAME}-pull-requests -c pipeline-pullrequests.yaml -l ci/config.yaml  -l ci/credentials-pullrequests.yaml \
  -v docker-image-basename=${IMAGE_BASENAME} -v docker-context=${CONTEXT}


IMAGE_BASENAME=train-simulator-edge-app
CONTEXT=train-simulation/edge/src
fly -t prod set-pipeline -p demo-${IMAGE_BASENAME} -c pipeline.yaml -l ci/config.yaml  -l ci/credentials.yaml  \
  -v docker-image-basename=${IMAGE_BASENAME} -v docker-context=${CONTEXT}

fly -t prod set-pipeline -p demo-${IMAGE_BASENAME}-pull-requests -c pipeline-pullrequests.yaml -l ci/config.yaml  -l ci/credentials-pullrequests.yaml \
  -v docker-image-basename=${IMAGE_BASENAME} -v docker-context=${CONTEXT}
>>>>>>> create global pipeline instead ofsingle pipeline for each app
