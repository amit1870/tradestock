import sys
import base64
import argparse
sys.path.append('/home/ec2-user/virenv/pcv')

from passlib.context import CryptContext

def get_context():
    context = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        pbkdf2_sha256__default_rounds=50000)

    return context

def generate_lsr(context, key):
    return context.hash(key)

def decrypt_lsr(context, key, lsr):
    return context.verify(key, lsr)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Return LSR for string.')
    parser.add_argument('--key', help='Key')
    parser.add_argument('--lsr', help='Value')
    parser.add_argument('--decrypt', default=False, help='True/False')
    args = parser.parse_args()

    context = get_context()
    if args.decrypt:
        print(decrypt_lsr(key, lsr))
    else:
        print(generate_lsr(key))
