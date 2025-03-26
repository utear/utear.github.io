import subprocess
import smtplib
from email.mime.text import MIMEText
import schedule
import time
import platform
import re
import sys
import io

# 处理 Windows 命令行编码问题
if platform.system() == "Windows":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 邮件配置信息
email_config = {
    "sender_email": "nutrat@163.com",
    "receiver_email": "largeclub@163.com",
    "password": "RITFEHXIRRQYUSZT",
    "server": "smtp.163.com",
    "port": 25,
    "subject": "IP 地址通知"
}

# 获取旧的 IP 地址
def get_old_ip():
    try:
        with open('ip_address.txt', 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return None

# 获取 IP 地址并写入文件
def get_and_write_ip_to_file():
    ip_info = get_ip_address()
    old_ip = get_old_ip()
    if ip_info == old_ip:
        print("IP 地址未发生变化，不更新文件和发送邮件。")
        return False
    try:
        with open('ip_address.txt', 'w') as file:
            file.write(ip_info)
        print("IP 地址信息已成功写入 ip_address.txt 文件。")
        return True
    except Exception as e:
        print(f"写入文件时出现错误: {e}")
        return False

def get_ip_address():
    system = platform.system()
    try:
        if system == "Linux":
            result = subprocess.run(['ip', 'addr'], capture_output=True, text=True)
        elif system == "Windows":
            result = subprocess.run(['ipconfig'], capture_output=True, text=True)
        elif system == "Darwin":
            result = subprocess.run(['ifconfig'], capture_output=True, text=True)
        else:
            print("不支持的操作系统平台")
            return None
        output = result.stdout
        # 正则表达式匹配 IPv6 地址
        ipv6_pattern = re.compile(r'(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))')
        ipv6_addresses = ipv6_pattern.findall(output)
        # 提取完整的 IPv6 地址，并只保留以 2409 开头的地址
        ipv6_addrs = [addr[0] for addr in ipv6_addresses if addr[0] and '%' not in addr[0] and addr[0].startswith('2409')]
        return '\n'.join(ipv6_addrs)
    except Exception as e:
        print(f"执行命令时出现错误: {e}")
        return None

# 发送邮件函数
def send_email(ip_address):
    try:
        body = f"当前 IP 地址是: {ip_address}"
        print(f"ip 地址: {ip_address}")
        # 创建邮件对象
        msg = MIMEText(body)
        msg['Subject'] = email_config["subject"]
        msg['From'] = email_config["sender_email"]
        msg['To'] = email_config["receiver_email"]

        # 发送邮件
        with smtplib.SMTP(email_config["server"], email_config["port"]) as server:
            server.starttls()
            server.login(email_config["sender_email"], email_config["password"])
            server.sendmail(email_config["sender_email"], email_config["receiver_email"], msg.as_string())
        print("邮件发送成功")
    except FileNotFoundError:
        print("文件未找到")
    except smtplib.SMTPException as e:
        print(f"邮件发送失败: {e}")

# 读取文件内容并发送邮件
def read_file_and_send_email():
    try:
        # 读取文件内容
        with open('ip_address.txt', 'r') as file:
            ip_address = file.read().strip()
        send_email(ip_address)
    except FileNotFoundError:
        print("文件未找到")

def job():
    if get_and_write_ip_to_file():
        read_file_and_send_email()

# 设置定时任务，每小时执行一次（如果需要定时功能，取消下面这行注释并确保已安装 schedule 模块）
# schedule.every().day.at("22:30").do(job)
schedule.every().minute.do(job)

if __name__ == "__main__":
    job()
    while True:
        schedule.run_pending()
        time.sleep(1)
    