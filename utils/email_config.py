# Email configurations
EMAIL = {
    'from': 'amitxvf@gmail.com',
    'to': 'amitpatel@teckvalley.com,sudoxvf@gmail.com',
    'subject': 'Daily Stock Update',
    'content': 'Dear Receiver,\nPlease find daily stocks updates.',
    'attachments': ['/home/ec2-user/virenv/stocks.log'],
    'schedule':{
        'D': (False, 'Daily'),
        'S': (False, 'Shortly'),
        'H': (True, 'Hourly'),
        'Q': (False, 'Quarterly'),
        'M': (False, 'Monthly')
    }
}

# API configurations
API = {
    'name': 'gmail',
    'version': 'v1',
    'scope': ['https://mail.google.com/',
              'https://www.googleapis.com/auth/gmail.send']

}