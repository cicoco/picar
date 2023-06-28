import os
import time

if __name__ == '__main__':
    result = os.system('ffmpeg -f video4linux2 -framerate 30 -video_size 640x480 '
                       '-input_format yuyv422 -i /dev/video0 -c:v h264_omx -pix_fmt yuv420p -g 10 '
                       '-b:v 1000k -f mpegts udp://192.168.2.5:5000')

    print(f'result{result}')
    while True:
        time.sleep(1)

