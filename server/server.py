from mqtt_client import MQTTClient
import time

def recv(client, feed_id, payload):
    print(f"Got {payload} from {feed_id}")

def conn(client):
    print("Connected, subscribing....")
    client.subscribe("therm", feed_user='pico')
    client.subscribe("warnings", feed_user='pico')
    client.subscribe("acks", feed_user='pico')


client = MQTTClient("server", "password", service_host="192.168.0.103", secure=False, port=5005)
client.on_message = recv
client.on_connect = conn
client.connect()
time.sleep(1)


while True:
    client.loop(timeout_sec=1.0)
    command = input("Command: ")
    client.publish("commands", command)
    time.sleep(1)

