from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from cultisk.Models import OAuth2User
import pickle
import os.path
# import email
#
import html
import json

# Define the SCOPES. If modifying it, delete the token.pickle file.

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']


def listToString(s):
    str1 = ""
    for ele in s:
        str1 += ele
    str2 = ''.join(e for e in str1 if e.isalnum() or e.isspace() or e == ">" or e == "<" or e == "@" or e == ".")
    return str2


def email_whitelist(namelist, addr):
    m = True
    if namelist is not None:
        for elem in namelist:
            if elem in addr:
                m = False
                break
    else:
        m = True
    return m


# @openid_required
# user_identifier = get_openid_identity()
# oauth2_user = OAuth2User.query.filter_by(sub=user_identifier).first()
# cred = oauth2_user.credentials
# cred = json.loads(cred)
# cred = Credentials(**cred)
# service = build('gmail', 'v1', credentials=cred)


def return_sevice(user_identifier):
    creds = None
    # The file token.pickle contains the user access token.
    # Check if it exists
    # if os.path.exists('token.pickle'):
    #     # Read the token from the file and store it in the variable creds
    #     with open('token.pickle', 'rb') as token:
    #         creds = pickle.load(token)

    # If credentials are not available or are invalid, ask the user to log in.
    oauth2_user = OAuth2User.query.filter_by(sub=user_identifier).first()
    cred = oauth2_user.credentials
    cred = json.loads(cred)
    cred = Credentials(**cred)
    # if not creds or not creds.valid:
    # if creds and creds.expired and creds.refresh_token:
    #     creds.refresh(Request())
    # else:
    #     flow = InstalledAppFlow.from_client_secrets_file('cultisk/credentials.json', SCOPES)
    #     creds = flow.run_local_server(port=0)
    #
    #     # Save the access token in token.pickle file for the next run
    # with open('token.pickle', 'wb') as token:
    #     pickle.dump(creds, token)
    service = build('gmail', 'v1', credentials=cred)
    return service


# oauth2_user = OAuth2User.query.filter_by(sub=user_identifier).first()
# cred = oauth2_user.credentials
# cred = json.loads(cred)
# cred = Credentials(**cred)
# service = build('gmail', 'v1', credentials=cred)
# return service


def getEmails(user_id, non=None):
    # request a list of all the messages
    service = return_sevice(user_id)
    results = service.users().messages().list(maxResults=100, userId='me', labelIds=['INBOX']).execute()
    messages = results.get('messages', [])
    # messages is a list of dictionaries where each dictionary contains a message id.
    # iterate through all the messages

    # count = 1
    # data = []
    m_dict = {}
    for message in messages:
        # Get the message from its id
        message_list = []
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        # msg2=service.users().messages().batchModify(userId='me',)
        # print(msg)
        headers = msg["payload"]["headers"]
        subject = [i['value'] for i in headers if i["name"] == "Subject"]
        sender = [i['value'] for i in headers if i["name"] == "From"]
        msg_body = msg['snippet']

        # convert to strings
        subject_val = listToString(subject)
        sender_val = listToString(sender)

        # print("Subject: ", subject_val)
        # print("Sender: ", sender_val)
        if email_whitelist(non, sender_val):
            message_list.append(subject_val)
            message_list.append(sender_val)
            message_list.append(html.unescape(msg_body))
            message_list.append(message['id'])
            m_dict[message['id']] = message_list
    return m_dict


def trash_message(userID, message_id):
    service = return_sevice(userID)
    body = {"addLabelIds": ['SPAM'],
            "removeLabelIds": []}
    try:
        message = service.users().messages().modify(userId='me', id=message_id, body=body).execute()
        print('Message Id: %s sent to Spam Folder.' % message['id'])
        # print('message sent to trash')
        # get_attachments(service,message_id,'C:\Project_Cultisk\EmailFilterPackage\Attachements')
        return message
    except Exception as error:
        print('An error occurred while sending email: %s' % error)
        return None


def untrash_message(userID, message_id):
    service = return_sevice(userID)
    body = {"addLabelIds": ['INBOX'],
            "removeLabelIds": []}
    try:
        message = service.users().messages().modify(userId='me', id=message_id, body=body).execute()
        print('Message Id: %s sent from Spam Folder.' % message['id'])
        # print('message sent to trash')
        # get_attachments(service,message_id,'C:\Project_Cultisk\EmailFilterPackage\Attachements')
        return message
    except Exception as error:
        print('An error occurred while sending email: %s' % error)
        return None


def get_one_email(user_id, messid):
    # request a list of all the messages
    service = return_sevice(user_id)
    message_list = []
    m_dict = {}
    # Get the message from its id
    msg = service.users().messages().get(userId='me', id=messid).execute()
    # msg2=service.users().messages().batchModify(userId='me',)
    # print(msg)
    headers = msg["payload"]["headers"]
    subject = [i['value'] for i in headers if i["name"] == "Subject"]
    sender = [i['value'] for i in headers if i["name"] == "From"]
    msg_body = msg['snippet']

    # convert to strings
    subject_val = listToString(subject)
    sender_val = listToString(sender)

    # print("Subject: ", subject_val)
    # print("Sender: ", sender_val)
    message_list.append(subject_val)
    message_list.append(sender_val)
    message_list.append(html.unescape(msg_body))
    message_list.append(messid)
    m_dict[messid] = message_list
    return m_dict

# if __name__ == "__main__":
#     return_sevice(u)
