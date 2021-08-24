import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()


def send_mail(message):
    content = MIMEMultipart()  # 建立MIMEMultipart物件
    content["subject"] = f"Buy {message} now"  # 郵件標題
    content["from"] = os.getenv("gmail")  # 寄件者
    content["to"] = os.getenv("gmail")  # 收件者
    content.attach(MIMEText("You should buy"))  # 郵件內容
    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login(os.getenv("gmail"), os.getenv("gmail_password"))  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件

        except Exception as e:
            print("Error message: ", e)
