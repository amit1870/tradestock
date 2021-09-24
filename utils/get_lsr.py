import sys
import base64
import argparse
sys.path.append('/home/ec2-user/virenv/pcv')

from cryptography.fernet import Fernet

def generate_lsr(key, lsr):
    print(key)
    fernet = Fernet(key)
    encrypted_lsr = fernet.encrypt(lsr.encode('utf-8'))
    return encrypted_lsr

def decrypt_lsr(key, lsr):
    print(key)
    fernet = Fernet(key)
    decrypted_lsr = fernet.decrypt(lsr).decode('utf-8')
    return decrypted_lsr


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Return LSR for string.')
    parser.add_argument('--key', help='Key')
    parser.add_argument('--lsr', help='Value')
    parser.add_argument('--decrypt', default=False, help='True/False')
    args = parser.parse_args()

    if args.key:
        try:
            key = base64.urlsafe_b64encode(args.key)
            lsr = args.lsr.encode('utf-8').decode('utf-8')
        except TypeError as e:
            print(e)
            exit(1)

    if args.decrypt:
        print(decrypt_lsr(key, lsr))
    else:
        print(generate_lsr(key, lsr))
