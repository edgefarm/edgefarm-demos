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
    data = avro.new_writer(msg, schema.register_sub_request_codec)
    data.seek(0)

    resp_msg = await nats_client.request(target+".config.register", data.read(), timeout=2)
    resp = avro.new_reader(io.BytesIO(resp_msg.data))
    r = RegisterResponse(subject=resp["subject"], error=resp["error"])
    error = resp["error"]
    if len(error) > 0:
        print("Error: "+error)
    return r


async def unergister_mqtt_topic(target, subject, nats_client):
    msg = [
        {u'subject': subject}
    ]
    data = avro.new_writer(msg, schema.unregister_sub_request_codec)
    data.seek(0)
    try:
        resp_msg = await nats_client.request(target+".config.unregister", data.read(), timeout=2)
    except Exception as e:
        raise Exception("Error: timeout to alm-mqtt-module {}".format(e))
    resp = avro.new_reader(io.BytesIO(resp_msg.data))
    error = resp["error"]
    if len(error) > 0:
        print("Error: "+error)
