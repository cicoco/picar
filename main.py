# -*- coding: utf-8 -*-
import atexit
import json
import logging
import os
import subprocess
import time
import uuid
import psutil

from mycar import MyCar
from myclient import MyClient

DEVICE_CODE = "WSCPCG100000001"
PRODUCT_KEY = "49KaPBUogOO7"
MQTT_USERNAME = "wesine"
MQTT_PASSWORD = "wesine"
MQTT_BROKER_HOST = "58.49.184.55"
MQTT_BROKER_PORT = 1883

running = True
ffmpeg_process = None
last_time = 0

if __name__ == '__main__':

    logging.basicConfig(filename='all.log', level=logging.DEBUG)
    # logging.basicConfig(level=logging.DEBUG)

    driver1 = 11
    driver2 = 15
    pilot1 = 12
    pilot2 = 13

    car = MyCar(driver1, driver2, pilot1, pilot2)
    mqtt_client = MyClient(MQTT_BROKER_HOST, MQTT_BROKER_PORT, DEVICE_CODE, MQTT_USERNAME, MQTT_PASSWORD)


    def on_message_callback(client, userdata, message):
        global running
        topic = message.topic
        payload = json.loads(message.payload.decode('utf-8'))

        if topic is not None and payload is not None:
            if topic.endswith('start'):
                data = payload.get('data')
                if data is not None:
                    ip = data.get('ip')
                    command = f'ffmpeg -f video4linux2 -framerate 30 -video_size 640x480 -input_format yuyv422 -i /dev/video0 -c:v h264_omx -pix_fmt yuv420p -g 10 -b:v 1000k -f mpegts udp://{ip}:5000'
                    logging.debug(f"执行开始命令:{command}")
                    global ffmpeg_process

                    ffmpeg_process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                                      stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
                    ack = {
                        "mid": str(uuid.uuid4()),
                        "rid": payload.get('mid'),
                        "ts": int(time.time() * 1000),
                        "sn": f"{DEVICE_CODE}",
                        "data": {"code": 0}
                    }
                    mqtt_client.publish(f"ws/sys/v1/{PRODUCT_KEY}/command_ack", json.dumps(ack))
                    logging.debug("执行开始命令完成")

            elif topic.endswith('stop'):
                # 终止 ffmpeg 进程
                cleanup()

                ack = {
                    "mid": str(uuid.uuid4()),
                    "rid": payload.get('mid'),
                    "ts": int(time.time() * 1000),
                    "sn": f"{DEVICE_CODE}",
                    "data": {"code": 0}
                }
                mqtt_client.publish(f"ws/sys/v1/{PRODUCT_KEY}/command_ack", json.dumps(ack))
                logging.debug("执行停止命令完成")

            elif topic.endswith('control'):
                data = payload.get('data')
                # if data is not None:
                #     cmd = data.get('cmd')
                #     logging.debug("收到命令:" + cmd)
                #     if cmd == "p":
                #         running = False
                #     elif cmd == "w":
                #         car.go_forward()
                #     elif cmd == "s":
                #         car.go_back()
                #     elif cmd == "a":
                #         car.to_left()
                #     elif cmd == "d":
                #         car.to_right()
                #     elif cmd == "n":
                #         car.stop()


    def on_my_disconnect(client, userdata, rc):
        global last_time
        last_time = 0
        mqtt_client.unsubscribe(f"ws/{DEVICE_CODE}/v1/{PRODUCT_KEY}/command/control")
        mqtt_client.unsubscribe(f"ws/{DEVICE_CODE}/v1/{PRODUCT_KEY}/command/start")
        mqtt_client.unsubscribe(f"ws/{DEVICE_CODE}/v1/{PRODUCT_KEY}/command/stop")


    def on_my_connect(client, userdata, flags, rc):
        mqtt_client.subscribe(f"ws/{DEVICE_CODE}/v1/{PRODUCT_KEY}/command/control", on_message_callback)
        mqtt_client.subscribe(f"ws/{DEVICE_CODE}/v1/{PRODUCT_KEY}/command/start", on_message_callback)
        mqtt_client.subscribe(f"ws/{DEVICE_CODE}/v1/{PRODUCT_KEY}/command/stop", on_message_callback)


    # 在 Python 进程退出时终止子进程
    def cleanup():
        global ffmpeg_process
        if ffmpeg_process is not None:
            ffmpeg_process.terminate()
            ffmpeg_process.wait()
            ffmpeg_process = None

            # 查找相关进程并杀死它们
            pids = subprocess.check_output(['pgrep', '-f', 'ffmpeg.*\/dev\/video0'])
            for pid in pids.split():
                # 先发送 SIGTERM 信号，等待 3 秒后再检查进程是否还存在
                subprocess.call(['kill', '-15', pid])
                time.sleep(3)
                try:
                    os.kill(int(pid), 0)
                except OSError:
                    pass
                else:
                    # 如果进程还存在，则使用 SIGKILL 信号强制终止
                    subprocess.call(['kill', '-9', pid])


    mqtt_client.on_disconnect = on_my_disconnect
    mqtt_client.on_connect = on_my_connect

    mqtt_client.connect()

    atexit.register(cleanup)

    while running:
        current_time = int(time.time() * 1000)
        # 五分钟来一次
        if mqtt_client.is_connect() and (current_time - last_time) > (1 * 60 * 1000):
            payload = {
                "mid": str(uuid.uuid4()),
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
