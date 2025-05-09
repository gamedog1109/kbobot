# today_games.py
import pandas as pd
from datetime import datetime, timedelta
import json

def get_today_game_info():
    try:
        # CSV 불러오기 및 날짜 정리
        df = pd.read_csv("KBO_2025_May_to_August.csv")
        df["date"] = pd.to_datetime(df["date"]).dt.date

        # 팬 정보 불러오기
        with open("fans.json", "r", encoding="utf-8") as f:
            fans = json.load(f)

        # KST 기준 오늘 날짜
        kst_now = datetime.utcnow() + timedelta(hours=9)
        today = kst_now.date()

        # 오늘 경기 필터링
        df_today = df[df["date"] == today]

        if df_today.empty:
            return f"📅 오늘({today})은 예정된 경기가 없습니다."

        result = [f"📅 오늘({today}) KBO 경기 일정\n"]
        for _, row in df_today.iterrows():
            home, away, stadium = row["home_team"], row["away_team"], row["stadium"]
            home_fans = [n for n, t in fans.items() if t == home]
            away_fans = [n for n, t in fans.items() if t == away]

            line = f"- {home} vs {away} @ {stadium}"
            if home_fans and away_fans:
                line += f"\n  🙌 {' & '.join(home_fans)}님 vs {' & '.join(away_fans)}님 → 찬조금 납부 시리즈 빅매치🔥"
            elif home_fans:
                line += f"\n  😌 {' & '.join(home_fans)}님 응원 중… 찬조금 없는 매치"
            elif away_fans:
                line += f"\n  😌 {' & '.join(away_fans)}님 응원 중… 찬조금 없는 매치"
            else:
                line += f"\n  😶 팬 없음. 관심 無 경기!"
            result.append(line)
        
        return "\n\n".join(result)

    except Exception as e:
        return f"⚠️ 오류 발생: {str(e)}"
