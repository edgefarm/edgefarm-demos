import fastavro


register_sub_request_codec = fastavro.schema.load_schema(
    "edgefarm/avro_schemas/registerSubRequest.avro")
unregister_sub_request_codec = fastavro.schema.load_schema(
    "edgefarm/avro_schemas/unregisterSubRequest.avro")
register_sub_response_codec = fastavro.schema.load_schema(
    "edgefarm/avro_schemas/registerSubResponse.avro")
unregister_sub_response_codec = fastavro.schema.load_schema(
    "edgefarm/avro_schemas/unregisterSubResponse.avro")
data_codec = fastavro.schema.load_schema(
    "edgefarm/avro_schemas/dataSchema.avro")
ads_codec = fastavro.schema.load_schema(
    "edgefarm/ads-schemas/ads_data.avsc")
