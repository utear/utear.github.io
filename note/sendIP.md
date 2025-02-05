# 发送邮件  ip
```python
import subprocess
import smtplib
from email.mime.text import MIMEText
import schedule
import time

# 获取IP地址并写入文件
def get_and_write_ip_to_file():
    try:
        # 执行Linux命令获取IP地址
        # result = subprocess.run(['ip', 'addr'], capture_output=True, text=True)
        # window
        result = subprocess.run(['ipconfig'], capture_output=True, text=True)
        ip_address = result.stdout.strip()

        # 将IP地址写入文件
        with open('ip_address.txt', 'r+') as file:
            old_ip_address = file.read().strip()
            file.write(ip_address)
            if (old_ip_address == ip_address):
                return True
    except subprocess.CalledProcessError as e:
        print(f"执行命令出错: {e}")
    return False

# 读取文件内容并发送邮件
def read_file_and_send_email():
    try:
        # 读取文件内容
        with open('ip_address.txt', 'r') as file:
            ip_address = file.read().strip()

        # 邮件配置
        sender_email = "nutrat@163.com"
        receiver_email = "largeclub@163.com"
        password = "RITFEHXIRRQYUSZT"
        server="smtp.163.com"
        port=25
        subject = "IP地址通知"
        body = f"当前IP地址是: {ip_address}"

        print(f"ip地址: {ip_address}")
        # 创建邮件对象
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = receiver_email

        # 发送邮件
        with smtplib.SMTP(server, port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("邮件发送成功")
    except FileNotFoundError:
        print("文件未找到")
    except smtplib.SMTPException as e:
        print(f"邮件发送失败: {e}")


def job():
    hasChanged = get_and_write_ip_to_file()
    if (hasChanged):
        read_file_and_send_email()


# 设置定时任务，每小时执行一次（如果需要定时功能，取消下面这行注释并确保已安装schedule模块）
# schedule.every().day.at("06:30").do(job)
schedule.every().minute.do(job)

if __name__ == "__main__":
    job()
    # 如果需要代码持续运行等待定时任务触发（配合上面的定时任务代码使用），取消下面的while循环注释
    while True:
        schedule.run_pending()
        time.sleep(1)
```
