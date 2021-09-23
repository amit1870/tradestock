# Email configurations
EMAIL = {
    'from': 'amitxvf@gmail.com',
    'to': 'sudoxvf@gmail.com,amitpatel@teckvalley.com,amitxvf@gmail.com',
    'subject': 'Daily Stock Update',
    'content': 'Dear Receiver,\nPlease find daily stocks updates.',
    'attachments': ['/home/ec2-user/virenv/stocks.log']
}

# API configurations
API = {
    'name': 'gmail',
    'version': 'v1',
    'scope': ['https://mail.google.com/',
              'https://www.googleapis.com/auth/gmail.send']

}