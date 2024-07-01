

import smtplib  # 导入PyEmail
from email.mime.text import MIMEText
import time


# 邮件构建

def send(stock_code, margin_price):
    subject = f"股市Elf-stock_code={0},margin_price={1}".format(stock_code, margin_price)  # 邮件标题
    sender = "piguanghua365@163.com"  # 发送方
    content = "加仓"
    recver = "piguanghua365@163.com"  # 接收方
    password = "TFDXQZXRZENQVXRZ" #邮箱密码
    message = MIMEText(content, "plain", "utf-8")
    # content 发送内容     "plain"文本格式   utf-8 编码格式

    message['Subject'] = subject  # 邮件标题
    message['To'] = recver  # 收件人
    message['From'] = sender  # 发件人

    smtp = smtplib.SMTP_SSL("smtp.163.com", 994)  # 实例化smtp服务器
    smtp.login(sender, password)  # 发件人登录
    smtp.sendmail(sender, [recver], message.as_string())  # as_string 对 message 的消息进行了封装
    smtp.close()
    print("发送邮件成功！！")

if __name__ == '__main__':
    send(1)