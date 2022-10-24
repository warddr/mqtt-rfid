import paho.mqtt.client as mqtt

mqtt_server = "<IP MQTT broker>"
client = mqtt.Client("P1")
client.username_pw_set("IoT", "DitIsGoed")
client.connect(mqtt_server, )
client.publish("AP/rfid/lezer/FFFF","Hello, World!")