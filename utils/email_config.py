# Email configurations
EMAIL = {
    'from': 'amitxvf@gmail.com',
    'to': 'sudoxvf@gmail.com',
    'subject': 'Subject is Fine',
    'content': 'This message is coming from Python test script.',
    'attachments': ['/home/ec2-user/virenv/stocks.log']
}

# API configurations
API = {
    'name': 'gmail',
    'version': 'v1',
    'scope': ['https://mail.google.com/',
              'https://www.googleapis.com/auth/gmail.send']

}