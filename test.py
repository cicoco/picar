import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)


driver1 = 11
driver2 = 12
driverPwm = 13

pwmDriver = None
try:
    # 设置gpio口为输出
    GPIO.setup(driver1, GPIO.OUT)
    GPIO.setup(driver2, GPIO.OUT)
    GPIO.setup(driverPwm, GPIO.OUT)


    # 设置PWM对象
    pwmDriver = GPIO.PWM(driverPwm, 100)

    # 启动
    pwmDriver.start(0)

    GPIO.output(driver1, True)
    GPIO.output(driver2, False)

    pwmDriver.ChangeDutyCycle(50)


    time.sleep(2)

except Exception as e:
    print(e)
finally:
    if pwmDriver is not None:
        pwmDriver.stop()
    GPIO.cleanup()