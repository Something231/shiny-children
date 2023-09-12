import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

def sendemail(reciever, subject, largebody, body):
  message = MIMEMultipart()
  message["To"] = reciever
  message["From"] = ''
  message["Subject"] = subject
  
  title = 'Nothing goes here'
  html = f"""\
<html>
  <head></head>
  <body>
    <h3>{largebody}</h3>
    <p>{body}</p>
  </body>
</html>"""
  messageText = MIMEText(html,'html')
  message.attach(messageText)
  
  email = ''
  password = os.getenv()
  
  server = smtplib.SMTP('smtp.gmail.com:587')
  server.ehlo('Gmail')
  server.starttls()
  server.login(email,password)
  fromaddr = 'sniofnjnfassfaionafsinasfonasfionsaf'
  toaddrs  = reciever
  server.sendmail(fromaddr,toaddrs,message.as_string())
  
  server.quit()
  print("email sent")
