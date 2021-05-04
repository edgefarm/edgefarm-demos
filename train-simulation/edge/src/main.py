import io
import signal
import sys
import asyncio
import edgefarm.avro as avro
from edgefarm.alm_mqtt_module_client import AlmMqttModuleClient


async def temperature_handler(msg):
    """This is the handler function that gets registered for `simulation/temperature`.
    The data is encoded using `Apache avro` with the schema from the file `edgefarm/avro_schemas/dataSchema.avro`."""
    message = avro.new_reader(io.BytesIO(msg.data))
    print(message)


# You can register multiple handlers for the same MQTT topic.
# Example:
# topics = {
#   'simulation/temperature': [temp_handler1, temp_handler2],
#   'simulation/acceleration': [accel_handler]
# }
topics = {
    'simulation/temperature': [temperature_handler]
}

# This is to store corresponding nats subjects to handler functions for specific MQTT topics.Exception
# Example for accessing subjects from topics example above:
# Let's access the corresponding nats subject for `temp_handler2` for `simulation/temperature`
# print(subjects["simulation/temperature"][1])
subjects = {}


async def run(loop):
    client = AlmMqttModuleClient(loop)

    await client.connect()
    try:
        for key in topics:
            print("Registering to '{}'".format(key))
            for handler in topics[key]:
                subject = await client.subscribe(key, handler)
                if key not in subjects:
                    subjects[key] = list()
                subjects[key].append(subject)
                print("-> corresponding nats subject: '{}'".format(subject))
    except Exception as e:
        sys.stderr.write(f"Error: '{e}'")
        exit(1)

    def signal_handler():
        print("Unsubscribing and shutting down...")
        loop.create_task(client.close())

    for sig in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, sig), signal_handler)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    try:
        loop.run_forever()
    finally:
        loop.close()
