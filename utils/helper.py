"""
This module will contain helping functions.
"""
import os
import contextlib
import sys
import os

from requests.exceptions import HTTPError
from .auto_mode import auto_mode_on_accounts


def supress_stdout(func):
    def wrapper(*a, **ka):
        with open(os.devnull, 'w') as devnull:
            with contextlib.redirect_stdout(devnull):
                func(*a, **ka)
    return wrapper


def authenticate_ib_client(ib_client, usernames, passwords):
    try:
        ib_client.logout()
    except HTTPError as e:
        raise e

    authenticated_accounts = auto_mode_on_accounts(usernames, passwords, sleep_sec=2)
    if authenticated_accounts:
        ib_client.is_authenticated()

    return ib_client