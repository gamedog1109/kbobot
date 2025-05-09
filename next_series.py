import pandas as pd
from datetime import datetime, timedelta
import json

def get_next_series_info(csv_path="KBO_2025_May_to_August.csv"):
    try:
        # 날짜 포맷팅
        df = pd.read_csv(csv_path)
        df["date"] = pd.to_datetime(df["date"]).dt.date

        with open("fans.json", "r", encoding="utf-8") as f:
            fans = json.load(f)

        # 오늘(KST)
        today = (datetime.utcnow() + timedelta(hours=9)).date()

        # 내일 이후 경기 중 가장 빠른 날짜 탐색
        upcoming = df[df["date"] > today].sort_values("date")
        if upcoming.empty:
            return "📅 다음 예정된 KBO 시리즈가 없습니다."

        next_date = upcoming.iloc[0]["date"]
        next_series = df[df["date"] == next_date]

        output = [f"📢 다음 KBO 시리즈 개막 안내 ({next_date})\n"]

        for _, row in next_series.iterrows():
            home, away, stadium = row["home_team"], row["away_team"], row["stadium"]
            home_fans = [name for name, team in fans.items() if team == home]
            away_fans = [name for name, team in fans.items() if team == away]

            line = f"🏟️ {stadium}\n🆚 {home} vs {away}"

            if home_fans and away_fans:
                line += f"\n🙌 {', '.join(home_fans)} vs {', '.join(away_fans)} → 찬조금 대결 예고🔥"
            elif home_fans:
                line += f"\n😌 {', '.join(home_fans)}님 응원 중 – 찬조금 없음"
            elif away_fans:
                line += f"\n😌 {', '.join(away_fans)}님 응원 중 – 찬조금 없음"
            else:
                line += "\n😶 팬 없음 – 무관심 시리즈"

            output.append(line)

        return "\n\n".join(output)

    except Exception as e:
        return f"⚠️ 오류 발생: {str(e)}"
