import streamlit as st
import datetime
import jpholiday
import calendar as cal
import time
import requests
import json

def check_holiday(day):
    if day.weekday() >= 5 or jpholiday.is_holiday(day):
        return 0
    else:
        return 1

def daterange(_start, _end):
    for n in range((_end - _start).days):
        yield _start + datetime.timedelta(n)


def get_events_time_gas(data, today):
    # 指定月のイベントの開始・終了・タイトルを出力します
    work_dic = {}
    for key in list(data):
        event = data[key]
        event_day = datetime.datetime.strptime(key, "%Y/%m/%d_%H:%M").date()
        if event_day <= today:  #今日以前のもののみ処理
            title = event['title']
            wark_time = event["time"]
            if wark_time<8: #8時間以下の予定のみ処理
                if title not in work_dic:      #辞書内に同様の作業がなければ
                    work_dic[title]=wark_time  #辞書に追加
                else:                               #なければ
                    work_dic[title]=work_dic[title]+wark_time #労働時間を加算
    return work_dic

def main_(staff_data):
    g_cal_id = cache_gcal_id(staff_data["G-cal_ID"])

    st.title("Nスタアプリ")
    
    ex1 = st.expander("一覧を取得",expanded=True)
    today = datetime.date.today()
    year = today.year

    select_y = ex1.selectbox(
        "取得したい年",
        list(range(2022,year+1))
    )
    select_m = ex1.selectbox(
        "取得したい月",
        list(range(1,13))
    )
    #今月の残り日数を取得
    last_day_num = cal.monthrange(year,today.month)[1]
    last_day = datetime.date(year,today.month,last_day_num)
    remaining_days = 0
    for i in daterange(today, last_day):
        remaining_days += check_holiday(i)
    remaining_days += check_holiday(last_day)

    work_dic = cache_dic()
    work_dic.clear()
    
    #カレンダー情報の取得
    cal_url = "https://script.google.com/macros/s/AKfycbzjcYPypWS_HzvPb383Ydp6xFToVwYmu5O3QBs12n65p6_8Ww9nCO5Vx0deLxDkroA/exec"

    year = 2022
    month = 7
    today = datetime.date.today()
    
    ##Gasでの取得
    cal_post_data = {"id":g_cal_id,"year":select_y,"month":select_m}
    event_time_r = requests.post(cal_url,data= json.dumps(cal_post_data).encode('utf-8'))
    #返り値：{"title":summary,"time":diff, "start":start, "end":end, "date":date}{タイトル,作業時間,開始時間,終了時間,日付}
    event_time_data = json.loads(event_time_r.text)
    work_dic = get_events_time_gas(event_time_data, today)
    
    max_hour=64
    column_1, column_2 = ex1.columns(2)
    if len(list(work_dic))>0:
        if work_dic != None:                #イベントが存在したら
            count_hour =0
            for i in work_dic:
                if "予定" not in i:
                    column_1.write(f"{i}")
                    column_2.write(f"{work_dic[i]}　時間作業")
                    count_hour += work_dic[i]
                else:
                    column_1.write(f"{i}")
                    column_2.write(f"{work_dic[i]}　時間")
            count_hour = round(count_hour,1)
            #作業時間/目標時間をプログレスバーで表示
            bar = ex1.progress(0)
            wariai = round(count_hour/max_hour*100)
            if wariai < 100:
                for i in range(wariai):
                    time.sleep(0.005)
                    bar.progress(round(i+1))
            else:
                for i in range(100):
                    time.sleep(0.003)
                    bar.progress(round(i+1))
            time.sleep(0.05)
            if today.month == select_m:
                ex1.write(f"今月は{count_hour}時間作業されたのですね！")
                ex1.write("")
                if count_hour < max_hour:                   #作業時間が目標以下の時
                    remaining_hour = round(max_hour-count_hour,1)    #残り日数*8時間　>　残りの時間なら
                    if remaining_days*8 > remaining_hour:
                        ex1.write(f"目標の{max_hour}時間まであと{remaining_hour}時間です。")
                        ex1.write(f"今月の平日はあと{remaining_days}日なので・・・、")
                        ex1.write(f"1日{round(remaining_hour/remaining_days,1)}時間作業すれば達成ということですね！　頑張っていきましょう！")
                    else:
                        ex1.write(f"目標の{max_hour}時間まであと{remaining_hour}時間です。")
                        ex1.write(f"今月の平日はあと{remaining_days}日。{round(remaining_hour/remaining_days,1)}時間/1日作業。大変ですね。。")
                elif count_hour < max_hour+10:              #作業時間が目標+10時間以内の時
                    ex1.write(f"目標の時間を{round(count_hour-max_hour,1)}時間超えているようです。頑張ってるんですね！")
                else:                                       #作業時間が目標+10時間以上の時
                    ex1.write(f"もう目標の時間を{round(count_hour-max_hour,1)}時間超えて働いていますよ！休まれては？")
                
            else:
                month = select_m
                if count_hour == 0:
                    f"{month}月はご活躍されてないようですね。今後に期待しています！"
                else:
                    ex1.write(f"{month}月は{count_hour}時間作業されたのですね。")
                    ex1.write("お疲れ様でした！")
                    if count_hour < max_hour:                   #作業時間が目標以下の時
                        remaining_hour = round(max_hour-count_hour,1)    #残り日数*8時間　>　残りの時間なら
                        ex1.write(f"目標の{max_hour}時間まであと{remaining_hour}時間でした。")
                    elif count_hour < max_hour+10:              #作業時間が目標+10時間以内の時
                        ex1.write(f"目標を{round(count_hour-max_hour,1)}時間超えていたようです。頑張ったんですね！")
                    else:                                       #作業時間が目標+10時間以上の時
                        ex1.write(f"目標を{round(count_hour-max_hour,1)}時間も超えて働いたようです！身体の調子は大丈夫ですか？")
                
    else:
        st.write("おっと、指定の期間中にはデータが見当たらないようです・・・。")
    
    #2022年1月以外を選択し、かつ取得した労働項目が0以上あれば、合計時間を表示
    work_list = list(work_dic)
    selection_list = list(set([i.split("]")[0].split("[")[1] for i in work_list if "]" in i]))
    if not(select_y == 2022 and select_m == 1) and len(work_list) > 0:
        ex2 = st.expander("選択した項目の合計時間を表示")
        genre_box = ex2.checkbox("ジャンルで選択",True)
        if genre_box:
            multi_work_type = ex2.multiselect(label="ジャンルを選択",options=selection_list)
        else:
            multi_work_type = ex2.multiselect(label="予定を選択",options=work_list)
        if len(multi_work_type)>0:
            total = 0
            if genre_box:
                for s in multi_work_type:
                    title = "[" + str(s) + "]"
                    for i in list(work_dic):
                        if title in i:
                            total += work_dic[i]
            else:
                for i in multi_work_type:
                    total += work_dic[i]
            ex2.write(f"合計時間は[{total}]時間です！")
            time_money=ex2.checkbox("時給換算")
            if time_money:
                total_money=int(total*1300)
                consumption_tax = int(total_money*0.1)
                Withholding_tax = int(total_money*0.1021)
                ex2.write(f"時給合計:{total_money}+消費税:{consumption_tax}+源泉徴収税:-{Withholding_tax}")
                ex2.write(f"= 合計 {str_3digits(total_money+consumption_tax-Withholding_tax)} 分になりますね")
    return

@st.cache(allow_output_mutation=True)
def cache_dic():
    dic = {}
    return dic

@st.cache(allow_output_mutation=True)
def cache_gcal_id(data):
    gcal_id = data
    return gcal_id

def str_3digits(x):
    return "¥" + f"{int(x):,}"



if __name__ == '__main__':
    main_()