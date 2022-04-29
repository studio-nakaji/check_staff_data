import streamlit as st
import streamlit_app
from access_sheets import access_bg_sheet_app
import secont_page


def main():
    contents = {"作業時間の取得":streamlit_app,"作業料金csvの取得":access_bg_sheet_app}
    st.sidebar.title("アプリを選択")
    selection = st.sidebar.radio("Go to",list(contents.keys()))
    page = contents[selection]
    page.main()



if __name__ == '__main__':
    main()