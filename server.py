"""
This is the server code, which retrieves the messages from the MQTT server, send from the ESP32 with its RFID reader.
Every student has its own Topic to publish the messages to. The server subscribes to the "AP/rfid/lezer/<student id>/+"
topic. When the ESP32 publishes messages to it, it will parse the message (only retrieve first line) and store it
in its sqlite3 database.
The server sends back the number of messages it has received from that card UID on the topic AP/rfid/deur/<student id>.

The message is the username or user identity on the card
"""
import paho.mqtt.client as mqtt
import sqlite3

# Replace with the IP address of your targeted MQTT message broker (install a Mosquitto on a Pi)
mqtt_server = "<IP MQTT broker>"
mqtt_student_id = "<Your ID with no spaces>"

# Create a sqlite3 database
conn = sqlite3.connect('rfid.db')
conn.execute('''
    CREATE TABLE IF NOT EXISTS log(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tijd DATETIME DEFAULT CURRENT_TIMESTAMP,
    lezer INTEGER,
    kaart TEXT,
    toegestaan INTEGER
    );
''')
conn.execute('''
CREATE TABLE IF NOT EXISTS badges(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 kaart TEXT
);
''')
conn.commit()

# create cursor to store elements
cursor = conn.cursor()
# topic to publish message where IoT devices can subscribe to
publish_topic = f"AP/rfid/deur/{mqtt_student_id}/"


def on_connect(client, userdata, flags, rc):
    """
    Callback function when the sever connect to the MQTT message broker

    :param client: client connection when connected.
    :param userdata:
    :param flags:
    :param rc: return code when succeeded or failed
    :return:
    """
    # logging of connection
    print("Connected with result code "+str(rc))
    # This server subscribes to MQTT broker to the channel
    client.subscribe(f"AP/rfid/lezer/{mqtt_student_id}/+")


def on_message(client, userdata, msg):
    """
    Callback function when a message was received on the AP/rfid/lezer/<student id>/+. The + is normally the <card uid>.

    :param client: client connection which can be used to publish (send) messages back to IoT device
    :param userdata:
    :param msg: the message content the IoT device published (send) on the topic AP/rfid/lezer/<student id>/<card uid>
    :return:
    """
    # Message send over, we retrieve only the first line (user of the card)
    bericht = (msg.payload.decode("utf-8").split("\r")[0])
    # Get the Card UID from the topic
    devid = (msg.topic.split("/")[4])
    # Check if user identity is present in db, if 0 then 'no access' to the door
    cursor.execute("SELECT * FROM badges WHERE kaart = ?",(bericht,))
    rows = cursor.fetchall()
    toegang = len(rows)
    # Insert the access to the audit data
    cursor.execute("INSERT INTO log(lezer, kaart, toegestaan) VALUES (?,?,?)",(devid,bericht,toegang))
    conn.commit()
    # Print some data to screen
    print(f"Got mqtt message with: {devid} {bericht} {toegang}")
    # Send message back to IoT device to say it has access (toegang > 0) or not (toegang == 0)
    client.publish(publish_topic + devid, toegang);


# Initialize the mqtt client and assign the callback functions
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message


if __name__ == '__main__':
    # Connect to MQTT broker and wait for messages to arrive.
    client.username_pw_set(username="IoT",password="DitIsGoed")
    client.connect(mqtt_server, 1883, 60)
    client.loop_forever()



