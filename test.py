import requests
from datetime import datetime

def get_kbo_results_by_json_api(date="2025-05-05"):
    date_param = date.replace("-", "")
    url = f"https://sports.news.naver.com/ajax/schedule/schedule.json?date={date_param}&league=KBO"
    headers = {"User-Agent": "Mozilla/5.0"}

    res = requests.get(url, headers=headers)
    data = res.json()

    result = f"[{datetime.strptime(date, '%Y-%m-%d').strftime('%m월 %d일')} KBO 경기 결과]\n\n"
    count = 0

    for game in data.get("todaySchedule", []):
        if game.get("status") == "종료":
            home = game["homeTeamName"]
            away = game["awayTeamName"]
            home_score = game["homeScore"]
            away_score = game["awayScore"]
            stadium = game["stadiumName"]
            result += f"- {home} {home_score}:{away_score} {away} ({stadium})\n"
            count += 1

    if count == 0:
        result += "📭 오늘은 경기가 없거나 아직 시작 전입니다."

    return result.strip()
