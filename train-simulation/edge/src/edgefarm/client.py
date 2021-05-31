import io
import edgefarm.avro as avro
import edgefarm.schema as schema


class RegisterResponse:
    def __init__(self, subject, error):
        self.subject = subject
        self.error = error


async def register_mqtt_topic(target, topic, nats_client):
    msg = [
        {u'topic': topic}
    ]
    data = avro.schema_encode(msg, schema.register_sub_request_codec)

    resp_msg = await nats_client.request(target + ".config.register", data, timeout=2)
    resp = avro.schema_decode(io.BytesIO(resp_msg.data))
    r = RegisterResponse(subject=resp["subject"], error=resp["error"])
    error = resp["error"]
    if len(error) > 0:
        print("Error: " + error)
    return r


async def unergister_mqtt_topic(target, subject, nats_client):
    msg = [
        {u'subject': subject}
    ]
    data = avro.schema_encode(msg, schema.unregister_sub_request_codec)
    try:
        resp_msg = await nats_client.request(target + ".config.unregister", data, timeout=2)
    except Exception as e:
        raise Exception("Error: timeout to alm-mqtt-module {}".format(e))
    resp = avro.schema_decode(io.BytesIO(resp_msg.data))
    error = resp["error"]
    if len(error) > 0:
        print("Error: " + error)
