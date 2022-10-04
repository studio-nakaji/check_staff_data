import streamlit as st
import get_work_time_app_v1_0_1

import requests
import json
import hashlib
import csv

from datetime import datetime


def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False

@st.cache(allow_output_mutation=True)
def login_info(data):
    st.session_state["login_info"] = data
    return st.session_state["login_info"]

def login_page ():
    api_url ="https://script.google.com/macros/s/AKfycbwGvcYp_dVfhH8LnjUMO--5l4m7H4N-GF1m8ANLrSiawdOT6GN_Xuj0TET7CvLpHAulqQ/exec"

    sb = st.sidebar
    if 'login_info' not in st.session_state:
        st.session_state['login_info'] = {"login":False}
    if st.session_state["login_info"]["login"] == False:
        sb.title("Nスタアプリ")
        ra = sb.radio("ログイン情報入力",["ログイン","サインアップ"])
        if ra == "ログイン":
            mail = sb.text_input("メールアドレス")
            pw = sb.text_input("パスワード",type="password")
            login_button = sb.button("ログイン")
            if login_button:
                print("ログイン")
                checkes = [mail, pw]
                if "" in checkes:
                    sb.text("情報が不足しています")
                else:
                    pw = make_hashes(pw)
                    post_data = {"mail":mail,"password":pw,"type":"login"}
                    print(f"Post data =>{post_data}")
                    event_time_r = requests.post(api_url,data= json.dumps(post_data).encode('utf-8'))
                    data = json.loads(event_time_r.text)
                    print(f"Return data =>{data}")
                    print(datetime.now())
                    if data["login"]:
                        login_info(data)
                        if st.session_state["login_info"] == {"login":False}:
                            st.session_state["login_info"].update(data)
                        
                    else:
                        if data["data"] == "Not Fined":
                            sb.text("入力されたメールアドレスは登録されていません")
                        elif data["data"] == "No Password":
                            sb.text("入力されたメールアドレスにはパスワードが設定されていません")
                            sb.text("サインアップして下さい")
                        elif data["data"] == "Discrepancy":
                            sb.text("パスワードが違います")
        elif ra == "サインアップ":
            #メール
            mail = sb.text_input("メールアドレス",help="nakaji@studio-nakaji.com")
            #パスワード
            pw = str(sb.text_input("パスワード",type="password"))
            #姓名
            family, first = sb.columns(2)
            family_name = family.text_input("姓",placeholder="中島",help="請求書の宛名に使用します")
            first_name = first.text_input("名",placeholder="理")
            full_name = family_name + " " + first_name
            #Biz内名称
            bizName = sb.text_input("Biz内名称",placeholder="ナカジ")
            #電話番号
            tel_1,tel_2,tel_3 = sb.columns(3)
            tel_1_num = tel_1.text_input("電話番号",placeholder="090")
            tel_2_num = tel_2.text_input("",placeholder="6810")
            tel_3_num = tel_3.text_input("",placeholder="1592")
            tel = str(tel_1_num)+"-"+str(tel_2_num)+"-"+str(tel_3_num)
            #郵便番号
            post_1,post_2 = sb.columns(2)
            post_1_num = post_1.text_input("郵便番号",placeholder="180")
            post_2_num = post_2.text_input("",placeholder="0014")
            postCode = str(post_1_num + "-" + post_2_num)
            #都道府県
            prefectures_list = [row[0] for row in csv.reader(open("_csv/prefectures_code.csv","r"))]
            prefectures = sb.selectbox("都道府県",prefectures_list)
            #以降の住所
            address = sb.text_input("以降の住所",help="建物名・部屋番号まで入力して下さい")
            #銀行口座情報
            bankNumber = sb.text("銀行口座情報(登録者と別名義の口座もOK)")
            #銀行名
            bank_dic = {row[0]:row[1] for row in csv.reader(open("_csv/bank_code.csv","r"))}
            bankCode = bank_dic[sb.selectbox("銀行名",bank_dic.keys())]
            branchCode = str(sb.text_input("支店コード"))
            #口座科目
            bankSubject = sb.selectbox("科目",["普通","当座"])
            #口座番号
            bankNumber = str(sb.text_input("口座番号"))
            #口座名義
            bankNumber = sb.text("口座名義")
            bank_family, bank_first = sb.columns(2)
            bank_family_name = bank_family.text_input("姓")
            bank_first_name = bank_first.text_input("名")
            bank_full_name = str(bank_family_name + " " + bank_first_name)
            #口座名義カナ
            bank_kana_name = str(sb.text_input("口座名義(カナ)"))
            #サインアップボタン
            sign_up_button = sb.button("サインアップ")
            sb.text("")
            if sign_up_button:
                checkes = [mail, pw, full_name, bizName, tel, postCode, prefectures, address, bankCode, branchCode, bankSubject, bankNumber, bank_full_name, bank_kana_name]
                if "" in checkes:
                    sb.text("情報が不足しています")
                else:
                    pw = make_hashes(pw)
                    post_data = {"type":"sign_up","mail":mail,"password":pw,"full_name":full_name,"bizName":bizName,"tel":tel,"postCode":postCode,"prefectures":prefectures,"address":address,"bankCode":bankCode,"branchCode":branchCode,"bankSubject":bankSubject,"bankNumber":bankNumber,"bankName":bank_full_name,"bankKanaName":bank_kana_name}
                    print(f"Post data =>{post_data}")
                    event_time_r = requests.post(api_url,data= json.dumps(post_data).encode('utf-8'))
                    data = json.loads(event_time_r.text)
                    print(f"Return data =>{data}")
                    sb.text(post_data)
                    print(datetime.now())
                    if data["login"]:
                        login_info(data)    #"login_info"ステートに情報を渡す
                        if st.session_state["login_info"] == {"login":False}:
                            st.session_state["login_info"].update(data)
                        if data["status"] == "register":
                            sb.text("アカウントを新規作成しました")
                        elif data["status"] == "done":
                            sb.text("アカウントは登録済みです")
                    else:
                        if data["data"] == "No Password":
                            sb.text("入力されたメールアドレスにはパスワードが設定されていません")
                            sb.text("パスワードを記入しました")
                        elif data["data"] == "Discrepancy":
                            st.text("パスワードが違います")
    return

def main():
    login_page ()
    
    if st.session_state["login_info"]["login"]:
        st.text(f'{st.session_state["login_info"]["data"]["氏名"]}様　いつもお疲れ様です！')
        get_work_time_app_v1_0_1.main_(st.session_state["login_info"]["data"])
    
    else:
        st.text("ログインして下さい")
        


if __name__ == '__main__':
    main()