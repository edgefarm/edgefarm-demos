import os
from nats.aio.client import Client as Nats
import edgefarm.client as client


class AlmMqttModuleClient:
    """A class to interact with the `alm-mqtt-module`. It supports
    registering and unregistering to MQTT topics proxied over nats
    via `alm-mqtt-module`."""

    __subjects = {}
    __subject_handlers = {}

    """Internal storage for nats subjects and its corresponding subscription id's"""

    def __init__(self, loop):
        """Initialize the Edgefarm object with an asyncio loop.

        Example usage:
        ```
        async def run(loop):
            mqttClient = AlmMqttModuleClient(loop)

        if __name__ == '__main__':
            loop = asyncio.get_event_loop()
            loop.run_until_complete(run(loop))
            try:
                loop.run_forever()
            finally:
                loop.close()
        ```
        """
        self.nc = Nats()
        self.loop = loop
        self.serverRunning = False

    async def connect(self):
        """Connect to the nats server.
        You can specify the nats server by defining the environment
        variable `NATS_SERVER`, e.g. `nats:4222`.

        Example usage:
        ```
        mqttClient = AlmMqttModuleClient(loop)
        await mqttClient.connect()
        ```
        """
        nats_server = os.getenv("NATS_SERVER", "nats:4222")
        options = {
            "servers": ["nats://" + nats_server],
            "loop": self.loop,
            "connect_timeout": 10,
            "ping_interval": 1,
            "max_outstanding_pings": 5,
        }

        await self.nc.connect(**options)

    async def close(self):
        """Close the connection to `alm-mqtt-module` and the nats server.

        Example usage:

        ```
        if exit == True:
            loop.create_task(mqttClient.close())
        ```
        """
        await self.__shutdown()

    async def subscribe(self, topic, handler):
        """Subscribe to a MQTT topic and register a handler function.
        The `alm-mqtt-module` returns a nats subject that corresponds to
        the registered MQTT topic to proxy the MQTT messages.

        Example usage:
        ```
        async def handler(msg):
            resp = avro.NewAvroReader(io.BytesIO(msg.data))
            print(resp)

        subject = await mqttClient.subscribe("mqtt/topic", handler)
        ```
        """
        response = await client.register_mqtt_topic("alm-mqtt-module", topic, self.nc)
        self.serverRunning = True
        self.__subjects[response.subject] = await self.nc.subscribe(
            subject=response.subject, cb=self.__nats_handler
        )
        self.__subject_handlers[response.subject] = handler
        return response.subject

    async def __nats_handler(self, msg):
        await self.nc.publish(msg.reply, b"")
        await self.__subject_handlers[msg.subject](msg)

    async def unsubscribe(self, subject):
        """Unsubscribe from a previously registered nats subject.
        Raises an Exception if subject was not found.

        Example usage:

        ```
        subject = await mqttClient.subscribe("mqtt/topic", handler)

        try:
            await mqttClient.unsubscribe(subject)
        except Exception as e:
            print(e)
        ```
        """
        if subject in self.__subjects.keys():
            await client.unergister_mqtt_topic("alm-mqtt-module", subject, self.nc)
            await self.nc.unsubscribe(self.__subjects[subject])
            del self.__subjects[subject]
        else:
            raise Exception("Subject '{}' was not found".format(subject))

    async def __shutdown(self):
        """Internal function for shutting down connections to `alm-mqtt-module` and the nats server"""
        if self.nc.is_closed:
            return
        try:
            for s in list(self.__subjects):
                await self.unsubscribe(s)
        except Exception as e:
            print(e)
            print("alm-mqtt-module not answering. Closing nats connection.")
        try:
            await self.nc.close()
        except Exception as e:
            print(e)
        # await asyncio.sleep(0.1)
