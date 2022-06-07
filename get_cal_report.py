from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import calendar as cal
import streamlit as st



def get_gcal_main(set_year,set_month):
    #カレンダーIDのリスト
    id_dict = [
                {"main_ID":"nakaji@studio-nakaji.com"},
                {"mai_ID":"c_pc8j2tb1hue45v4adq4g7t0tnc@group.calendar.google.com"},
                {"haikai_ID":"c_90ih641bbpif2h1vp3p0l6vi5k@group.calendar.google.com"}
            ]
    
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    # CLIENT_SECRET_FILE = '/Volumes/GoogleDrive/マイドライブ/MyScript/My_Python/Nstudio/client_secret_cal.json'
    secrets = st.secrets["GoogleCalenderKey"]
    
    CAL_ID = id_dict[1]["mai_ID"]
    
    first_hms = "T00:00:00z"                    #0時0分0秒
    last_hms = "T23:59:59z"                     #23時59分59秒
    
    first = datetime.date(set_year,set_month,1)                     #指定月の月初を取得；2022-01-01 <class 'datetime.date'>
    first_day = str(first)+first_hms                                #指定のフォーマットに
    
    last = cal.monthrange(set_year, set_month)[1]                   #指定月の最終日を取得：31 <class 'int'>
    last_dayonly = datetime.date(set_year,set_month,last)           #datetime型で取得：2022-01-31 <class 'datetime.date'>
    last_day = str(last_dayonly) + last_hms                         #指定のフォーマットに
    
    print(f"{set_year}年{set_month}月の合計作業時間")
    creds = None
    
    # ファイルtoken.jsonは、ユーザーのアクセストークンと更新トークンを保存し、
    # 認証フローが初めて完了すると自動的に作成されます。
    # if os.path.exists(secrets_token):
    # if os.path.exists(token.json):
        # creds = Credentials.from_authorized_user_file(token.json, SCOPES)
    
    creds = Credentials(token=secrets["token"],refresh_token=secrets["refresh_token"],id_token=None,token_uri=secrets["token_uri"],client_id=secrets["client_id"],client_secret=secrets["client_secret"],scopes=secrets["scopes"],quota_project_id=secrets["project_id"],expiry=secrets["expiry"])
    # 使用可能な（有効な）クレデンシャルがない場合は、ユーザーにログインさせます。
    # if not creds or not creds.valid:
    #     print("有効なクレデンシャルがない為、ログインして下さい")
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:
    #         flow = InstalledAppFlow.from_client_secrets_file(
    #             CLIENT_SECRET_FILE, SCOPES)
    #         creds = flow.run_local_server(port=0)
    #     # 次の実行のためにクレデンシャルを保存します
    #     with open('token.json', 'w') as token:
    #         token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # CalendarAPIを呼び出す
        events_result = service.events().list(calendarId=CAL_ID,
                                            timeMin=first_day,
                                            timeMax=last_day, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('今後のイベントは見つかりませんでした。')
            return
        else:
            return events
    except HttpError as error:
        print('エラーが発生しました: %s' % error)
        return None
    
if __name__ == '__main__':
    get_gcal_main()