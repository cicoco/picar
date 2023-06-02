import json
import time
import uuid

# from mycar import MyCar
from myclient import MyClient

DEVICE_CODE = ""
PRODUCT_KEY = ""
MQTT_USERNAME = ""
MQTT_PASSWORD = ""
MQTT_BROKER_HOST = ""
MQTT_BROKER_PORT = 1883
running = True

if __name__ == '__main__':

    frontRight = 11
    frontLeft = 15
    backRight = 12
    backLeft = 13


    # car = MyCar(frontLeft, frontRight, backLeft, backRight)
    mqtt_client = MyClient(MQTT_BROKER_HOST, MQTT_BROKER_PORT, DEVICE_CODE, MQTT_USERNAME, MQTT_PASSWORD)

    def on_message_callback(client, userdata, message):
        global running
        topic = message.topic
        payload = json.loads(message.payload.decode('utf-8'))

        if topic is not None and payload is not None:
            data = payload.get('data')
            if data is not None:
                # forward,backward,toLeft, toRight, stop
                cmd = data.get('cmd')
                print("收到命令:" + cmd)
                if cmd == "finish":
                    running = False
                # elif cmd == "forward":
                #     car.go_forward()
                # elif cmd == "backward":
                #     car.go_back()
                # elif cmd == "toLeft":
                #     car.to_left()
                # elif cmd == "toRight":
                #     car.to_right()
                # elif cmd == "stop":
                #     car.stop()

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

    print("结束小车活动")
    mqtt_client.disconnect()
    # del car
