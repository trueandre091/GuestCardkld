import os

import httplib2
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build


def get_service_sacc():
    creds_json = os.path.dirname(__file__) + "\\credentials.json"
    scopes = ['https://www.googleapis.com/auth/spreadsheets']

    creds_service = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scopes).authorize(httplib2.Http())
    return build('sheets', 'v4', http=creds_service)


resp = get_service_sacc().spreadsheets().values().batchGet(spreadsheetId='1wdDfiglVyZAmfqi5OxpVa04FG8Sd4NVcHNQwfMdoefI',
                                                           ranges=["Лист1"]).execute()

print(resp)
