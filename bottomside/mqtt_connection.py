import copy
import json
from threading import Lock
import paho.mqtt.client as mqtt


class MQTTConnection:
    def __init__(self, ip: str = "localhost", port: int = 1883, client_id: str = "ROV") -> None:
        """Initialize the SurfaceConnection object.

        Args:
            ip (str, optional):
                The IP address of the MQTT broker.
                Defaults to "localhost".
            port (int, optional):
                The port of the MQTT broker.
                Defaults to 1883.
            client_id (str, optional):
                The name of the ROV.
                Defaults to "ROV".
        """
        self._ip = ip
        self._port = port
        self._rov_name = client_id

        self._connection_wanted = True

        self._client = mqtt.Client(client_id=client_id)

        # Set the callback functions.
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.on_disconnect = self._on_disconnect
        self._client.on_publish = self._on_publish
        self._client.on_subscribe = self._on_subscribe

        # Set up a locked subscription dictionary.
        self._subscription_lock = Lock()
        self._subscriptions: dict[str, str | float | int] = {}
        self._new_subscriptions: dict[str, str | float | int] = {}

        self._sent_vals: dict[str, str | float | int] = {}

    def connect(self):
        self._client.connect(self._ip, self._port)
        self.start_listening()

    def subscribe(self, topic: str) -> None:
        """Subscribe to the specified topic.

        Args:
            topic (str):
                The topic to subscribe to.
        """
        self._client.subscribe(topic)

    def set_subscription_value(self, sub: str, value: str | float) -> None:
        """Set the subscription dictionary values.

        Args:
            sub (str):
                The subscription to set the value for.
            value (str | float):
                The value to set the subscription to.
        """
        with self._subscription_lock:
            self._subscriptions[sub] = value

    def set_new_subscription_value(self, sub: str, value: str | float | int) -> None:
        """Set the new subscription dictionary values that have changed since the last call.

        Args:
            sub (str):
                The subscription to set the value for.
            value (str | float | int):
                The value to set the subscription to.
        """
        with self._subscription_lock:
            self._new_subscriptions[sub] = value

    def get_subscription_dict(self) -> dict[str, str | float | int]:
        """Get the subscription dictionary values.

        Returns:
            dict[str, str | float | int]:
                The subscription dictionary.
        """
        with self._subscription_lock:
            return self._subscriptions

    def get_new_subscription_dict(self) -> dict[str, str | float | int]:
        """Get any subscription dictionary values that have changed since the last call.

        Returns:
            dict[str, str | float | int]:
                The subscription dictionary.
        """
        with self._subscription_lock:
            subs = copy.deepcopy(self._new_subscriptions)
            self._subscriptions |= self._new_subscriptions
            self._new_subscriptions = {}

        return subs

    def send_data(self, gpio_data: dict[str, int], i2c_data: dict[str, dict[int, bytes]], status: str | float,
                  other: dict[str, str | float] | None = None) -> None:
        """Send a packet from the Raspberry Pi with the specified sensor data and other data.

        Args:
            gpio_data (dict[str, int]):
                The GPIO data to send to the surface.
            i2c_data (dict[str, dict[int, bytes]]):
                The I2C data to send to the surface.
            status (str | float):
                The status of the ROV, whether in string or numeric form.
            other (dict[str, str | float] | None, optional):
                Any other data to send to the surface.
                Defaults to None.
        """
        for name, value in gpio_data.items():
            self._publish_if_changed(f"ROV/GPIO/{name}", str(value))

        for name, value in i2c_data.items():
            for sub_key, sub_value in value.items():
                self._publish_if_changed(f"ROV/I2C/{name}/{sub_key}", sub_value)

        self._publish_if_changed("ROV/status", json.dumps(status))
        self._publish_if_changed("ROV/other", json.dumps(other))

    def _publish_if_changed(self, topic: str, payload) -> None:
        """Publish the data if it has changed from the previous value.

        Args:
            topic (str):
                The topic to publish the data to.
            payload:
                The data to publish.
        """
        if topic not in self._sent_vals or self._sent_vals[topic] != payload:
            self._sent_vals[topic] = payload
            self._client.publish(topic, payload)

    def _on_message(self, client, userdata, message):
        if message.topic == "PC/commands/subscribe":
            self.subscribe(message.payload.decode())
        else:
            self.set_new_subscription_value(message.topic, message.payload.decode())

    def _on_connect(self, client, userdata, flags, rc) -> None:
        print(f"Connected with result code {rc}")

        client.subscribe("PC/commands/#")
        client.subscribe(f"PC/pins/#")
        client.subscribe(f"PC/i2c/#")

    def _on_disconnect(self, client, userdata, rc) -> None:
        print(f"Disconnected with result code {rc}")

    def _on_publish(self, client, userdata, mid) -> None:
        print(f"Published message with mid {mid}")

    def _on_subscribe(self, client, userdata, mid, granted_qos) -> None:
        print(f"Subscribed to topic with mid {mid} and QoS {granted_qos}")

    def stop_listening(self) -> None:
        """Stop listening for messages from the MQTT broker."""
        self._client.loop_stop()

        print("Stopped listening for messages.")

    def start_listening(self) -> None:
        """Start listening for messages from the MQTT broker."""
        self._client.loop_start()

        print("Started listening for messages.")

    def disconnect(self) -> None:
        """Disconnect from the MQTT broker."""
        self.stop_listening()
        self._client.disconnect()

        print("Disconnected from MQTT broker.")


if __name__ == "__main__":
    connection = MQTTConnection()
    connection.connect()

