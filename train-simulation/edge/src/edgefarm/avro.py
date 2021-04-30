from io import BytesIO
from fastavro import writer, reader


def new_writer(msg, schema):
    fo = BytesIO()
    writer(fo=fo, schema=schema, records=msg)
    fo.seek(0)
    return fo


def new_reader(data):
    avro_reader = reader(data)
    # Returning all other records. Only returning the first one.
    for record in avro_reader:
        return record
