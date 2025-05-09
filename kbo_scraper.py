import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_today_kbo_results():
    date = "2025-05-05"
    url = f"https://sports.news.naver.com/kbaseball/schedule/index?date={date}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    game_rows = soup.select(".sch_tb .tb_wrap > table tbody tr")
    result = f"[{datetime.today().strftime('%m월 %d일')} KBO 경기 결과]\n\n"
    count = 0

    for row in game_rows:
        teams = row.select("td.team")
        score = row.select_one("td.score")
        stadium = row.select_one("td.place")

        if teams and score and ":" in score.text and stadium:
            home = teams[0].text.strip()
            away = teams[1].text.strip()
            score_text = score.text.strip()
            stadium_name = stadium.text.strip()
            result += f"- {home} {score_text} {away} ({stadium_name})\n"
            count += 1

    if count == 0:
        result += "아직은 KBO 경기를 시작하지 않았습니다. 아마도요??"

    return result.strip()
