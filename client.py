"""
Test script to send some messages to the MQTT message broker
"""
import paho.mqtt.client as mqtt
import time

mqtt_server = "<IP MQTT broker>"
mqtt_student_id = "<Your ID with no spaces>"


def on_message(client, userdata, msg):
    """
    Get message from the server.
    """
    # Message send over, we retrieve only the first line (user of the card)
    bericht = (msg.payload.decode("utf-8").split("\r")[0])
    # Print some data to screen
    print(f"Got mqtt message with: {bericht}")


client = mqtt.Client()
client.on_message = on_message
client.username_pw_set("IoT", "DitIsGoed")
client.connect(mqtt_server, 1883, 60)
client.loop_start()
print(f"Subscribe to AP/rfid/deur/{mqtt_student_id}/+")
client.subscribe(f"AP/rfid/deur/{mqtt_student_id}/+")
print(f"Publish 'Test_User_0001' to AP/rfid/lezer/{mqtt_student_id}/FFFF")
client.publish(f"AP/rfid/lezer/{mqtt_student_id}/FFFF", f"Test_User_0001")
print(f"Wait for response")
time.sleep(5)
client.loop_stop()

