from scrape import scrape
from config import email_list, gmail, gmail_pass
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
import smtplib, ssl
import sys
import schedule
import time

print("Running...")
def send_email():
  all_budgets,transactions = scrape()

  # Defining subjectline and sender email
  msg = MIMEMultipart()
  msg['Subject'] = 'Daily Budget Update'
  msg['From'] = gmail
  # Creating tables from Pandas DFs
  html = """\
  <html>
    <head></head>
    <body>
      {0}
    </body>
  </html>
  """.format(all_budgets.to_html())

  html2 = """\
  <html>
    <head></head>
    <body>
      {0}
    </body>
  </html>
  """.format(transactions.to_html())

  # Insert HTML tables into the email
  part1 = MIMEText(html, 'html')
  part2 = MIMEText(html2, 'html')
  msg.attach(part1)
  msg.attach(part2)

  # Send Email
  context = ssl.create_default_context()
  with smtplib.SMTP_SSL('smtp.gmail.com',port=465, context=context) as server:
      server.login(gmail,gmail_pass)
      server.sendmail(gmail, email_list, msg.as_string())
      print('Message Sent') 

schedule.every().day.at("01:30").do(send_email)

while True:
  schedule.run_pending()
  time.sleep(1)