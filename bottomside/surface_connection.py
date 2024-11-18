import json
from threading import Lock
import paho.mqtt.client as mqtt


class SurfaceConnection:
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

        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.on_disconnect = self._on_disconnect
        self._client.on_publish = self._on_publish
        self._client.on_subscribe = self._on_subscribe

        self._subscription_lock = Lock()
        self._subscriptions: dict[str, str | float] = {}

    def connect(self):
        self._client.connect(self._ip, self._port)
        self._client.loop_start()

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

    def get_subscription_dict(self) -> dict[str, str | float]:
        """Get the subscription dictionary values.

        Returns:
            dict[str, str | float]:
                The subscription dictionary.
        """
        with self._subscription_lock:
            return self._subscriptions

    def send_data(self, sensor_data: dict[str, str | float], status: str | float,
                  other: dict[str, str | float]) -> None:
        """Send a packet from the Raspberry Pi with the specified sensor data and other data.

        Args:
            sensor_data (dict[str, str | float]):
                The sensor data to send to the surface.
            status (str | float):
                The status of the ROV, whether in string or numeric form.
            other (dict[str, str | float]):
                Other data to send to the surface, such as error/success codes.
        """
        self._client.publish("ROV_sensor_data", json.dumps(sensor_data))
        self._client.publish("ROV_status", json.dumps(status))
        self._client.publish("ROV_other", json.dumps(other))

    def _on_message(self, client, userdata, message):
        print(f"Received message '{message.payload.decode()}' on topic '{message.topic}'")

        if message.topic == "subscribe":
            self.subscribe(message.payload.decode())
        else:
            self.set_subscription_value(message.topic, int(message.payload.decode()))

    def _on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")

        client.subscribe("subscribe")
        client.subscribe("thruster_pwm/FRONT_RIGHT")
        client.subscribe("thruster_pwm/REAR_RIGHT")
        client.subscribe("thruster_pwm/FRONT_LEFT")
        client.subscribe("thruster_pwm/REAR_LEFT")
        client.subscribe("thruster_pwm/FRONT_RIGHT_VERTICAL")
        client.subscribe("thruster_pwm/REAR_RIGHT_VERTICAL")
        client.subscribe("thruster_pwm/FRONT_LEFT_VERTICAL")
        client.subscribe("thruster_pwm/REAR_LEFT_VERTICAL")

    def _on_disconnect(self, client, userdata, rc):
        print(f"Disconnected with result code {rc}")

    def _on_publish(self, client, userdata, mid):
        print(f"Published message with mid {mid}")

    def _on_subscribe(self, client, userdata, mid, granted_qos):
        print(f"Subscribed to topic with mid {mid} and QoS {granted_qos}")

    def disconnect(self):
        self._client.loop_stop()
        self._client.disconnect()


if __name__ == "__main__":
    connection = SurfaceConnection()
    connection.connect()
