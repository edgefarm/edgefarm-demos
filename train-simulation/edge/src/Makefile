install_dependencies:
	mkdir -p edgefarm/avro_schemas && cd edgefarm/avro_schemas && \
	curl -O https://raw.githubusercontent.com/edgefarm/alm-service-modules/main/alm-mqtt-module/pkg/schema/avro_schemas/registerSubRequest.avro && \
	curl -O https://raw.githubusercontent.com/edgefarm/alm-service-modules/main/alm-mqtt-module/pkg/schema/avro_schemas/registerSubResponse.avro && \
	curl -O https://raw.githubusercontent.com/edgefarm/alm-service-modules/main/alm-mqtt-module/pkg/schema/avro_schemas/unregisterSubRequest.avro && \
	curl -O https://raw.githubusercontent.com/edgefarm/alm-service-modules/main/alm-mqtt-module/pkg/schema/avro_schemas/unregisterSubResponse.avro && \
	curl -O https://raw.githubusercontent.com/edgefarm/alm-service-modules/main/alm-mqtt-module/pkg/client/avro_schemas/dataSchema.avro

	mkdir -p edgefarm/ads_schemas && cd edgefarm/ads_schemas && \
	curl -O https://raw.githubusercontent.com/edgefarm/ads_schemas/main/ads_data.avsc && \
	curl -O https://raw.githubusercontent.com/edgefarm/ads_schemas/main/temperature_data.avsc && \
	curl -O https://raw.githubusercontent.com/edgefarm/ads_schemas/main/gps_data.avsc && \
	curl -O https://raw.githubusercontent.com/edgefarm/ads_schemas/main/mvb_data.avsc

install_requirements:
	pip3 install -r requirements.txt

test:
	python3 -m unittest tests/avro_test.py

.PHONY: install_dependencies install_requirements
