from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import os
from traceback import format_exc

def get_live_scores():
    try:
        fan_data = {}
        if os.path.exists("fans.json"):
            with open("fans.json", "r", encoding="utf-8") as f:
                fan_data = json.load(f)

        team_to_fans = {}
        for fan, team in fan_data.items():
            team_to_fans.setdefault(team, []).append(fan)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://www.koreabaseball.com/Schedule/GameCenter/Main.aspx")
            page.wait_for_selector("li.game-cont", timeout=10000)
            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, "html.parser")
        games = soup.select("li.game-cont")
        if not games:
            return "📡 현재 중계 중인 경기가 없습니다."

        result = []
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
            away_score = int(score_away.text.strip())
            home_score = int(score_home.text.strip())
            game_status = status.text.strip()

            cheer_msg = ""
            if away_score == home_score:
                fans = team_to_fans.get(away_name, []) + team_to_fans.get(home_name, [])
                if fans:
                    fan_str = ", ".join(f"{n}님" for n in fans)
                    cheer_msg = f"\n{fan_str} 두 팀 팬들 모두 조마조마하시겠어요 🤔"
            else:
                win_team = away_name if away_score > home_score else home_name
                lose_team = home_name if away_score > home_score else away_name
                if win_team in team_to_fans:
                    cheer_msg += f" ({', '.join(f'{n}님' for n in team_to_fans[win_team])} 기분 좋으시겠어요 😊)"
                if lose_team in team_to_fans:
                    cheer_msg += f"\n{', '.join(f'{n}님' for n in team_to_fans[lose_team])} 힘내세요... 🥲"

            line = f"{away_name} {away_score} : {home_score} {home_name} - 상태: {game_status}{cheer_msg}"
            result.append(line)

        return "\n\n".join(result)

    except Exception as e:
        print("❌ Playwright 예외 발생:", format_exc())
        return "❌ 경기 정보를 불러오는 중 서버 오류가 발생했습니다."