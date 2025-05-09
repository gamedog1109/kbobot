import pandas as pd
import json
from datetime import datetime, timedelta

# 📅 다음 시리즈 시작일 계산 함수
def get_next_series_start_date():
    kst_now = datetime.utcnow() + timedelta(hours=9)
    today = kst_now.date()
    weekday = today.weekday()  # 0=월, 1=화, ..., 6=일

    if weekday in [0, 1, 2]:  # 월, 화, 수 → 이번 주 금요일
        delta = (4 - weekday) % 7
    else:  # 목, 금, 토, 일 → 다음 주 화요일
        delta = (1 - weekday + 7) % 7

    return today + timedelta(days=delta)

# 🔍 다음 시리즈 정보 생성 함수
def get_next_series_info(csv_path="KBO_2025_May_to_August.csv", fans_path="fans.json"):
    try:
        df = pd.read_csv(csv_path)
        df["date"] = pd.to_datetime(df["date"]).dt.date

        with open(fans_path, "r", encoding="utf-8") as f:
            fans = json.load(f)

        start_date = get_next_series_start_date()
        end_date = start_date + timedelta(days=2)  # 시리즈는 3연전 기준

        df_series = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

        if df_series.empty:
            return f"📅 {start_date}부터 시작하는 시리즈가 없습니다."

        result = [f"📣 다음 시리즈 안내 ({start_date} ~ {end_date})\n"]

        for _, row in df_series.iterrows():
            home = row["home_team"]
            away = row["away_team"]
            stadium = row["stadium"]

            home_fans = [n for n, t in fans.items() if t == home]
            away_fans = [n for n, t in fans.items() if t == away]

            line = f"- {home} vs {away} @ {stadium}"

            if home_fans and away_fans:
                line += f"\n  🙌 {' & '.join(home_fans)}님 vs {' & '.join(away_fans)}님 → 찬조금 시리즈 빅매치🔥"
            elif home_fans:
                line += f"\n  😌 {' & '.join(home_fans)}님만 있는 경기 (무난한 경기)"
            elif away_fans:
                line += f"\n  😌 {' & '.join(away_fans)}님만 있는 경기 (무난한 경기)"
            else:
                line += "\n  😶 팬 없음. 관심 無 시리즈!"

            result.append(line)

        return "\n\n".join(result)

    except Exception as e:
        return f"⚠️ 오류 발생: {str(e)}"
