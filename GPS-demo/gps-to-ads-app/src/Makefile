install_dependencies:
	mkdir -p edgefarm/ads_schemas && cd edgefarm/ads_schemas && \
	curl -O https://raw.githubusercontent.com/edgefarm/ads-schemas/main/ads_data.avsc && \
	curl -O https://raw.githubusercontent.com/edgefarm/ads-schemas/main/gps_data.avsc

install_requirements:
	pip3 install -r requirements.txt

.PHONY: install_dependencies install_requirements
