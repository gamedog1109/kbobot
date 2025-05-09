# tomorrow_games.py
import pandas as pd
from datetime import datetime, timedelta
import json

def get_tomorrow_game_info():
    try:
        df = pd.read_csv("KBO_2025_May_to_August.csv")
        df["date"] = pd.to_datetime(df["date"]).dt.date

        with open("fans.json", "r", encoding="utf-8") as f:
            fans = json.load(f)

        tomorrow = datetime.today().date() + timedelta(days=1)
        df_tomorrow = df[df["date"] == tomorrow]

        if df_tomorrow.empty:
            return f"📅 내일({tomorrow})은 예정된 경기가 없습니다."

        result = [f"📅 내일({tomorrow}) KBO 경기 일정\n"]
        for _, row in df_tomorrow.iterrows():
            home, away, stadium = row["home_team"], row["away_team"], row["stadium"]
            home_fans = [n for n, t in fans.items() if t == home]
            away_fans = [n for n, t in fans.items() if t == away]

            line = f"- {home} vs {away} @ {stadium}"
            if home_fans and away_fans:
                line += f"\n  🙌 {' & '.join(home_fans)} vs {' & '.join(away_fans)} → 찬조금 납부 예정시리즈 빅매치!!!🔥"
            elif home_fans:
                line += f"\n  😌 {' & '.join(home_fans)}만 응원 중… 찬조금은 PASS!"
            elif away_fans:
                line += f"\n  😌 {' & '.join(away_fans)}만 응원 중… 찬조금은 PASS!"
            else:
                line += f"\n  😶 팬 없음. 관심 無 경기!"
            result.append(line)
        
        return "\n\n".join(result)

    except Exception as e:
        return f"⚠️ 오류 발생: {str(e)}"
