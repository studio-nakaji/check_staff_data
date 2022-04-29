import streamlit as st
from access_sheets_dir import access_sheets as sh
import pandas as pd
import datetime

"""
### Nスタアプリ
## 作業料チェックシート
"""

def color_add(val):
    return f"color:#2aa3b1"

def main():
    SPREADSHEET_KEY = '1fH75awI6NAOjUGoiuZlD4YsNs1cnXcyLA9wsJmNP5Lg'    #「背景スケジュールまとめ」スプレッドシート

    title_list = sh.get_sheets_name(SPREADSHEET_KEY)
    # title_list = ['作品リスト', 'Tv_シキザクラ', 'Co_シキザクラ版権', 'Tv_シキザクラ#特典映像', 'Tv_すずめの戸締まり#A']
    title = st.selectbox(label="シートを選択" ,options= title_list)
    if title == "":
        st.stop()
    left_col,right_col = st.columns(2)
    member = sh.get_member(SPREADSHEET_KEY,title)
    worker = left_col.selectbox("スタッフを選択",member)
    today = datetime.datetime.today()
    default_month = today.month-1
    if today.day<10:
        default_month = default_month-1
    if default_month <= 0:
        default_month = 1
    month = right_col.selectbox("取得する月を選択",range(1,13),index=default_month)
    if worker == "" or month == "":
        st.stop()

    if st.button("取得"):
        st.write(f"{worker}さんの{month}月分の報酬金額は・・・")
        new_df, reward_df = sh.main(SPREADSHEET_KEY,title,worker,month)
        # new_df = new_df.set_index("Cut番号",drop=True)
        if type(new_df)== pd.core.frame.DataFrame:
            st.table(new_df.style.applymap(color_add,subset=["報酬金額"]))
            st.table(reward_df.style.applymap(color_add,subset=["支払い金額"]))
            sum_df = new_df.join(reward_df)
            sum_df = sum_df.fillna("")
            # st.table(sum_df)
            csv = sum_df.to_csv().encode('utf-8')
            st.download_button(
                "ダウンロード",
                csv,
                f"Nスタ_{worker}様:{month}月分明細.csv",
                "text/csv",
                key="download-csv"
            )
        else:
            f"おや？{month}月は作業されてないようですね。"


if __name__ == "__main__":
    main()


