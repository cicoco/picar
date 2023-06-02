import json
import logging
import time
import uuid

from mycar import MyCar
from myclient import MyClient

DEVICE_CODE = "WSCPCG100000001"
PRODUCT_KEY = "49KaPBUogOO7"
MQTT_USERNAME = "wesine"
MQTT_PASSWORD = "wesine"
MQTT_BROKER_HOST = "58.49.184.55"
MQTT_BROKER_PORT = 1883

running = True

if __name__ == '__main__':

    logging.basicConfig(filename='all.log', level=logging.DEBUG)
    # logging.basicConfig(level=logging.DEBUG)

    frontRight = 11
    frontLeft = 15
    backRight = 12
    backLeft = 13

    car = MyCar(frontLeft, frontRight, backLeft, backRight)
    mqtt_client = MyClient(MQTT_BROKER_HOST, MQTT_BROKER_PORT, DEVICE_CODE, MQTT_USERNAME, MQTT_PASSWORD)


    def on_message_callback(client, userdata, message):
        global running
        topic = message.topic
        payload = json.loads(message.payload.decode('utf-8'))

        if topic is not None and payload is not None:
            data = payload.get('data')
            if data is not None:
                cmd = data.get('cmd')
                logging.debug("收到命令:" + cmd)
                if cmd == "p":
                    running = False
                elif cmd == "w":
                    car.go_forward()
                elif cmd == "s":
                    car.go_back()
                elif cmd == "a":
                    car.to_left()
                elif cmd == "d":
                    car.to_right()
                elif cmd == "n":
                    car.stop()


    last_time = 0

    def on_my_disconnect(client, userdata, rc):
        global last_time
        last_time = 0
        mqtt_client.unsubscribe(f"ws/{DEVICE_CODE}/v1/{PRODUCT_KEY}/command/control")


    def on_my_connect(client, userdata, flags, rc):
        mqtt_client.subscribe(f"ws/{DEVICE_CODE}/v1/{PRODUCT_KEY}/command/control", on_message_callback)


    mqtt_client.on_disconnect = on_my_disconnect
    mqtt_client.on_connect = on_my_connect

    mqtt_client.connect()

    while running:
        current_time = int(time.time() * 1000)
        if mqtt_client.is_connect() and (current_time - last_time) > 60000:
            payload = {"mid": str(uuid.uuid4()),
                       "ts": current_time,
                       "sn": f"{DEVICE_CODE}",
                       "data": {"online": 1}
                       }
            mqtt_client.publish(f"ws/sys/v1/{PRODUCT_KEY}/status", json.dumps(payload))
            last_time = current_time

        time.sleep(1)

    logging.info("结束小车活动")
    mqtt_client.disconnect()
    del car
