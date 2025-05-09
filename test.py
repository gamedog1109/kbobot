import requests
from datetime import datetime

def get_today_kbo_scores():
    today = datetime.today().strftime("%Y%m%d")
    url = f"https://www.koreabaseball.com/ws/scoreboard/schedule.aspx?date={today}"
    headers = {"User-Agent": "Mozilla/5.0"}

    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return "❌ 경기 정보를 불러오지 못했습니다."

    try:
        games = res.json()
    except Exception:
        return "❌ JSON 파싱 실패. 경기 데이터 구조가 바뀌었을 수 있어요."

    if not games:
        return f"📅 오늘({today})은 예정된 경기가 없습니다."

    result = f"📊 오늘 KBO 실시간 경기 현황\n\n"
    for game in games:
        home = game.get("HomeTeamName", "홈팀")
        away = game.get("AwayTeamName", "원정팀")
        status = game.get("GameStatus", "경기 상태")
        home_score = game.get("HomeScore", "?")
        away_score = game.get("AwayScore", "?")
        result += f"{home} {home_score} : {away_score} {away} ({status})\n"

    return result.strip()
