# -*- coding: utf-8 -*-
import atexit
import json
import logging
import os
import socket
import subprocess
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
ffmpeg_process = None
last_ping_time = 0

if __name__ == '__main__':

    logging.basicConfig(filename='all.log', level=logging.DEBUG)
    # logging.basicConfig(level=logging.DEBUG)

    driver1 = 15
    driver2 = 16
    driverPwm = 18

    pilot1 = 11
    pilot2 = 12
    pilotPwm = 13

    mqtt_client = MyClient(MQTT_BROKER_HOST, MQTT_BROKER_PORT, DEVICE_CODE, MQTT_USERNAME, MQTT_PASSWORD)
    car = MyCar(mqtt_client, driver1, driver2, driverPwm, pilot1, pilot2, pilotPwm)


    def on_message_callback(client, userdata, message):
        global running
        topic = message.topic
        payload = json.loads(message.payload.decode('utf-8'))

        if topic is not None and payload is not None:
            if topic.endswith('/start'):
                data = payload.get('data')
                if data is not None:
                    ip = data.get('ip')
                    command = f'ffmpeg -f video4linux2 -framerate 30 -video_size 640x480 -input_format yuyv422 -i /dev/video0 -c:v h264_omx -pix_fmt yuv420p -g 10 -b:v 1000k -f mpegts udp://{ip}:5000'
                    logging.debug(f"执行开始命令:{command}")
                    global ffmpeg_process

                    if ffmpeg_process is not None:
                        ack = {
                            "mid": str(uuid.uuid4()),
                            "rid": payload.get('mid'),
                            "ts": int(time.time() * 1000),
                            "sn": f"{DEVICE_CODE}",
                            "data": {"code": 1}
                        }
                        mqtt_client.publish(f"ws/sys/v1/{PRODUCT_KEY}/command_ack", json.dumps(ack))
                        logging.debug("执行开始命令失败")
                        return

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

            elif topic.endswith('/stop'):
                # 终止 ffmpeg 进程
                kill_ffmpeg_process()

                ack = {
                    "mid": str(uuid.uuid4()),
                    "rid": payload.get('mid'),
                    "ts": int(time.time() * 1000),
                    "sn": f"{DEVICE_CODE}",
                    "data": {"code": 0}
                }
                mqtt_client.publish(f"ws/sys/v1/{PRODUCT_KEY}/command_ack", json.dumps(ack))
                logging.debug("执行停止命令完成")

            elif topic.endswith('/w'):
                data = payload.get('data')
                max = 100
                if data is not None:
                    max = data.get("a")
                car.go_forward(max)
            elif topic.endswith('/s'):
                max = 5
                data = payload.get('data')
                if data is not None:
                    max = data.get("a")
                car.go_back(max)
            elif topic.endswith('/n'):
                car.stop_run()
            elif topic.endswith('/a'):
                car.to_left()
            elif topic.endswith('/d'):
                car.to_right()
            elif topic.endswith('/i'):
                car.stop_turn()


    def on_my_disconnect(client, userdata, rc):
        global last_ping_time
        last_ping_time = 0
        mqtt_client.unsubscribe(f"ws/{DEVICE_CODE}/v1/{PRODUCT_KEY}/command/start")
        mqtt_client.unsubscribe(f"ws/{DEVICE_CODE}/v1/{PRODUCT_KEY}/command/stop")
        mqtt_client.unsubscribe(f"ws/{DEVICE_CODE}/v1/{PRODUCT_KEY}/command/w")
        mqtt_client.unsubscribe(f"ws/{DEVICE_CODE}/v1/{PRODUCT_KEY}/command/s")
        mqtt_client.unsubscribe(f"ws/{DEVICE_CODE}/v1/{PRODUCT_KEY}/command/a")
        mqtt_client.unsubscribe(f"ws/{DEVICE_CODE}/v1/{PRODUCT_KEY}/command/d")
        mqtt_client.unsubscribe(f"ws/{DEVICE_CODE}/v1/{PRODUCT_KEY}/command/n")
        mqtt_client.unsubscribe(f"ws/{DEVICE_CODE}/v1/{PRODUCT_KEY}/command/i")


    def on_my_connect(client, userdata, flags, rc):
        mqtt_client.subscribe(f"ws/{DEVICE_CODE}/v1/{PRODUCT_KEY}/command/start", on_message_callback)
        mqtt_client.subscribe(f"ws/{DEVICE_CODE}/v1/{PRODUCT_KEY}/command/stop", on_message_callback)
        mqtt_client.subscribe(f"ws/{DEVICE_CODE}/v1/{PRODUCT_KEY}/command/w", on_message_callback)
        mqtt_client.subscribe(f"ws/{DEVICE_CODE}/v1/{PRODUCT_KEY}/command/s", on_message_callback)
        mqtt_client.subscribe(f"ws/{DEVICE_CODE}/v1/{PRODUCT_KEY}/command/a", on_message_callback)
        mqtt_client.subscribe(f"ws/{DEVICE_CODE}/v1/{PRODUCT_KEY}/command/d", on_message_callback)
        mqtt_client.subscribe(f"ws/{DEVICE_CODE}/v1/{PRODUCT_KEY}/command/n", on_message_callback)
        mqtt_client.subscribe(f"ws/{DEVICE_CODE}/v1/{PRODUCT_KEY}/command/i", on_message_callback)


    def kill_ffmpeg_process():
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


    # 在 Python 进程退出时终止子进程
    def cleanup():
        kill_ffmpeg_process()


    def get_inner_ip():
        # 获取主机名
        hostname = socket.gethostname()

        # 获取IP地址列表
        ip_list = socket.getaddrinfo(hostname, None)
        ip_address = None

        # 获取内网IP地址
        for item in ip_list:
            if ':' not in item[4][0] and item[4][0].startswith('192.168.'):
                ip_address = item[4][0]
                break
        return ip_address


    mqtt_client.on_disconnect = on_my_disconnect
    mqtt_client.on_connect = on_my_connect

    mqtt_client.connect()

    atexit.register(cleanup)

    sendIP = True

    while running:
        current_time = int(time.time() * 1000)
        if mqtt_client.is_connect():
            if sendIP:
                ip_address = {
                    "mid": str(uuid.uuid4()),
                    "ts": current_time,
                    "sn": f"{DEVICE_CODE}",
                    "data": {"inner_ip": f"{get_inner_ip()}"}
                }
                mqtt_client.publish(f"ws/sys/v1/{PRODUCT_KEY}/properties", json.dumps(ip_address))
                sendIP = False

            if (current_time - last_ping_time) > (1 * 60 * 1000):
                ping = {
                    "mid": str(uuid.uuid4()),
                    "ts": current_time,
                    "sn": f"{DEVICE_CODE}",
                    "data": {"online": 1}
                }
                mqtt_client.publish(f"ws/sys/v1/{PRODUCT_KEY}/status", json.dumps(ping))
                last_ping_time = current_time

        time.sleep(1)

    mqtt_client.disconnect()
    del car
    logging.info("结束小车活动")
