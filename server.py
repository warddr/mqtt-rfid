import paho.mqtt.client as mqtt
import sqlite3

conn = sqlite3.connect('rfid.db')
cursor = conn.cursor()

publishtopic = "AP/rfid/deur/"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("AP/rfid/lezer/+")

def on_message(client, userdata, msg):
    bericht = (msg.payload.decode("utf-8").split("\r")[0])
    devid = (msg.topic.split("/")[3])
    cursor.execute("SELECT * FROM badges WHERE kaart = ?",(bericht,))
    rows = cursor.fetchall()
    toegang = len(rows)
    cursor.execute("INSERT INTO log(lezer, kaart, toegestaan) VALUES (?,?,?)",(devid,bericht,toegang))
    conn.commit()
    client.publish(publishtopic + devid, toegang);
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(username="IoT",password="DitIsGoed")
client.connect("broker.emqx.io", 1883, 60)

client.loop_forever()



