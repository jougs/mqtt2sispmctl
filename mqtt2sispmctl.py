
import paho.mqtt.client as mqttClient
from subprocess import Popen, PIPE
import json
import re

broker = "homehub"
device_name = "Mancave PA"

outlets = {
    "Mancave PA mixer": "1",
    "Mancave PA amplifier 1": "2",
    "Mancave PA amplifier 2": "3",
}

hass_topic = "homeassistant/status"

base_cmd = "sispmctl"


def call_process(call):
    p = Popen(call, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    rc = p.returncode
    return out, err, rc


def on_connect(client, userdata, flags, rc):
    print(f"Connected to broker with result code {rc}")

    for topic in outlets:
        print(f"Subscribing to {topic}")
        client.subscribe(topic + "/command")

    print(f"Subscribing to {hass_topic}")
    client.subscribe(hass_topic)


def get_cmd(base_topic, mode):
    outlet = outlets[base_topic]["outlet"]
    return [base_cmd, mode, outlet]


def on_message(client, userdata, msg):
    print(f"Received '{msg.payload}' on topic '{msg.topic}'")

    if msg.topic == hass_topic and msg.payload == "online":
        announce()
        return

    base_topic = str(msg.topic).rsplit("/", 1)[0]

    mode = "-o" if str(msg.payload).lower()[2:-1] == "on" else "-f"
    print(call_process(get_cmd(base_topic, mode)))

    out, err, _ = call_process(get_cmd(base_topic, "-g"))
    topic = base_topic + '/status'
    state = str(out).rsplit(":", 1)[-1][2:-3].upper()
    print(f"Publishing '{state}' on topic '{topic}'")
    client.publish(topic, state)


def announce():
    """Announce entities to Home Assistant

    """
    out = str(call_process([base_cmd, "-s"])[0])
    serial = re.search("serial number:    (.*?)n", out).group(1)[:-1]
    manufacturer = re.search("^(.*?) ", out).group(1)[2:]
    model = re.search("device type:      (.*?)n", out).group(1)[:-1]
    device_config = {
        "name": device_name,
        "identifiers": [serial],
        "manufacturer": manufacturer,
        "model": model,
    }

    for base_topic, data in outlets.items():
        unique_id = data["name"].lower().replace(" ", "_")
        config = {
            "name": data["name"],
            "command_topic": base_topic + "/command",
            "state_topic": base_topic + "/status",
            "device": device_config,
            "unique_id": unique_id
        }

        config_topic = f"homeassistant/switch/{unique_id}/config"
        print(f"Publishing config for '{data['name']}' on '{config_topic}'")
        client.publish(config_topic, json.dumps(config))


tmp = {}
for name, outlet in outlets.items():
    topic = name.lower().replace(" ", "_")
    tmp[topic] = {"name": name, "outlet": outlet}
outlets = tmp

client = mqttClient.Client(device_name)
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker)

announce()

client.loop_forever()
