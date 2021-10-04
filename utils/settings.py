# Secret Key
secret_key = '4$hsjhd9323j233239032jkj32320903283'

# Email configurations
EMAIL = {
    'from': 'amitxvf@gmail.com',
    'to': 'amitpatel@teckvalley.com,investment@peacehaven.co',
    'subject': 'Daily Stock Update',
    'content': 'Dear Receiver,\nPlease find daily stocks updates.',
    'attachments': ['/home/ec2-user/virenv/stocks.log'],
    'schedule':{
        'D': (False, 'Daily'),
        'S': (True, 'Shortly'),
        'H': (False, 'Hourly'),
        'H2': (False, 'Every Two Hour'),
        'HF': (False, 'Every Six Hour'),
        'Q': (False, 'Every Quarter'),
        'M': (False, 'Monthly')
    }
}

# API configurations
API = {
    'name': 'gmail',
    'version': 'v1',
    'token_path': '/home/ec2-user/virenv/token.json',
    'scope': ['https://mail.google.com/',
              'https://www.googleapis.com/auth/gmail.send']

}

# Flask app configuration
FLASK_CONF = {
    'hostname': 'localhost',
    'port': 8085,
    'debug': True
}

# Accounts
account_peace77t7 = {
    'name': 'Sunny',
    'username': 'peace77t7',
    'account_id': 'U5931342',
    'lsr': '$pbkdf2-sha256$50000$o1TKGUMIwbh3bi3FOIfQeg$sDee9esxLvqbae0zvbf6bqjMltiI9UfuGbj.NRuO8Fo'
}

account_peace77t6 = {
    'name': 'PS',
    'username': 'peace77t6',
    'account_id': 'U6092014',
    'lsr': '$pbkdf2-sha256$50000$O.eck9I6J2QspbSWcg7h3A$07.o555xh2YW41Q27K8zUjLf68MkC6PFWYmNV5T.V7c'
}

account_peace77t5 = {
    'name': 'Albertross',
    'username': 'peace77t5',
    'account_id': 'U6050929',
    'lsr': '$pbkdf2-sha256$50000$O.eck9I6J2QspbSWcg7h3A$07.o555xh2YW41Q27K8zUjLf68MkC6PFWYmNV5T.V7c'
}

account_peace77t4 = {
    'name': 'Miracle Austin',
    'username': 'peace77t4',
    'account_id': 'U6498436',
    'lsr': '$pbkdf2-sha256$50000$O.eck9I6J2QspbSWcg7h3A$07.o555xh2YW41Q27K8zUjLf68MkC6PFWYmNV5T.V7c'
}

# Add Accounts to this to authenticate
ACCOUNTS = {
    'peace77t7': account_peace77t7,
    'peace77t6': account_peace77t6,
    'peace77t5': account_peace77t5,
    'peace77t4': account_peace77t4
}
