from scrape import scrape
from config import email_list
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
import smtplib
import sys

all_budgets,transactions = scrape()

recipients = [email_list[0]] 
emaillist = [elem.strip().split(',') for elem in recipients]
msg = MIMEMultipart()
msg['Subject'] = "Daily Budget Update"
msg['From'] = email_list[1]

html = """\
<html>
  <head></head>
  <body>
    {0}
  </body>
</html>
""".format(all_budgets.to_html())

part1 = MIMEText(html, 'html')
msg.attach(part1)

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.sendmail(msg['From'], emaillist , msg.as_string())
server.quit()