from io import BytesIO
from fastavro import writer, reader, schemaless_writer


def schema_encode(msg, schema):
    '''
    Binary encoding of message. Schema is part of binary.
    Return binary as bytes.
    '''
    fo = BytesIO()
    writer(fo=fo, schema=schema, records=msg)
    fo.seek(0)
    return fo.read()


def schema_decode(data):
    '''
    Decoding of an Avro binary that contains the schema.
    Return the first decoded message
    '''
    avro_reader = reader(data)
    # Returning all other records. Only returning the first one.
    for record in avro_reader:
        return record


def schemaless_encode(msg, schema):
    '''
    Binary encoding of message. Schema is NOT part of binary.
    Return binary as bytes.
    '''
    fo = BytesIO()
    schemaless_writer(fo=fo, schema=schema, record=msg)
    fo.seek(0)
    return fo.read()
