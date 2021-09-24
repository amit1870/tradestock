import sys
import os
import base64
import argparse
import mimetypes
sys.path.append('/home/ec2-user/virenv/pcv')

from time import sleep
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from requests.exceptions import HTTPError
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from email_config import EMAIL, API

HOUR = 3600

EMAIL_SCHEDULE = {
    'H': HOUR,
    'D': 24 * HOUR,
    'Q': 24 * 15 * HOUR,
    'M': 24 * 15 * 30 * HOUR
}

def create_plain_html_message(sender, to, subject, message_text, html=False):
    """Create a message for an email.

    Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

    Returns:
    An object containing a base64url encoded email object.
    """
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    if not html:
        msg.attach(MIMEText(message_text, 'plain'))
    else:
        msg.attach(MIMEText(message_text, 'html'))

    return {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}

def create_message_with_attachment(
    sender,
    to,
    subject,
    message_text,
    attachment_file_path,
    html=False
    ):
    """Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      message_text: Html or plain text message to be sent         
      attachment_file_path: The path to the file to be attached.

    Returns:
      An object containing a base64url encoded email object.
    """
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    if not html:
        msg.attach(MIMEText(message_text, 'plain'))
    else:
        msg.attach(MIMEText(message_text, 'html'))

    content_type, encoding = mimetypes.guess_type(attachment_file_path)

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'

    main_type, sub_type = content_type.split('/', 1)

    if main_type == 'text':
        fp = open(attachment_file_path, 'r')
        attachment_msg = MIMEText(fp.read(), _subtype=sub_type)
        fp.close()

    elif main_type == 'image':
        fp = open(attachment_file_path, 'rb')
        attachment_msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()

    elif main_type == 'audio':
        fp = open(attachment_file_path, 'rb')
        attachment_msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()

    else:
        fp = open(attachment_file_path, 'rb')
        attachment_msg = MIMEBase(main_type, sub_type)
        attachment_msg.set_payload(fp.read())
        fp.close()

    filename = os.path.basename(attachment_file_path)
    attachment_msg.add_header('Content-Disposition', 'attachment', filename=filename)
    msg.attach(attachment_msg)

    return {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}


def create_service(client_secrets_file_path, api_name, api_version, scopes):
    creds = None
    service = None

    if not creds or not cred.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file_path, scopes)
            creds = flow.run_local_server(port=0)
    try:
        service = build(api_name, api_version, credentials=creds)
    except Exception as e:
        print(e)

    return service

def send_message(service, user_id, message):
    """Send an email message.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

    Returns:
    Sent Message.
    """
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print ('Message Id: {}'.format(message['id']))
        return message
    except HTTPError as  error:
        print ('Error {}'.format(error))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send Email with Gmail API.')
    parser.add_argument('--token-path', help='TOKEN_FILE_PATH')
    parser.add_argument('--email-attach', default='', help='EMAIL_ATTACHMENT')
    parser.add_argument('--schedule', default='H', help='D:Daily, H:Hourly, Q:Quarterly, M:Monthly')
    args = parser.parse_args()

    service = create_service(args.token_path, API['name'], API['version'], API['scope'])

    while True:
        message_list = []
        if args.email_attach != '':
            message = create_message_with_attachment(EMAIL['from'],
                EMAIL['to'],
                EMAIL['subject'],
                EMAIL['content'],
                args.email_attach)
            message_list.append(message)

        elif EMAIL['attachments']:
            for attachment_file_path in EMAIL['attachments']:
                message = create_message_with_attachment(EMAIL['from'],
                    EMAIL['to'],
                    EMAIL['subject'],
                    EMAIL['content'],
                    attachment_file_path)
                message_list.append(message)

        if not message_list:
            message = create_plain_html_message(EMAIL['from'],
                EMAIL['to'],
                EMAIL['subject'],
                EMAIL['content'])
            message_list.append(message)

        for message in message_list:
            message_response = send_message(service, EMAIL['from'], message)
            print(message_response)
        
        email_schedule = 'H'
        if args.schedule:
            email_schedule = args.schedule
        else:
            for notation, pair in EMAIL['schedule'].items():
                if pair[0]:
                    email_schedule = notation
                    break
        
        sleep_time = EMAIL_SCHEDULE.get(email_schedule)
        sleep(sleep_time)
