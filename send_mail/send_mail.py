# import necessary packages

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

# create message object instance
msg = MIMEMultipart()


message = "Tes de prueba"

# setup the parameters of the message
password = "luyntp@gcx2Zkii"
msg['From'] = "info@sanmartindelosandesbureau.com.ar"
msg['To'] = "iturrima@gmail.com"
msg['Subject'] = "Hola asunto"

# add in the message body
msg.attach(MIMEText(message, 'plain'))

#create server
# server = smtplib.SMTP('smtp.gmail.com: 587')
server = smtplib.SMTP_SSL('mail.sanmartindelosandesbureau.com.ar', 465)

# server.starttls()

# Login Credentials for sending the mail
server.login(msg['From'], password)


# send the message via the server.
server.sendmail(msg['From'], msg['To'], msg.as_string())

server.quit()

print "successfully sent email to %s:" % (msg['To'])
