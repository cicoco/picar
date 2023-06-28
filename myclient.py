# -*- coding: utf-8 -*-
import logging

import paho.mqtt.client as mqtt


class MyClient(object):

    def __init__(self, broker_host, broker_port, client_id, username, password, keep_alive=60,
                 on_connect=None, on_disconnect=None):
        self.client = mqtt.Client(client_id=client_id)
        self.client.username_pw_set(username, password)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.keep_alive = keep_alive
        self.connected = False

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            logging.info("Connected to MQTT broker success")
            self.on_connect(client, userdata, flags, rc)
        else:
            logging.info("Connected to MQTT broker failed")

    def on_disconnect(self, client, userdata, flags, rc):
        logging.info("inner disconnect called")

    def on_connect(self, client, userdata, flags, rc):
        logging.info("inner connect called")

        # 0：表示正常断开连接。
        # 1：表示与服务器的连接丢失。
        # 2：表示客户端主动断开连接。
        # 3：表示协议错误。
        # 4：表示服务器不可用。
        # 5：表示无法连接到服务器。

    def _on_disconnect(self, client, userdata, rc):
        if rc != 0 and rc != 2:
            logging.info("Connect Lost")
            self.on_disconnect(client, userdata, rc)
        else:
            logging.info("Disconnect Success")

            self.connected = False

    def connect(self):
        self.client.connect(self.broker_host, self.broker_port, self.keep_alive)
        self.client.loop_start()
        logging.info("完成连接")

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False

    def subscribe(self, topic, on_message_callback):
        if self.connected:
            self.client.subscribe(topic)
            self.client.message_callback_add(topic, on_message_callback)
            logging.info("订阅topic:" + topic)
        else:
            logging.info("在订阅前请先链接broker")

    def is_connect(self):
        return self.connected

    def unsubscribe(self, topic):
        if self.connected:
            self.client.unsubscribe(topic)
            self.client.message_callback_remove(topic)
            logging.info("取消订阅:" + topic)
        else:
            logging.info("在取消前请先链接broker")

    def publish(self, topic, payload, qos=0, retain=False):
        if self.connected:
            logging.debug("发布topic:" + topic)
            self.client.publish(topic, payload, qos=qos, retain=retain)
        else:
            logging.debug("在发布前请先链接broker")
