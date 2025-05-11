from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import pytz

def convert_utc_to_kst(utc_time):
    return utc_time + timedelta(hours=9)

def get_kbo_games(page):
    page.wait_for_selector("li.game-cont", timeout=15000)
    html = page.content()
    soup = BeautifulSoup(html, "html.parser")
    games = soup.select("li.game-cont")
    result = []

    for game in games:
        status = game.select_one("p.staus")
        away = game.select_one("div.team.away img")
        home = game.select_one("div.team.home img")
        score_away = game.select_one("div.team.away .score")
        score_home = game.select_one("div.team.home .score")

        if not (away and home and status):
            continue

        away_name = away.get("alt", "원정")
        home_name = home.get("alt", "홈")
        away_score = score_away.text.strip() if score_away else "vs"
        home_score = score_home.text.strip() if score_home else "vs"
        game_status = status.text.strip()

        line = f"{away_name} {away_score} : {home_score} {home_name} - 상태: {game_status}"
        result.append(line)

    return result

def crawl_kbo_yesterday_today():
    utc_time = datetime.now(pytz.utc)
    kst_time = convert_utc_to_kst(utc_time)
    today = kst_time.date()
    yesterday = today - timedelta(days=1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 테스트 시 False
        page = browser.new_page()
        page.goto("https://www.koreabaseball.com/Schedule/GameCenter/Main.aspx")

        # 어제로 이동
        page.wait_for_selector("li.prev", timeout=10000)
        page.click("li.prev")
        page.wait_for_timeout(3000)
        games_yesterday = get_kbo_games(page)

        # 오늘로 복귀
        page.wait_for_selector("li.next", timeout=10000)
        page.click("li.next")
        page.wait_for_timeout(3000)
        games_today = get_kbo_games(page)

        browser.close()

    output = {
        "games": {
            str(yesterday): games_yesterday,
            str(today): games_today
        },
        "last_updated": kst_time.strftime("%Y-%m-%d %H:%M:%S")
    }

    with open("today_games.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("✅ today_games.json 생성 완료")
    print(f"📆 날짜별 경기 수: {len(games_yesterday)} (어제), {len(games_today)} (오늘)")
    print(f"🕒 마지막 업데이트: {output['last_updated']}")

if __name__ == "__main__":
    crawl_kbo_yesterday_today()
