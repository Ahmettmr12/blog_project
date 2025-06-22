import smtplib
import random
from email.mime.text import MIMEText

def generate_code():
    return str(random.randint(100000, 999999))

def send_email_code(receiver_email, code):
    sender_email = "krakix12@gmail.com"           
    sender_password = "yyyh gsbs ecgv qyye"        

    msg = MIMEText(f"Giriş kodunuz: {code}")
    msg['Subject'] = '2FA Giriş Kodu'
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print("Kod başarıyla gönderildi.")
    except Exception as e:
        print("Kod gönderilemedi:", e)
