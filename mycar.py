# -*- coding: utf-8 -*-

import time

import RPi.GPIO as GPIO


class MyCar(object):

    def __init__(self, driver1, driver2, driverPwm, pilot1, pilot2, pilotPwm):
        self.driver1 = driver1
        self.driver2 = driver2
        self.driverPwm = driverPwm
        self.pilot1 = pilot1
        self.pilot2 = pilot2
        self.pilotPwm = pilotPwm
        self.state = None

        GPIO.setmode(GPIO.BOARD)

        # 设置gpio口为输出
        GPIO.setup(self.driver1, GPIO.OUT)
        GPIO.setup(self.driver2, GPIO.OUT)
        GPIO.setup(self.driverPwm, GPIO.OUT)
        GPIO.setup(self.pilot1, GPIO.OUT)
        GPIO.setup(self.pilot2, GPIO.OUT)
        GPIO.setup(self.pilotPwm, GPIO.OUT)

        # 设置PWM对象
        self.driver = GPIO.PWM(driverPwm, 100)
        self.pilot = GPIO.PWM(pilotPwm, 100)

        # 启动
        self.driver.start(0)
        self.pilot.start(0)

    # 前进
    def go_forward(self):
        if self.state == "Forward":
            return
        self.state = "Forward"

        GPIO.output(self.driver1, True)
        GPIO.output(self.driver2, False)

        duty_cycle = 0
        while self.state == "Forward":
            duty_cycle += 10  # 每次增加10个占空比
            if duty_cycle > 100:  # 占空比最大值为100
                duty_cycle = 100
            self.driver.ChangeDutyCycle(duty_cycle)
            time.sleep(0.1)  # 等待一段时间，以便观察PWM信号效果

    # 后退
    def go_back(self):
        if self.state == "Back":
            return
        self.state = "Back"
        GPIO.output(self.driver1, False)
        GPIO.output(self.driver2, True)

        duty_cycle = 0
        while self.state == "Forward":
            duty_cycle += 10  # 每次增加10个占空比
            if duty_cycle > 100:  # 占空比最大值为100
                duty_cycle = 100
            self.driver.ChangeDutyCycle(duty_cycle)
            time.sleep(0.1)  # 等待一段时间，以便观察PWM信号效果

    # 左转
    def to_left(self, angle):
        if self.state == "ToLeft":
            return
        self.state = "ToLeft"

    # 右转
    def to_right(self, angle):
        if self.state == "ToRight":
            return
        self.state = "ToRight"

    def stop(self):
        if self.state == "Stop":
            return

        self.driver.ChangeDutyCycle(0)
        self.pilot.ChangeDutyCycle(0)
        self.state = "Stop"

    def __del__(self):
        self.driver.stop()
        self.pilot.stop()
        GPIO.cleanup()
