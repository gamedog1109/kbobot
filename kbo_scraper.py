import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def get_today_kbo_results():
    today = datetime.today().strftime('%Y%m%d')
    url = f"https://sports.news.naver.com/kbaseball/schedule/index?date={today}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    game_rows = soup.select(".sch_tb .tb_wrap > table tbody tr")

    result = f"[{datetime.today().strftime('%m월 %d일')} KBO 경기 결과]\n\n"
    game_count = 0

    for row in game_rows:
        teams = row.select("td.team")
        score = row.select_one("td.score")
        stadium = row.select_one("td.place")

        if teams and score and stadium:
            home = teams[0].text.strip()
            away = teams[1].text.strip()
            score_text = score.text.strip()
            stadium_name = stadium.text.strip()
            result += f"- {home} {score_text} {away} ({stadium_name})\n"
            game_count += 1

    if game_count == 0:
        result += "오늘은 KBO 경기가 없습니다. 후훗..\n"

    return result


def get_recent_series_games(days=4):
    all_games = []

    for i in range(days):
        day = datetime.today() - timedelta(days=i)
        date_str = day.strftime('%Y%m%d')
        url = f"https://sports.news.naver.com/kbaseball/schedule/index?date={date_str}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        game_rows = soup.select(".sch_tb .tb_wrap > table tbody tr")

        for row in game_rows:
            teams = row.select("td.team")
            score = row.select_one("td.score")
            stadium = row.select_one("td.place")

            if teams and score and stadium:
                home = teams[0].text.strip()
                away = teams[1].text.strip()
                score_text = score.text.strip()
                stadium_name = stadium.text.strip()

                # 점수 정제
                if ":" in score_text:
                    home_score, away_score = map(int, score_text.split(":"))
                    all_games.append({
                        "home": home,
                        "away": away,
                        "home_score": home_score,
                        "away_score": away_score,
                        "stadium": stadium_name,
                        "date": date_str
                    })

    # 같은 팀끼리 3경기 이상한 시리즈만 필터링
    from collections import defaultdict
    matchups = defaultdict(list)

    for g in all_games:
        key = tuple(sorted([g["home"], g["away"]]))
        matchups[key].append(g)

    result = []
    for games in matchups.values():
        if len(games) >= 3:
            result.extend(games)

    return result


def get_next_week_games():
    from datetime import datetime, timedelta

    games = []

    for i in range(7):
        target_date = datetime.today() + timedelta(days=i)
        date_str = target_date.strftime('%Y%m%d')
        url = f"https://sports.news.naver.com/kbaseball/schedule/index?date={date_str}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        game_rows = soup.select(".sch_tb .tb_wrap > table tbody tr")

        for row in game_rows:
            teams = row.select("td.team")
            stadium = row.select_one("td.place")

            if teams and stadium:
                home = teams[0].text.strip()
                away = teams[1].text.strip()
                stadium_name = stadium.text.strip()

                games.append({
                    "date": target_date.strftime('%Y-%m-%d'),
                    "home": home,
                    "away": away,
                    "stadium": stadium_name
                })

    return games


def get_kbo_rankings():
    url = "https://sports.news.naver.com/kbaseball/record/index?category=kbo"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    table = soup.select_one(".tbl_box")
    rows = table.select("tbody tr")

    result = "📊 KBO 순위표\n\n"
    result += "순위 팀  승-패-무  승률  게임차\n"

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 6:
            rank = cols[0].text.strip()
            team = cols[1].text.strip()
            record = cols[2].text.strip()
            win_rate = cols[3].text.strip()
            gap = cols[5].text.strip()

            result += f"{rank}. {team} {record}  {win_rate}  {gap}\n"

    return result.strip()


