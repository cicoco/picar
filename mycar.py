# -*- coding: utf-8 -*-
import logging
import threading
import time

import RPi.GPIO as GPIO


class MyCar(object):

    def __init__(self, mqtt_client, driver1, driver2, driverPwm, pilot1, pilot2, pilotPwm):
        self.driver1 = driver1
        self.driver2 = driver2
        self.driverPwm = driverPwm
        self.pilot1 = pilot1
        self.pilot2 = pilot2
        self.pilotPwm = pilotPwm
        self.driverState = None
        self.pilotState = None
        self.last_run_duty = 0

        self.mqtt_client = mqtt_client

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
    def go_forward(self, max):
        if max <= 10:
            return
        self.driverState = "Forward"

        GPIO.output(self.driver1, False)
        GPIO.output(self.driver2, True)

        thread = threading.Thread(target=self.car_run, args=("Forward", max))
        thread.start()

    def car_run(self, direction, max):
        self.last_run_duty = 10
        while self.driverState == f"{direction}":
            if self.last_run_duty < max:
                self.last_run_duty += 1
            elif self.last_run_duty > max:
                self.last_run_duty -= 1

            self.driver.ChangeDutyCycle(self.last_run_duty)
            time.sleep(0.1)
        logging.debug(f"停止{direction}")

    # # 后退
    def go_back(self, max):
        if max <= 10:
            return
        self.driverState = "Back"
        GPIO.output(self.driver1, True)
        GPIO.output(self.driver2, False)

        thread = threading.Thread(target=self.car_run, args=("Back", max))
        thread.start()

    # 左转
    def to_left(self):
        if self.pilotState == "ToLeft":
            return
        self.pilotState = "ToLeft"
        GPIO.output(self.pilot1, True)
        GPIO.output(self.pilot2, False)
        self.pilot.ChangeDutyCycle(100)

    # 右转
    def to_right(self):
        if self.pilotState == "ToRight":
            return
        self.pilotState = "ToRight"
        GPIO.output(self.pilot1, False)
        GPIO.output(self.pilot2, True)
        self.pilot.ChangeDutyCycle(100)

    def stop_turn(self):
        if self.pilotState == 'stopTurn':
            return
        self.pilotState = 'stopTurn'
        self.pilot.ChangeDutyCycle(0)

    def stop_run(self):
        if self.driverState == "StopRun":
            return
        self.driverState = "StopRun"
        self.last_run_duty = 0
        self.driver.ChangeDutyCycle(self.last_run_duty)
        logging.debug("刹车")

    def __del__(self):
        self.driver.stop()
        self.pilot.stop()
        GPIO.cleanup()
