import smtplib, imaplib, email

imap_host = "imap.mail.ru"
smtp_host = "imap.mail.ru"
smtp_port = 587
user = "a_lex90_90@mail.ru"
passwd = "XMVhnjPLKiXZ3weKgACR"
msgid = 7
from_addr = "a_lex90_90@mail.ru"
to_addr = "kardash.by@gmail.com"

# open IMAP connection and fetch message with id msgid
# store message data in email_data
mail = imaplib.IMAP4_SSL(imap_host)
mail.login(user, passwd)
mail.list()
mail.select('inbox')
result, data = mail.uid('search', None, "ALL")  # (ALL/UNSEEN)
i = len(data[0].split())  # emails count
for x in range(i):
    latest_email_uid = data[0].split()[x]
    result, email_data = mail.uid('fetch', latest_email_uid, '(RFC822)')
    raw_email_string = email_data[0][1].decode('utf-8')
    message = email.message_from_string(raw_email_string)
    # create a Message instance from the email data

    # replace headers (could do other processing here)
    message.replace_header("From", from_addr)
    message.replace_header("To", to_addr)

    # open authenticated SMTP connection and send message with
    # specified envelope from and to addresses
    smtp = smtplib.SMTP(smtp_host, smtp_port)
    smtp.starttls()
    smtp.login(user, passwd)
    smtp.sendmail(from_addr, to_addr, message.as_string())