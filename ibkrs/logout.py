import sys
import argparse
sys.path.append('/home/ec2-user/virenv/pcv')

from requests.exceptions import HTTPError
from pprint import pprint
from ibw.client import IBClient

def logout(username, account_id):
    # Create a new session of the IB Web API.
    ib_client = IBClient(
        username=username,
        account=account_id,
        is_server_running=True
    )

    response = ib_client.is_authenticated()
    if response.ok:
        auth_status = response.text.get('authenticated')
        if auth_status:
            return ib_client.logout()
    return response

def main(args):
    try:
        response = logout(args.username, args.account_id)
        if response.ok:
            print("Logout successful.")
        else:
            print("Logout unsuccessful.")
    except HTTPError as e:
        print(e)
        print("Logout unsuccessful.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get stock details with Interactive Brokers.')
    parser.add_argument('--username', help='YOUR_USERNAME')
    parser.add_argument('--account-id', help='YOUR_ACCOUNT_NUMBER')
    args = parser.parse_args()

    main(args)
