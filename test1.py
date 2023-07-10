import socket

if __name__ == '__main__':

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


    print(f"{get_inner_ip()}")

    # result = os.system('ffmpeg -f video4linux2 -framerate 30 -video_size 640x480 '
    #                    '-input_format yuyv422 -i /dev/video0 -c:v h264_omx -pix_fmt yuv420p -g 10 '
    #                    '-b:v 1000k -f mpegts udp://192.168.2.5:5000')
    #
    # print(f'result{result}')
    # while True:
    #     time.sleep(1)
