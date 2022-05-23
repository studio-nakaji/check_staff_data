import gspread
import pandas as pd

from oauth2client.service_account import ServiceAccountCredentials

#スプレッドシートへのアクセス
def access_spread_sheet(SPREADSHEET_KEY):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

    #認証情報設定   
    credentials = ServiceAccountCredentials.from_json_keyfile_name("access_sheets_dir/access_sp_secret.json", scope)

    #OAuth2の資格情報を使用してGoogle APIにログインします。
    gc = gspread.authorize(credentials)

    #共有設定したスプレッドシートキーを変数[SPREADSHEET_KEY]に格納する。
    #(スプレッドシートのURLのxxxxの部分→[〜spreadsheets/d/xxxx/edit〜])
    # SPREADSHEET_KEY = '1fH75awI6NAOjUGoiuZlD4YsNs1cnXcyLA9wsJmNP5Lg'

    #スプレッドシートを開く
    sp = gc.open_by_key(SPREADSHEET_KEY)
    return sp

#スプレッドシート内の指定の名前を含むシートの[0]番目を取得
def get_sheet_valus(sp, sh_name):
    target_sh = [sh for sh in sp.worksheets() if sh_name in sh.title][0]
    return target_sh

#1カット毎の情報を取得→データフレームで返す
def get_cut_deta(values,unit_price):
    new_columns = values["担当"]        #担当者名を取得
    values = values.rename(index={"Cut":"Cut番号","上乗":"単価","発注":"発注日","納品":"納品日","報酬":"報酬金額"}) #インデックス名を変更
    values = values.drop(["撮出", "L/o in","担当"])                     #不要な行の削除
    values["単価"] = "¥" + f"{int(int(values['単価'])+unit_price):,}"   #単価を基本単価との合計金額に変更
    values["報酬金額"] = int(values["報酬金額"].replace(",",""))
    values.name = new_columns               #カラム名を担当者名に変更
    # print(values)
    values = pd.DataFrame(values).T         #行・列を入れ替えてデータフレームに
    return values

def str_3digits(x):
    return "¥" + f"{int(x):,}"

def get_sheets_name(SPREADSHEET_KEY):
    sp = access_spread_sheet(SPREADSHEET_KEY)
    sh_list = [sh.title for sh in sp.worksheets()]
    sh_list.insert(0,"")
    return sh_list

def get_member(SPREADSHEET_KEY,title):
    sp = access_spread_sheet(SPREADSHEET_KEY)
    target_sh = get_sheet_valus(sp, title)      #指定の名前のシートを取得
    data = target_sh.get_all_values()           #全てのデータを取得
    member_df = pd.DataFrame(data[15:32],columns=data[13])    #15行目〜32行目をデータフレームで取得。13行をカラムに指定
    member_df = member_df.drop(member_df.columns[1:],axis=1)  #4列分を削除
    member = [i for i in sum(member_df.values.tolist(),[]) if i != ""]
    member.insert(0,"")
    return member


def main(SPREADSHEET_KEY,title,worker,month):
    # title = "すずめ"
    # worker = "針﨑"
    # month = 4

    sp = access_spread_sheet(SPREADSHEET_KEY)
    target_sh = get_sheet_valus(sp, title)      #指定の名前のシートを取得

    data = target_sh.get_all_values()           #全てのデータを取得
    story_num = target_sh.acell("C5")
    unit_price = target_sh.acell("B7").value.replace(",","") #","を除去した基本単価を取得
    if "¥" in unit_price:
        unit_price = unit_price.replace("¥","").replace(" ","") #"¥"があればそれも除去
    unit_price = int(unit_price)                                #整数値に
    content_df = pd.DataFrame(data[3:],columns=data[2])         #3行目以降をデータフレームで取得。3行をカラムに指定
    content_df = content_df.drop(content_df.columns[[0,1,2,3]],axis=1)      #4列分を削除

    col = list(content_df.columns)                                      #シートのカラムをリストで取得(※重複している)
    tantou_col = [i for i,value in enumerate(col) if value == "担当"]   #"担当の列番号をリスト化"
    siries_list=[]
    for i in tantou_col:    #担当の列を検索
        tantou_row = [i for i,value in enumerate(content_df.iloc[:,i] == worker) if value == True] #該当の担当者を含む行番号を取得
        # print(len(tantou_row))
        if len(tantou_row)>0:   #1つ以上あれば処理
            for row in tantou_row:                                          #行番号順に検索
                if content_df.iloc[row,i+3].split("/")[0] == str(month):
                    siries_list.append(content_df.iloc[row,i-3:i+6])        #Siriesをリストに追加
        else:
            continue
    if len(siries_list) == 0:
        return None, None
    new_df = get_cut_deta(siries_list[0],unit_price)       
    for i in range(len(siries_list)):
        new_df = pd.merge(new_df,get_cut_deta(siries_list[i],unit_price), how='outer')
    reward = new_df["報酬金額"].sum()
    #支払いの総額明細データフレーム[報酬総額,源泉徴収額,消費税額,支払い金額]
    reward_df = pd.DataFrame([[str_3digits(reward),str_3digits(reward*0.1021),str_3digits(reward*0.1),str_3digits(int(reward)-int(reward*0.1021)+int(reward*0.1))]],columns=["報酬総額","源泉徴収額","消費税額","支払い金額"])
    new_df["報酬金額"] = new_df["報酬金額"].map(str_3digits)
    # print(new_df)
    # print(reward_df)
    # print(member)
    return new_df, reward_df
    
if __name__ == "__main__":
    title = "すずめ"
    worker = "針﨑"
    month = 4
    SPREADSHEET_KEY = '1fH75awI6NAOjUGoiuZlD4YsNs1cnXcyLA9wsJmNP5Lg'    #「背景スケジュールまとめ」スプレッドシート
    new_df, reward_df = main(SPREADSHEET_KEY,title,worker,month)
    # member,story_num = get_member(SPREADSHEET_KEY,title)
    # print(new_df.set_index("Cut番号",drop=True))
    
    
    

