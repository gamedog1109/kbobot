import json
from collections import defaultdict

# 팬 정보 불러오기
def load_fans():
    with open("fans.json", "r", encoding="utf-8") as f:
        return json.load(f)

# 시리즈 결과 분석
def analyze_series(games: list):
    """
    games: [
        {"home": "LG", "away": "두산", "home_score": 5, "away_score": 3, "stadium": "잠실"},
        ...
    ]
    """
    result_summary = ""
    fan_penalty = []

    # 시리즈별 승리 수 계산
    matchup = defaultdict(lambda: {"home": 0, "away": 0, "games": []})

    for game in games:
        key = tuple(sorted([game["home"], game["away"]]))
        data = matchup[key]
        data["games"].append(game)

        if game["home_score"] > game["away_score"]:
            data["home"] += 1
        elif game["away_score"] > game["home_score"]:
            data["away"] += 1
        # 무승부는 생략

    fans = load_fans()

    for teams, data in matchup.items():
        team1, team2 = teams
        games = data["games"]
        result_summary += f"\n[{team1} vs {team2} 시리즈 결과]\n"
        for g in games:
            result_summary += f"- {g['home']} {g['home_score']} : {g['away_score']} {g['away']} ({g['stadium']})\n"

        home_wins = data["home"]
        away_wins = data["away"]

        if home_wins + away_wins < 2:
            result_summary += "→ 시리즈 미완료 또는 무효\n"
            continue

        winner = None
        loser = None
        penalty = 0
        summary = ""

        if home_wins == 2:
            winner = games[0]["home"]
            loser = games[0]["away"]
            penalty = 5000
            summary = "위닝 시리즈"
        elif away_wins == 2:
            winner = games[0]["away"]
            loser = games[0]["home"]
            penalty = 5000
            summary = "위닝 시리즈"
        if home_wins == 3:
            winner = games[0]["home"]
            loser = games[0]["away"]
            penalty = 10000
            summary = "스윕 시리즈"
        elif away_wins == 3:
            winner = games[0]["away"]
            loser = games[0]["home"]
            penalty = 10000
            summary = "스윕 시리즈"

        if winner:
            result_summary += f"→ {winner} {summary}\n"
            for name, team in fans.items():
                if team == winner and loser in fans.values():
                    fan_penalty.append((name, penalty))

    return result_summary, fan_penalty
