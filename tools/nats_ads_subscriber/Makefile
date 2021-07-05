ADS_SCHEMAS_GIT_COMMIT_ID = 28bc8c23c140da6ff21539b2780b07c3e8c1b81b
install_dependencies:
	mkdir -p schemas && cd schemas && \
	curl -O https://raw.githubusercontent.com/edgefarm/ads-schemas/${ADS_SCHEMAS_GIT_COMMIT_ID}/ads_data.avsc && \
	curl -O https://raw.githubusercontent.com/edgefarm/ads-schemas/${ADS_SCHEMAS_GIT_COMMIT_ID}/gps_data.avsc && \
	curl -O https://raw.githubusercontent.com/edgefarm/ads-schemas/${ADS_SCHEMAS_GIT_COMMIT_ID}/temperature_data.avsc

.PHONY: install_dependencies
