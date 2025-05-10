import requests
from bs4 import BeautifulSoup
import json

def get_live_scores():
    try:
        with open("fans.json", "r", encoding="utf-8") as f:
            fan_data = json.load(f)  # { "뉴비": "LG", "제이": "한화" }

        team_to_fans = {}
        for fan, team in fan_data.items():
            team_to_fans.setdefault(team, []).append(fan)

        url = "https://www.koreabaseball.com/Schedule/GameCenter/Main.aspx"
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")

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
            if away_score > home_score:
                win_team = away_name
                lose_team = home_name
                if win_team in team_to_fans:
                    fans = ", ".join(f"{n}님" for n in team_to_fans[win_team])
                    cheer_msg += f" ({fans} 기분 좋으시겠어요 😊)"
                if lose_team in team_to_fans:
                    fans = ", ".join(f"{n}님" for n in team_to_fans[lose_team])
                    cheer_msg += f"\n{fans} 힘내세요... 🥲"
            elif home_score > away_score:
                win_team = home_name
                lose_team = away_name
                if win_team in team_to_fans:
                    fans = ", ".join(f"{n}님" for n in team_to_fans[win_team])
                    cheer_msg += f" ({fans} 기분 좋으시겠어요 😊)"
                if lose_team in team_to_fans:
                    fans = ", ".join(f"{n}님" for n in team_to_fans[lose_team])
                    cheer_msg += f"\n{fans} 힘내세요... 🥲"
            else:  # 동점
                fans = []
                if away_name in team_to_fans:
                    fans.extend(team_to_fans[away_name])
                if home_name in team_to_fans:
                    fans.extend(team_to_fans[home_name])
                if fans:
                    fan_str = ", ".join(f"{n}님" for n in fans)
                    cheer_msg = f"\n{fan_str} 두 팀 팬들 모두 조마조마하시겠어요 🤔"

            line = f"{away_name} {away_score} : {home_score} {home_name} - 상태: {game_status}{cheer_msg}"
            result.append(line)

        return "\n\n".join(result)  # 경기당 줄바꿈

    except Exception as e:
        return f"❌ 실시간 점수 가져오기 실패: {str(e)}"
