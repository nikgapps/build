import os
import smtplib


class NikMail:

    def __init__(self, subject, body):
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            gmail_user = "NikGapps@gmail.com"
            gmail_password = '' if os.environ.get('GMAIL_PASSWORD') is None else os.environ.get('GMAIL_PASSWORD')
            to = ""
            if os.environ.get('TO_MAILS') is not None:
                to = str(os.environ.get('TO_MAILS')).split(",")
            email_text = f"""From: {gmail_user}\nTo: {", ".join(to)}\nSubject: {subject}\n{body}"""
            print(email_text)
            server.login(gmail_user, gmail_password)
            server.sendmail(from_addr=gmail_user, to_addrs=to, msg=email_text)
            server.close()
            print("Email Sent!")
        except:
            print('Something went wrong...')
