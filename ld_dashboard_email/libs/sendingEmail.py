import json, requests
from email.mime.application import MIMEApplication
import datetime
from email.mime.image import MIMEImage
from importlib.resources import path
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from email.mime.base import MIMEBase
from email.encoders import encode_base64
import argparse

THIS_DIR=os.path.dirname(os.path.abspath(__file__))


def parser():
	parse = argparse.ArgumentParser("generateChart")
	parse.add_argument("--output_dir", "-od",  help="Output Directory", default=f"{THIS_DIR}/../build", type=str)
	parse.add_argument("--templates_dir", "-td",  help="Templates Directory", default=f"{THIS_DIR}/../templates", type=str)
	parse.add_argument("--project", "-p",  help="Project Name", required=True, type=str)
	return parse

def get_receiver_lists(**kwargs):
  return requests.get(f'http://127.0.0.1:8000/get_receivers/{kwargs["project"]}').json().get('receivers_list')

def main(**kwargs):

  if not os.path.isdir( kwargs.get('output_dir') ):
    os.makedirs( kwargs.get('output_dir') )

  for _, _, files in os.walk( kwargs.get('output_dir') ):
    email_attach_pdf = [ each for each in files if each.endswith('.pdf') ]
    email_image = [ each for each in files if each.endswith('.jpeg') ]
  email_body = os.path.join( *[ kwargs.get('output_dir'), "body.html" ] )

  mail_from = ""
  mail_to = get_receiver_lists(**kwargs)
  now = datetime.datetime.now()
  nowDate = now.strftime('%Y.%m.%d')
  today_date = str(nowDate)
  mail_subject = f"{kwargs.get('project')} REGRESSION REPORT {today_date}"

  mimemsg = MIMEMultipart()
  mimemsg['From']=mail_from
  mimemsg['To']= ",".join(mail_to)
  mimemsg['Subject']=mail_subject

  for each in email_image:
    with open( f"{kwargs.get('output_dir')}/{each}", 'rb') as img_file:
      mime_img = MIMEImage(img_file.read())
      mime_img.add_header('Content-Disposition', 'attachment', filename=each)
      mime_img.add_header('X-Attachment-Id', '0')
      mime_img.add_header('Content-ID', '<0>')
      mimemsg.attach(mime_img)

  with open( email_body , 'r') as fp:
    temp_html = fp.read()
    mimemsg.attach(MIMEText(temp_html, 'html'))

  files = list()
  for each in email_attach_pdf:
    files.append(f"{kwargs.get('output_dir')}/{each}")

  for f in files:
    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(f,"rb").read())
    encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
    mimemsg.attach(part)

  connection = smtplib.SMTP(host='smtp.office365.com', port=587)
  connection.starttls()
  connection.login('id','pw')
  connection.send_message(mimemsg)
  connection.quit()

if __name__ == "__main__":
  args = parser().parse_args()
  main(**vars(args))