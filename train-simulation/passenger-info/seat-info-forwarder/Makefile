LOCAL_SCHEMAS_GIT_COMMIT_ID = $(VERSION)
LOCAL_SCHEMAS_REPO = https://raw.githubusercontent.com/edgefarm/edgefarm-demos/$(LOCAL_SCHEMAS_GIT_COMMIT_ID)/train-simulation/schemas
CURL = curl --silent --show-error --fail -O

# install_dependencies is supposed to be called only when building docker image. Otherwise VERSION is undefined
# VERSION can be provided by executing `export VERSION="$(git rev-parse --short HEAD)"` before.
install_dependencies:
ifdef VERSION
	mkdir -p src/schemas && cd src/schemas && \
	${CURL} ${LOCAL_SCHEMAS_REPO}/seat-info-request.avsc && \
	${CURL} ${LOCAL_SCHEMAS_REPO}/seat-info-response.avsc
else
	@echo "VERSION not set! Schemas will not be copied"
endif

install_requirements:
	pip3 install -r requirements.txt

.PHONY: install_requirements
