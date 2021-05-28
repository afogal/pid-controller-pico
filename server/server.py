from mqtt_client import MQTTClient
import time
import json

def recv(client, feed_id, payload):
    global acked
    print(f"Got {payload} from {feed_id}")

    if feed_id == "ack" and payload == "ACK":
        acked = True

def conn(client):
    print("Connected, subscribing....")
    client.subscribe("therm", feed_user='pico')
    client.subscribe("warnings", feed_user='pico')
    client.subscribe("ack", feed_user='pico')


client = MQTTClient("server", "password", service_host="192.168.0.103", secure=False, port=5005)
client.on_message = recv
client.on_connect = conn
client.connect()
time.sleep(1)


acked = True
last = time.monotonic_ns()
while True:
    try:
        curr = time.monotonic_ns()
        if not acked and (curr - last) > 20e9:
            print("Still haven't gotten ack!!")
            if (curr - last) > 30e9:
                print("Still no ack, shutting off warning")
                acked = True
                
        client.loop(timeout_sec=1.0)
        time.sleep(1)
    except KeyboardInterrupt:
        command = input("Command: ")
        client.publish("commands", json.dumps({"command":command, "temp":0}))
        last = time.monotonic_ns()
        acked = False

