import json
import requests

from flask import Flask, request, jsonify
from today_games import get_today_game_info
from kbo_weather_checker import build_weather_message
from next_series import get_next_series_info
import re
from flask import Flask, jsonify
import os


app = Flask(__name__)

# GitHub Pages에 JSON 파일이 업로드된 주소로 바꿔주세요
JSON_URL = "https://gamedog1109.github.io/kbobot/today_games.json"


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        res = requests.get(JSON_URL, timeout=5)
        data = res.json()
        games = data.get("games", [])
        last_updated = data.get("last_updated", "")

        if not games:
            message = "⚠️ 현재 중계 중인 경기가 없습니다."
        else:
            message = "\n\n".join(games) + f"\n\n🕒 마지막 업데이트: {last_updated}"

    except Exception as e:
        message = "❌ 경기 정보를 불러오는 중 오류가 발생했습니다."

    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [{
                "simpleText": {
                    "text": message
                }
            }]
        }
    })

@app.route("/games_today", methods=["POST"])
def show_today_games():
    message = get_today_game_info()
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [{
                "simpleText": {"text": message}
            }]
        }
    })

@app.route("/weather_today", methods=["POST"])
def show_weather_today():
    message = build_weather_message()
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [{
                "simpleText": {
                    "text": message
                }
            }]
        }
    })

@app.route("/next_series", methods=["POST"])
def show_next_series():
    message = get_next_series_info()
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [{
                "simpleText": {"text": message}
            }]
        }
    })




@app.route("/fan_message", methods=["POST"])
def fan_message():
    try:
        with open('fans.json', 'r', encoding='utf-8') as f:
            fan_data = json.load(f)  # {이름: 팀}
        with open('today_games.json', 'r', encoding='utf-8') as f:
            game_data = json.load(f)

        games = game_data.get("games", [])
        messages = []
        fan_team_map = {v: k for k, v in fan_data.items()}  # {팀: 이름}

        for game in games:
            try:
                parts, status_raw = game.split(" - ")
                status = status_raw.strip().replace("상태:", "").strip()

                team1, score1, score2, team2 = re.match(r"(.*) (\d+) : (\d+) (.*)", parts).groups()
                score1, score2 = int(score1), int(score2)
                score_line = f"{team1} {score1} : {score2} {team2}"

                team1_is_fan = team1 in fan_team_map
                team2_is_fan = team2 in fan_team_map

                if team1_is_fan and team2_is_fan:
                    # 팬끼리 맞붙음
                    if score1 > score2:
                        messages.append(f"🎉 {fan_team_map[team1]}님 축하합니다! {team1}이 {team2}에게 승리했습니다. ({score_line})")
                    elif score2 > score1:
                        messages.append(f"🎉 {fan_team_map[team2]}님 축하합니다! {team2}이 {team1}에게 승리했습니다. ({score_line})")
                    else:
                        messages.append(f"⚖️ {fan_team_map[team1]}님과 {fan_team_map[team2]}님, {team1}과 {team2}가 비기고 있어요. ({score_line})")

                elif team1_is_fan or team2_is_fan:
                    team = team1 if team1_is_fan else team2
                    opp = team2 if team1_is_fan else team1
                    fan_name = fan_team_map[team]
                    team_score = score1 if team1_is_fan else score2
                    opp_score = score2 if team1_is_fan else score1

                    if team_score > opp_score:
                        if "경기종료" in status:
                            messages.append(f"🎉 {fan_name}님 축하합니다! {team}이 {opp}에게 승리했습니다. ({score_line})")
                        else:
                            messages.append(f"🔥 {fan_name}님, {team}이 {opp}를 상대로 이기고 있습니다. ({score_line})")
                    elif team_score < opp_score:
                        if "경기종료" in status:
                            messages.append(f"😢 {fan_name}님 아쉽습니다. {team}이 {opp}에게 패배했습니다. ({score_line})")
                        else:
                            messages.append(f"😓 {fan_name}님, {team}이 {opp}에게 지고 있습니다. ({score_line})")
                    else:
                        messages.append(f"⚖️ {fan_name}님, {team}이 {opp}와 비기고 있습니다. ({score_line})")

                else:
                    messages.append(f"💤 {team1} vs {team2} — 노잼 경기입니다 👀 ({score_line})")

            except:
                messages.append(f"⚠️ 경기 정보 해석 실패: {game}")

        result_text = "📡 [실시간 중계 안내]\n\n" + "\n".join(messages)

        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [{
                    "simpleText": {"text": result_text}
                }]
            }
        })

    except Exception as e:
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [{
                    "simpleText": {"text": f"❌ 오류 발생: {str(e)}"}
                }]
            }
        })













@app.route("/")
def index():
    return "✅ KBO 챗봇 서버 정상 실행 중!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
