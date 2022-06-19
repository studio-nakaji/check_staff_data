from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
from google.oauth2 import service_account
import os
import streamlit as st

def get_drive():
    gauth = GoogleAuth()
    
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    # import json
    # json_acct = json.loads("drive_secrets.json")
    # print(json_acct)

    #資格情報ロードするか、存在しない場合は空の資格情報を作成
    # 認証(ローカル)
    gauth.LoadCredentialsFile("mycreds.txt")
    # import toml
    # import json
    # with open("../secrets.toml") as f:
    #     secrets = toml.load(f)["GoogleDriveKey"]
    #     j = json.dumps(secrets, indent=2)
    # # 認証(クラウド)
    # gauth.LoadCredentialsFile(j)
    # secrets = st.secrets["GoogleDriveKey"]
    # import toml
    # with open("../secrets.toml") as f:
    #     secrets = toml.load(f)["GoogleSpreadSheetKey"]
    # secrets = st.secrets["GoogleDriveKey"]
    
    # credentials = service_account.Credentials.from_service_account_info(secrets, scopes=scope)
    # gauth.credentials = service_account.Credentials.from_service_account_info(secrets, scopes=scope)
    
    #Googleサービスの資格情報がない場合
    if gauth.credentials is None:
        #ユーザーから認証コードを自動的に受信しローカルWebサーバーを設定
        gauth.LocalWebserverAuth()
    #アクセストークンが存在しないか、期限切れかの場合    
    elif gauth.access_token_expired:
        #Googleサービスを認証をリフレッシュする
        gauth.Refresh()
    #どちらにも一致しない場合    
    else:
        #Googleサービスを承認する
        gauth.Authorize()
    #資格情報をtxt形式でファイルに保存する  
    gauth.SaveCredentialsFile("mycreds.txt") 

    drive = GoogleDrive(gauth)
    
    return drive


#フォルダの作成(作成場所のid,作成フォルダ名)
def create_folder(drive, parent_folder_id, subfolder_name):
    newFolder = drive.CreateFile({'title': subfolder_name, "parents": [{"kind": "drive#fileLink", "id": parent_folder_id}],
                                    "mimeType": "application/vnd.google-apps.folder"})
    newFolder.Upload(param={'supportsTeamDrives': True})
    return newFolder


#特定フォルダ下のファイルを全てダウンロード(ローカルフォルダーパス,共有ドライブID,ダウンロードしたいフォルダID)
def download_recursively(drive, save_folder, team_drive_id, drive_folder_id):
    # 保存先フォルダがなければ作成
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    max_results = 100
    query = f"'{drive_folder_id}' in parents and trashed=false"

    for file_list in drive.ListFile({'q': query, 'maxResults': max_results, 'supportsAllDrives':True,
                                    'corpora': "teamDrive",'teamDriveId': team_drive_id,
                                    'includeTeamDriveItems': "true",'supportsTeamDrives': "true",}):
        for file in file_list:
            # mimeTypeでフォルダか判別
            if file['mimeType'] == 'application/vnd.google-apps.folder':
                download_recursively(os.path.join(save_folder, file['title']), file['id'])
            else:
                file.GetContentFile(os.path.join(save_folder, file['title']))


#共有ドライブ内の特定フォルダ下のファイルを取得(共有ドライブID,特定フォルダのID)
def get_files_list(drive, team_drive_id, drive_folder_id):
    
    max_results = 100
    query = f"'{drive_folder_id}' in parents and trashed=false"

    files = {}          #辞書を定義
    for file_list in drive.ListFile({'q': query, 'maxResults': max_results,'supportsAllDrives':True,
                                    'corpora': "teamDrive",'teamDriveId': team_drive_id,
                                    'includeTeamDriveItems': "true",'supportsTeamDrives': "true",}):
        for file in file_list:
            files[file["title"]]=file["id"]     #ファイル名とそのidを辞書に追加
    return files


if __name__ == "__main__":
    drive = get_drive()
    #特定のフォルダID
    folder_id = "1FL1SaR15Y5rVLHEXOJ2bgM6MkJ03hgxY"
    ID = "1EwP979EinsmcXs4l05ecKMJdg1WSKvqP"
    #共有ドライブID
    team_drive_id = "0ALoDSiRif-lvUk9PVA"
    #templateシートID
    template_id = "1YCY_4u2vkq5WK281ei0b9gqdgqmM2TOX"
    # folder = create_folder(drive, ID, "subfolder_name")
    print(drive)