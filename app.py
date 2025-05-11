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
            fan_data = json.load(f)
        with open('today_games.json', 'r', encoding='utf-8') as f:
            game_data = json.load(f)

        games = game_data.get("games", [])
        messages = []

        for name, team in fan_data.items():
            found = False
            for game in games:
                if team in game:
                    found = True
                    try:
                        parts, status_raw = game.split(" - ")
                        status = status_raw.strip().replace("상태:", "").strip()

                        team1, score1, score2, team2 = re.match(r"(.*) (\d+) : (\d+) (.*)", parts).groups()
                        score1 = int(score1)
                        score2 = int(score2)

                        # 응원팀이 어느 쪽인지 판단
                        if team == team1:
                            team_score, opp_score, opponent = score1, score2, team2
                            score_line = f"{team1} {score1} : {score2} {team2}"
                        elif team == team2:
                            team_score, opp_score, opponent = score2, score1, team1
                            score_line = f"{team1} {score1} : {score2} {team2}"
                        else:
                            continue

                        # 이기고 있을 때만 메시지 출력
                        if team_score > opp_score:
                            if "경기종료" in status:
                                msg = f"🎉 {name}님 축하합니다! {team}이 {opponent}에게 승리했습니다. ({score_line})"
                            elif "회" in status or "중" in status:
                                msg = f"🔥 {name}님, {team}이 {opponent}를 상대로 이기고 있습니다. ({score_line})"
                            else:
                                msg = f"ℹ️ {name}님, {team} 경기 상태: {status} (점수: {score_line})"
                            messages.append(msg)
                        # 지거나 비긴 경우는 무시
                    except:
                        messages.append(f"⚠️ {name}님, {team} 경기 정보 해석 실패")
                    break
            if not found:
                messages.append(f"ℹ️ {name}님, {team}은 오늘 경기 중이 아닙니다.")
        
        result_text = "\n".join(messages)

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
