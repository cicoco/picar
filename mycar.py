# -*- coding: utf-8 -*-
import time

import RPi.GPIO as GPIO


class MyCar(object):

    def __init__(self, driver1, driver2, pilot1, pilot2):
        self.driver1 = driver1
        self.driver2 = driver2
        self.pilot1 = pilot1
        self.pilot2 = pilot2
        self.state = None

        GPIO.setmode(GPIO.BOARD)

        # 设置gpio口为输出
        GPIO.setup(self.driver1, GPIO.OUT)
        GPIO.setup(self.driver2, GPIO.OUT)
        GPIO.setup(self.pilot1, GPIO.OUT)
        GPIO.setup(self.pilot2, GPIO.OUT)

        # 设置PWM对象
        self.pwmDriver1 = GPIO.PWM(self.driver1, 100)
        self.pwmDriver2 = GPIO.PWM(self.driver2, 100)
        self.pwmPilot1 = GPIO.PWM(self.pilot1, 100)
        self.pwmPilot2 = GPIO.PWM(self.pilot2, 100)

        # 启动
        self.pwmDriver1.start(0)
        self.pwmDriver2.start(0)
        self.pwmPilot1.start(0)
        self.pwmPilot2.start(0)

    # 前进
    def go_forward(self):
        if self.state == "Forward":
            return

        self.pwmDriver1.ChangeDutyCycle(50)
        self.pwmDriver2.ChangeDutyCycle(0)
        self.state = "Forward"

    # 后退
    def go_back(self):
        if self.state == "Back":
            return
        self.pwmDriver1.ChangeDutyCycle(0)
        self.pwmDriver2.ChangeDutyCycle(50)
        self.state = "Back"

    # 左转
    def to_left(self):
        if self.state == "ToLeft":
            return
        self.state = "ToLeft"
        self.pwmPilot1.ChangeDutyCycle(0)
        self.pwmPilot2.ChangeDutyCycle(20)
        time.sleep(1)
        self.state = "DoneLeft"

    # 右转
    def to_right(self):
        if self.state == "ToRight":
            return
        self.state = "ToRight"
        self.pwmPilot1.ChangeDutyCycle(20)
        self.pwmPilot2.ChangeDutyCycle(0)
        time.sleep(1)
        self.state = "DoneRight"

    def stop(self):
        if self.state == "Stop":
            return
        self.pwmDriver1.ChangeDutyCycle(0)
        self.pwmDriver2.ChangeDutyCycle(0)
        self.pwmPilot1.ChangeDutyCycle(0)
        self.pwmPilot2.ChangeDutyCycle(0)

        self.state = "Stop"

    def __del__(self):
        self.pwmDriver1.stop()
        self.pwmDriver2.stop()
        self.pwmPilot1.stop()
        self.pwmPilot2.stop()
        GPIO.cleanup()
