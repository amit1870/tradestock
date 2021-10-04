# -*- coding: utf-8 -*-

import os
import flask
import requests
import argparse

from time import sleep

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import settings
from email.mime.multipart import MIMEMultipart
from utils.settings import EMAIL, API, FLASK_CONF
from utils.send_email import (create_plain_html_message,
                              create_message_with_attachment,
                              send_message)

HOUR = 3600 # Seconds

EMAIL_SCHEDULE = {
    'S': HOUR / 10,
    'H': HOUR,
    'H2': 2 * HOUR,
    'HF': 12 * HOUR,
    'D': 24 * HOUR,
    'Q': 24 * 15 * HOUR,
    'M': 24 * 15 * 30 * HOUR
}

app = flask.Flask(__name__)
app.secret_key = settings.secret_key


@app.route('/')
def index():
  return print_index_table()


@app.route('/send-email')
def send_email():
    global EMAIL_ATTACHMENTS
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    service = googleapiclient.discovery.build(
        API.get("name"), API.get("version"), credentials=credentials)

    # Save credentials back to session in case access token was refreshed.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    flask.session['credentials'] = credentials_to_dict(credentials)

    while True:
        message_list = []
        if EMAIL_ATTACHMENTS:
            for attachment_file_path in EMAIL_ATTACHMENTS:
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

        message_responses = []
        for message in message_list:
            message_response = send_message(service, EMAIL['from'], message)
            message_responses.append(message_response)

        email_schedule = 'S'
        sleep_time = EMAIL_SCHEDULE.get(email_schedule)
        sleep(sleep_time)

    return flask.jsonify(message_responses)


@app.route('/authorize')
def authorize():

    global CLIENT_SECRETS_FILE

    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=API.get('scope'))

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')


    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state

    return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    global CLIENT_SECRETS_FILE
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=EMAIL.get('scope'), state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.redirect(flask.url_for('send_email'))


@app.route('/revoke')
def revoke():
    if 'credentials' not in flask.session:
        return ("You need to <a href='/authorize'>authorize</a> before '" +
                "testing the code to revoke credentials.")

    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    revoke = requests.post('https://oauth2.googleapis.com/revoke',
        params={'token': credentials.token},
        headers = {'content-type': 'application/x-www-form-urlencoded'})
    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        return('Credentials successfully revoked.' + print_index_table())

    return('An error occurred.' + print_index_table())


@app.route('/clear')
def clear_credentials():
    if 'credentials' in flask.session:
        del flask.session['credentials']
    return ('Credentials have been cleared.<br><br>', print_index_table())


def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

def print_index_table():
  return ('<table>' +
          '<tr><td><a href="/send-email">Test an API request</a></td>' +
          '<td>Submit an API request and see a formatted JSON response. ' +
          '    Go through the authorization flow if there are no stored ' +
          '    credentials for the user.</td></tr>' +
          '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
          '<td>Go directly to the authorization flow. If there are stored ' +
          '    credentials, you still might not be prompted to reauthorize ' +
          '    the application.</td></tr>' +
          '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
          '<td>Revoke the access token associated with the current user ' +
          '    session. After revoking credentials, if you go to the test ' +
          '    page, you should see an <code>invalid_grant</code> error.' +
          '</td></tr>' +
          '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
          '<td>Clear the access token currently stored in the user session. ' +
          '    After clearing the token, if you <a href="/test">test the ' +
          '    API request</a> again, you should go back to the auth flow.' +
          '</td></tr></table>')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send Email with Gmail API.')
    parser.add_argument('--token-path', help='TOKEN_FILE_PATH')
    parser.add_argument('--email-attach', default='', help='EMAIL_ATTACHMENT')
    args = parser.parse_args()

    EMAIL_ATTACHMENTS = []
    CLIENT_SECRETS_FILE = None

    if args.token_path:
        CLIENT_SECRETS_FILE = args.token_path

    if args.email_attach != '':
        EMAIL_ATTACHMENTS.append(args.email_attach)
    elif EMAIL['attachments']:
        EMAIL_ATTACHMENTS = EMAIL['attachments']

    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

    # Specify a hostname and port that are set as a valid redirect URI
    # for your API project in the Google API Console.

    if CLIENT_SECRETS_FILE:
        app.run(FLASK_CONF.get('hostname'), FLASK_CONF.get('port'), FLASK_CONF.get('debug'))
    else:
        print("Provide client secret file path to start flask app server.")