# # -*- coding: utf-8 -*-
# import RPi.GPIO as GPIO
#
#
# class MyCar(object):
#
#     def __init__(self, frontLeft, frontRight, backLeft, backRight):
#         self.frontLeft = frontLeft
#         self.frontRight = frontRight
#         self.backLeft = backLeft
#         self.backRight = backRight
#         self.state = None
#
#         GPIO.setmode(GPIO.BOARD)
#
#         # 设置gpio口为输出
#         GPIO.setup(self.frontLeft, GPIO.OUT)
#         GPIO.setup(self.frontRight, GPIO.OUT)
#         GPIO.setup(self.backLeft, GPIO.OUT)
#         GPIO.setup(self.backRight, GPIO.OUT)
#
#     # 前进
#     def go_forward(self):
#         if self.state == "Forward":
#             return
#         GPIO.output(self.frontRight, GPIO.HIGH)
#         GPIO.output(self.backRight, GPIO.LOW)
#         GPIO.output(self.frontLeft, GPIO.LOW)
#         GPIO.output(self.backLeft, GPIO.HIGH)
#
#         self.state = "Forward"
#
#     # 后退
#     def go_back(self):
#         if self.state == "Back":
#             return
#         GPIO.output(self.frontRight, GPIO.LOW)
#         GPIO.output(self.backRight, GPIO.HIGH)
#         GPIO.output(self.frontLeft, GPIO.HIGH)
#         GPIO.output(self.backLeft, GPIO.LOW)
#         self.state = "Back"
#
#     # 左转
#     def to_left(self):
#         if self.state == "ToLeft":
#             return
#         GPIO.output(self.frontRight, GPIO.HIGH)
#         GPIO.output(self.backRight, GPIO.LOW)
#         GPIO.output(self.frontLeft, False)
#         GPIO.output(self.backLeft, False)
#         self.state = "ToLeft"
#
#     # 右转
#     def to_right(self):
#         if self.state == "ToRight":
#             return
#         GPIO.output(self.frontRight, False)
#         GPIO.output(self.backRight, False)
#         GPIO.output(self.frontLeft, GPIO.LOW)
#         GPIO.output(self.backLeft, GPIO.HIGH)
#         self.state = "ToRight"
#
#     def stop(self):
#         if self.state == "Stop":
#             return
#         GPIO.output(self.frontRight, False)
#         GPIO.output(self.backRight, False)
#         GPIO.output(self.frontLeft, False)
#         GPIO.output(self.backLeft, False)
#         self.state = "Stop"
#
#
# def __del__(self):
#     GPIO.cleanup()
