from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
from datetime import datetime

def crawl_kbo_games():
    with sync_playwright() as p:
        # headless=True로 설정하면 창 없이 백그라운드에서 실행됩니다
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.koreabaseball.com/Schedule/GameCenter/Main.aspx")
        page.wait_for_selector("li.game-cont", timeout=10000)  # 경기 목록이 로딩될 때까지 기다림
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    games = soup.select("li.game-cont")
    result = []

    # 게임 정보 파싱
    for game in games:
        status = game.select_one("p.staus")
        away = game.select_one("div.team.away img")
        home = game.select_one("div.team.home img")
        score_away = game.select_one("div.team.away .score")
        score_home = game.select_one("div.team.home .score")

        if not (away and home and score_away and score_home and status):
            continue

        away_name = away.get("alt", "원정")
        home_name = home.get("alt", "홈")
        away_score = score_away.text.strip()
        home_score = score_home.text.strip()
        game_status = status.text.strip()

        line = f"{away_name} {away_score} : {home_score} {home_name} - 상태: {game_status}"
        result.append(line)

    # JSON 파일로 저장
    output = {
        "games": result,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open("today_games.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("✅ today_games.json 파일 생성 완료")
    print(f"❗ 마지막 업데이트: {output['last_updated']}")

if __name__ == "__main__":
    crawl_kbo_games()
