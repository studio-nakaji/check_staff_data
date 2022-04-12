import streamlit as st
import get_cal_report
import datetime as dt
from datetime import timedelta
import jpholiday
import calendar as cal

def check_holiday(day):
    if day.weekday() >= 5 or jpholiday.is_holiday(day):
        return 0
    else:
        return 1

def daterange(_start, _end):
    for n in range((_end - _start).days):
        yield _start + timedelta(n)

st.title("Nstudio App")

left_column,right_column = st.columns(2)
today = dt.date.today()
year = today.year

select_y = left_column.selectbox(
    "取得したい年",
    list(range(year-3,year+1))
)
select_m = right_column.selectbox(
    "取得したい月",
    list(range(1,13))
)
#今月の残り日数を取得
last_day_num = cal.monthrange(year,today.month)[1]
last_day = dt.date(year,today.month,last_day_num)
remaining_days = 0
for i in daterange(today, last_day):
    remaining_days += check_holiday(i)
remaining_days += check_holiday(last_day)

work_dic = get_cal_report.get_gcal_main(select_y,select_m)
button = st.button("舞ちゃんの作業時間を表示")
left_column, right_column = st.columns(2)
max_hour=64
if button:
    if work_dic != None:
        # all = sum(work_dic.values())
        count_hour =0
        for i in work_dic:
            if "予定" not in i:
                left_column.write(f"[{i}]を")
                right_column.write(f"{work_dic[i]}時間作業")
                count_hour += work_dic[i]
            else:
                left_column.write(f"[{i}]が")
                right_column.write(f"{work_dic[i]}時間")
                
        left_column.write(f"合計{count_hour}時間作業されましたね。")
        if today.month == select_m:
            if count_hour < max_hour:
                remaining_hour = max_hour-count_hour   #残り日数*8時間　>　残りの時間なら
                if remaining_days*8 > remaining_hour:
                    st.write(f"目標の{max_hour}勤務時間まであと{remaining_hour}時間です。")
                    st.write(f"今月の平日は残り{remaining_days}日です。1日{round(remaining_hour/remaining_days,1)}時間作業する計算ですね。頑張りましょう！")
            elif count_hour < max_hour+10:
                st.write(f"目標の時間を{count_hour-max_hour}時間超えているようです。頑張ってるんですね！")
            else:
                st.write(f"もう目標の時間を{count_hour-max_hour}時間超えて働いていますよ！休まれては？")
    else:
        left_column.write("指定の期間中にはデータがありません")
# for v in work_dic.values():
    
#     st.write(v)
# expander = left_column.expander("問い合わせ")
# expander.write("内容のテスト")