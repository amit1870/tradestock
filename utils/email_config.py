# Email configurations
EMAIL = {
    'from': 'amitxvf@gmail.com',
    'to': 'amitpatel@teckvalley.com,sunny@peacehaven.co',
    'subject': 'Daily Stock Update',
    'content': 'Dear Receiver,\nPlease find daily stocks updates.',
    'attachments': ['/home/ec2-user/virenv/stocks.log'],
    'schedule':{
        'D': (False, 'Daily'),
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