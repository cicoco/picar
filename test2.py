import subprocess
if __name__ == '__main__':
    # 执行 ifconfig 命令，获取 WLAN0 网络接口的信息
    output = subprocess.check_output(['ifconfig', 'wlan0'])

    # 解析输出结果，获取 WLAN0 接口的IP地址
    ip_address = output.split(b'\n')[1].split()[1].decode()

    print(ip_address)
