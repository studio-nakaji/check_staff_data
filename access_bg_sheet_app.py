import streamlit as st
from access_sheets_dir import access_sheets as sp
import pandas as pd
import datetime
from access_sheets_dir import access_drive as ad
import requests
import json
import time

"""
### Nスタアプリ
## 作業の明細書をPDFにするよ
"""

def color_add(val):
    return f"color:#2aa3b1"


def main():
    SPREADSHEET_KEY = '1fH75awI6NAOjUGoiuZlD4YsNs1cnXcyLA9wsJmNP5Lg'    #「背景スケジュールまとめ」スプレッドシート
    # re = sp.access_spread_sheet(SPREADSHEET_KEY)
    # st.write(re)
    
    wb, title_dic = sp.get_sheets_name(SPREADSHEET_KEY)
    title_list = list(title_dic)
    title_list = [""]+title_list
    title = st.selectbox(label="シートを選択してね" ,options= title_list)
    
    if title == "":
        st.stop()
    today = datetime.datetime.today()
    year = today.year
    left_col,right_col = st.columns(2)
    
    default_month = today.month-1
    if today.day<10:
        default_month = default_month-1
    if default_month <= 0:
        default_month = 1
    select_year = left_col.selectbox("取得したい年は？",list(range(2022,year+1)))
    month = right_col.selectbox("取得したい月は？",range(1,13),index=default_month)
    
    drive = ad.get_drive()
    st.write(drive)
    if st.button("全スタッフ分をPDF出力しましょう！"):
        st.write("出力がスタートされる")
    #     save_pdf(st, title,select_year,month)
        
    ##旧バージョン(個別にcsv書き出し)
    # if st.button("スタッフを選択してcsv取得"):
    #     member = sp.get_member(wb,title)
    #     member = [""] + member                #空白を先頭に追加
    #     worker = st.selectbox("スタッフを選択",member)
    #     if worker == "" or month == "":
    #         st.stop()
    #     if st.button("取得"):
    #         st.write(f"{worker}さんの{month}月分の報酬金額は・・・")
    #         new_df, reward_df = sp.main(wb,title,worker,month)
    #         # new_df = new_df.set_index("Cut番号",drop=True)
    #         if type(new_df)== pd.core.frame.DataFrame:
    #             st.table(new_df.style.applymap(color_add,subset=["報酬金額"]))      #カット単位の明細を表示
    #             st.table(reward_df.style.applymap(color_add,subset=["支払い金額"])) #総額に対する税金明細を表示
    #             sum_df = new_df.join(reward_df)         #明細を合体
    #             sum_df = sum_df.fillna("")              #NANを空白に変更
    #             # st.table(sum_df)
    #             csv = sum_df.to_csv().encode('utf-8')
    #             st.download_button(
    #                 "ダウンロード",
    #                 csv,
    #                 f"Nスタ_{worker}様:{month}月分明細.csv",
    #                 "text/csv",
    #                 key="download-csv"
    #             )
    #         else:
    #             f"おや？{month}月は作業されてないようですね。"

def check_file_exist(drive, team_drive_id, folder_id, text):
    files = ad.get_files_list(drive, team_drive_id, folder_id)  #フォルダ下のファイル名とidを辞書リストで取得
    if text in list(files): #ファイル名が含まれていたら
        return files[text]  #そのファイルのidを返す
    else:
        return False

def save_pdf(st, title,year,month):
    progress_num = 0
    bar = st.progress(progress_num)
    now_progress = st.empty()
            
    #「背景スケジュールまとめ」スプレッドシートID
    SPREADSHEET_KEY = '1fH75awI6NAOjUGoiuZlD4YsNs1cnXcyLA9wsJmNP5Lg'
    #経理ドライブ/支払い明細書の親フォルダID
    statement_folder_id = "1FL1SaR15Y5rVLHEXOJ2bgM6MkJ03hgxY"
    #共有ドライブID
    team_drive_id = "0ALoDSiRif-lvUk9PVA"
    #Gasへのアクセス用のJSONファイルの読み込み
    json_open = open("access_sheets_dir/access_gas.json", "r")
    json_load = json.load(json_open)
    copy_url = json_load["COPY_URL"]
    set_url = json_load["SET_URL"]
    pdf_url = json_load["PDF_URL"]
    #メンバーの本名を辞書で取得
    worker_dic = member_name()
    
    
    drive = ad.get_drive()
    
    #指定の年数のフォルダの存在チェック
    result_1 = check_file_exist(drive, team_drive_id, statement_folder_id, str(year))
    if result_1 == False:   #存在しなかったら
        now_progress.text(f"{year}フォルダが無いので作りますね。")
        yaer_folder_id = ad.create_folder(drive,statement_folder_id,str(year))["id"]    #フォルダ作成 フォルダのIDを取得
    else:                   #あれば
        yaer_folder_id = result_1   #そのIDを取得
        now_progress.text(f"{year}フォルダがありました。取得完了。")
    
    progress_num = 5
    bar.progress(progress_num)
    #PDFフォルダの存在チェック
    result_2 = check_file_exist(drive, team_drive_id, yaer_folder_id, f"{month}月分PDF")
    if result_2 == False:   #存在しなかったら
        now_progress.text("PDFフォルダが無いので作りますね。")
        pdf_folder_id = ad.create_folder(drive,yaer_folder_id, f"{month}月分PDF")["id"]    #フォルダ作成 フォルダのIDを取得
    else:                   #あれば
        pdf_folder_id = result_2   #そのIDを取得
        now_progress.text("PDFフォルダがありました。取得完了。")
    
    progress_num = 10
    bar.progress(progress_num)
    
    #コピー先のワークブックの存在チェック。あればidを取得。なければコピー後idを取得
    wb_title = str(month)+"月分"
    result_3 = check_file_exist(drive, team_drive_id, yaer_folder_id, wb_title)
    if result_3 == False:           #存在しなかったら
        now_progress.text("ワークブックが見当たらないので、Gasにテンプレートのコピーをお願いしてみます")
        #テンプレートからコピー ファイルのIDを取得
        copy_wb_data = json.dumps({"month":wb_title,"id":yaer_folder_id})
        # print(copy_wb_data)
        r = requests.post(copy_url,data=copy_wb_data)  #Gasへのリクエスト
        print(r)
        #もう一度ワークブックの存在チェック。あればidを取得。
        result_4 = check_file_exist(drive, team_drive_id, yaer_folder_id, wb_title)
        if result_4 != False:
            now_progress.text("ワークブックがコピーできました")
            wb, sh_dic = sp.get_sheets_name(result_4)
    else:                           #あれば
        wb, sh_dic = sp.get_sheets_name(result_3)  #そのIDからワークブックとシート名をリストで取得
        now_progress.text("ワークブックを見つけました")
    progress_num = 20
    bar.progress(progress_num)
    
    #背景スケジュールまとめワークブックを取得
    bg_wb = sp.access_spread_sheet(SPREADSHEET_KEY)
    now_progress.text("メンバーの作業量を見てみますね")
    members = sp.get_member(bg_wb,title)
    
    progress_num = 30
    bar.progress(progress_num)
    
    member_num = len(members)
    #メンバー毎に処理
    first_count = 0
    export_count = 0
    for worker in members:
        first_count+=1
        now_progress.text(f"{first_count}/{member_num}人目")
        worker_name = worker_dic[worker]
        wb_id = wb.id
        
        #シート名チェック
        if worker_name in list(sh_dic):      #明細書ワークブックのシート名に作業者の名前があれば
            continue                    #スルー
        else:                           #なければ
            new_df, reward_df = sp.main(bg_wb,title,worker,month)
            now_progress.text(f"{worker}さんの作業情報を見てみます")
            if type(new_df) == pd.core.frame.DataFrame:
                worker_data = {"wb_id":wb_id,"worker":worker_name,"year":year,"month":month,"row":len(new_df),"data":new_df.to_dict(orient='records')}
                now_progress.text(f"{worker}さんの{month}月のカット情報をシートにまとめます")
                r = requests.post(set_url,data= json.dumps(worker_data).encode('utf-8'))#ensure_ascii=False
                print(r)
                export_count += 1
                
            else:
                now_progress.text(f"{worker}さんには{month}月の作業情報がありませんね。スキップしちゃいます")
        
        progress_num = progress_num + int(50/member_num)
        bar.progress(progress_num)
    
    now_progress.text(f"{month}月に作業してくれたスタッフの全作業料情報をスプレッドシートに出力できました！")
    
    #PDF出力
    pdf_count = 0
    for worker in members:
        pdf_count+=1
        now_progress.text(f"{pdf_count}/{member_num}枚目をPDFにしてます")
        worker_name = worker_dic[worker]
        export_data = {"wb_id":wb.id,"worker":worker_name,"pdf_folder_id":pdf_folder_id}
        # print(export_data)
        r = requests.post(pdf_url,data= json.dumps(export_data).encode('utf-8'))
        print(r)
        progress_num = progress_num + int(20/member_num)
        bar.progress(progress_num)
        
    now_progress.text(f"{export_count}枚分をPDFにできました！")
    time.sleep(1)
    now_progress.text("お疲れ様でした。URLからPDFページへどうぞ")
    time.sleep(0.5)
    
    url = "https://drive.google.com/drive/folders/" + pdf_folder_id
    link = f"[PDFフォルダリンク]{url}"
    st.markdown(link,unsafe_allow_html=True)


def save_pdf2(title,year,month):
            
    #「背景スケジュールまとめ」スプレッドシートID
    SPREADSHEET_KEY = '1fH75awI6NAOjUGoiuZlD4YsNs1cnXcyLA9wsJmNP5Lg'
    #経理ドライブ/支払い明細書の親フォルダID
    statement_folder_id = "1FL1SaR15Y5rVLHEXOJ2bgM6MkJ03hgxY"
    #共有ドライブID
    team_drive_id = "0ALoDSiRif-lvUk9PVA"
    #Gasへのアクセス用のJSONファイルの読み込み
    json_open = open("access_sheets_dir/access_gas.json", "r")
    json_load = json.load(json_open)
    copy_url = json_load["COPY_URL"]
    set_url = json_load["SET_URL"]
    pdf_url = json_load["PDF_URL"]
    #メンバーの本名を辞書で取得
    worker_dic = member_name()
    
    
    drive = ad.get_drive()
    
    #指定の年数のフォルダの存在チェック
    result_1 = check_file_exist(drive, team_drive_id, statement_folder_id, str(year))
    if result_1 == False:   #存在しなかったら
        yaer_folder_id = ad.create_folder(drive,statement_folder_id,str(year))["id"]    #フォルダ作成 フォルダのIDを取得
    else:                   #あれば
        yaer_folder_id = result_1   #そのIDを取得
    
    #PDFフォルダの存在チェック
    result_2 = check_file_exist(drive, team_drive_id, yaer_folder_id, f"{month}月分PDF")
    if result_2 == False:   #存在しなかったら
        pdf_folder_id = ad.create_folder(drive,yaer_folder_id, f"{month}月分PDF")["id"]    #フォルダ作成 フォルダのIDを取得
    else:                   #あれば
        pdf_folder_id = result_2   #そのIDを取得
    
    
    #コピー先のワークブックの存在チェック。あればidを取得。なければコピー後idを取得
    wb_title = str(month)+"月分"+"_"+title
    result_3 = check_file_exist(drive, team_drive_id, yaer_folder_id, wb_title)
    if result_3 == False:           #存在しなかったら
        #テンプレートからコピー ファイルのIDを取得
        copy_wb_data = json.dumps({"month":wb_title,"id":yaer_folder_id})
        print("テンプレートをコピー")
        r = requests.post(copy_url,data=copy_wb_data)  #Gasへのリクエスト
        print(r)
        #もう一度ワークブックの存在チェック。あればidを取得。
        result_4 = check_file_exist(drive, team_drive_id, yaer_folder_id, wb_title)
        if result_4 != False:
            wb, sh_dic = sp.get_sheets_name(result_4)
    else:                           #あれば
        wb, sh_dic = sp.get_sheets_name(result_3)  #そのIDからワークブックとシート名をリストで取得
    
    #背景スケジュールまとめワークブックを取得
    bg_wb = sp.access_spread_sheet(SPREADSHEET_KEY)
    members = sp.get_member(bg_wb,title)
    
    #メンバー毎に処理
    for worker in members:
        worker_name = worker_dic[worker]
        wb_id = wb.id
        
        #シート名チェック
        if worker_name in list(sh_dic):      #明細書ワークブックのシート名に作業者の名前があれば
            continue                    #スルー
        else:                           #なければ
            new_df, reward_df = sp.main(bg_wb,title,worker,month)
            if type(new_df) == pd.core.frame.DataFrame:
                print(f"{worker_name}さんのデータをシートに出力")
                worker_data = {"wb_id":wb_id,"worker":worker_name,"year":year,"month":month,"row":len(new_df),"data":new_df.to_dict(orient='records')}
                r = requests.post(set_url,data= json.dumps(worker_data).encode('utf-8'))#ensure_ascii=False
                print(r)
                
        
    
    #PDF出力
    for worker in members:
        worker_name = worker_dic[worker]
        export_data = {"wb_id":wb.id,"worker":worker_name,"pdf_folder_id":pdf_folder_id}
        print(f"{worker_name}さんのデータをPDF出力")
        # print(export_data)
        r = requests.post(pdf_url,data= json.dumps(export_data).encode('utf-8'))
        print(r)
        
    
    url = "https://drive.google.com/drive/folders/" + pdf_folder_id
    print(url)
    
        
def member_name():
    #スタッフ名ワークブックid
    staff_name_wb_id = "1ENGRCc9IQNY1W0qmFReKaFxqC3E7D9V0548XORJpjCc"
    #メンバーの本名を取得と辞書化
    staff_wb, staff_sh_dic = sp.get_sheets_name(staff_name_wb_id)
    staff_sh = staff_sh_dic["背景解剖BIZメンバー"]
    staff_data = staff_sh.get_all_values()           #全てのデータを取得
    content_df = pd.DataFrame(staff_data[1:],columns=staff_data[0])         #3行目以降をデータフレームで取得。3行をカラムに指定
    worker_dic = {}
    for i in range(len(content_df["BIZ内名称"])):
        worker_dic[content_df["BIZ内名称"][i]]=content_df["明細書宛名"][i]    
    return worker_dic
 
if __name__ == "__main__":
    main()
    # title = "Tv_すずめの戸締まり#A"
    # title = "その他依頼"
    # year = 2022
    # month = 5
    # save_pdf2(title,year,month)
    