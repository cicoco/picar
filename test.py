import time

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

driver1 = 11
driver2 = 12
driverPwm = 13

# driver1 = 15
# driver2 = 16
# driverPwm = 18

pwmDriver = None
try:
    # 设置gpio口为输出
    GPIO.setup(driver1, GPIO.OUT)
    GPIO.setup(driver2, GPIO.OUT)
    GPIO.setup(driverPwm, GPIO.OUT)

    # 设置PWM对象
    pwmDriver = GPIO.PWM(driverPwm, 100)

    # 启动

    GPIO.output(driver1, True)
    GPIO.output(driver2, False)

    # Position -7 Duty Cycle: 100%, analogWrite(): 255, C1: +, C2: - (90 degrees counter-clockwise)
    # Position -6 Duty Cycle: 88.2%, analogWrite(): 225, C1: +, C2: -
    # Position -5 Duty Cycle: 76.0%, analogWrite(): 194, C1: +, C2: -
    # Position -4 Duty Cycle: 63.5%, analogWrite(): 162, C1: +, C2: -
    # Position -3 Duty Cycle: 50.1%, analogWrite(): 128, C1: +, C2: -
    # Position -2 Duty Cycle: 38.0%, analogWrite(): 97, C1: +, C2: -
    # Position -1 Duty Cycle: 25.8%, analogWrite(): 66, C1: +, C2: -
    # Position 0 Duty Cycle: 0%, analogWrite(): 0 (center)
    # Position 1 Duty Cycle: 25.8%, analogWrite(): 66, C1: -, C2: +
    # Position 2 Duty Cycle: 38.0%, analogWrite(): 97, C1: -, C2: +
    # Position 3 Duty Cycle: 50.1%, analogWrite(): 128, C1: -, C2: +
    # Position 4 Duty Cycle: 63.5%, analogWrite(): 162, C1: -, C2: +
    # Position 5 Duty Cycle: 76.0%, analogWrite(): 194, C1: -, C2: +
    # Position 6 Duty Cycle: 88.2%, analogWrite(): 225, C1: -, C2: +
    # Position 7 Duty Cycle: 100%, analogWrite(): 255, C1: -, C2: + (90 degrees clockwise)

    pwmDriver.start(100)

    time.sleep(1)

    # GPIO.output(driver1, True)
    # GPIO.output(driver2, False)

    # pwmDriver.ChangeDutyCycle(100)

    # time.sleep(1)

except Exception as e:
    print(e)
finally:
    if pwmDriver is not None:
        pwmDriver.stop()
    GPIO.cleanup()
