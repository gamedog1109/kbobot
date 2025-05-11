import json
import requests

from flask import Flask, request, jsonify
from today_games import get_today_game_info
from kbo_weather_checker import build_weather_message
from next_series import get_next_series_info
import re
from flask import Flask, jsonify
import os
from datetime import datetime 
from collections import defaultdict


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

        games_by_date = game_data.get("games", {})
        today_str = datetime.now().strftime("%Y-%m-%d")
        yesterday_str = sorted(games_by_date.keys())[-2] if today_str in games_by_date else sorted(games_by_date.keys())[-1]
        fan_team_map = {v: k for k, v in fan_data.items()}

        messages = [f"📡 [최근 경기 결과 안내]\n"]
        match_counter = defaultdict(int)

        for date, games in games_by_date.items():
            date_label = "🕘 어제 경기" if date == yesterday_str else "🟢 오늘 경기"
            messages.append(f"{date_label} ({date})\n")

            for game in games:
                try:
                    parts, status_raw = game.split(" - ")
                    status = status_raw.strip().replace("상태:", "").strip()
                    team_match = re.match(r"(.*) (\d+|vs) : (\d+|vs) (.*)", parts)
                    if not team_match:
                        continue

                    team1, score1_raw, score2_raw, team2 = team_match.groups()

                    # 경기 수 카운트용 키
                    matchup_key = f"{date}_{team1}_{team2}"
                    match_counter[matchup_key] += 1
                    count = match_counter[matchup_key]

                    # 총 동일 경기 수 확인
                    total_matches = sum(
                        1 for g in games
                        if re.match(rf"{re.escape(team1)} (?:\d+|vs) : (?:\d+|vs) {re.escape(team2)}", g.split(" - ")[0])
                    )

                    if count > 2:
                        continue  # DH2까지만 허용

                    dh_suffix = f" (DH{count})" if total_matches >= 2 else ""

                    team1_is_fan = team1 in fan_team_map
                    team2_is_fan = team2 in fan_team_map
                    score_line = f"{team1} {score1_raw} : {score2_raw} {team2}{dh_suffix}"

                    # 오늘 예정 경기
                    if date == today_str and "예정" in status:
                        if team1_is_fan and team2_is_fan:
                            messages.append(f"⏳ {fan_team_map[team1]}님, {fan_team_map[team2]}님\n{team1} vs {team2} 경기 예정입니다.{dh_suffix}\n")
                        elif team1_is_fan:
                            messages.append(f"⏳ {fan_team_map[team1]}님\n{team1} vs {team2} 경기 예정입니다.{dh_suffix}\n")
                        elif team2_is_fan:
                            messages.append(f"⏳ {fan_team_map[team2]}님\n{team2} vs {team1} 경기 예정입니다.{dh_suffix}\n")
                        continue

                    # 취소 경기
                    if score1_raw == "vs" or score2_raw == "vs":
                        if "예정" in status:
                            continue
                        if team1_is_fan and team2_is_fan:
                            messages.append(f"☁️ {fan_team_map[team1]}님, {fan_team_map[team2]}님\n{team1} vs {team2} 경기가 취소되었습니다.{dh_suffix}\n")
                        elif team1_is_fan:
                            messages.append(f"☁️ {fan_team_map[team1]}님,\n{team1} 경기 취소되었습니다.{dh_suffix}\n")
                        elif team2_is_fan:
                            messages.append(f"☁️ {fan_team_map[team2]}님,\n{team2} 경기 취소되었습니다.{dh_suffix}\n")
                        continue

                    score1, score2 = int(score1_raw), int(score2_raw)

                    # 어제 경기 결과
                    if date == yesterday_str:
                        if team1_is_fan and team2_is_fan:
                            if score1 > score2:
                                messages.append(f"🎉 {fan_team_map[team1]}님 축하합니다!\n{team1} 승리했습니다. 상대: {team2}{dh_suffix}\n📊 {score_line}\n")
                            elif score2 > score1:
                                messages.append(f"🎉 {fan_team_map[team2]}님 축하합니다!\n{team2} 승리했습니다. 상대: {team1}{dh_suffix}\n📊 {score_line}\n")
                        elif team1_is_fan or team2_is_fan:
                            team = team1 if team1_is_fan else team2
                            opp = team2 if team1_is_fan else team1
                            fan_name = fan_team_map[team]
                            team_score = score1 if team1_is_fan else score2
                            opp_score = score2 if team1_is_fan else score1
                            if team_score > opp_score:
                                messages.append(f"🎉 {fan_name}님 축하합니다!\n{team} 승리했습니다. 상대: {opp}{dh_suffix}\n📊 {score_line}\n")
                            elif team_score < opp_score:
                                messages.append(f"😢 {fan_name}님 아쉽습니다.\n{team} 패배했습니다. 상대: {opp}{dh_suffix}\n📊 {score_line}\n")
                        else:
                            messages.append(f"💤 {team1} vs {team2} — 노잼 경기입니다 👀{dh_suffix}\n📊 {score_line}\n")

                    # 오늘 실시간 경기
                    elif date == today_str:
                        if "회" in status:
                            inning = status
                            if team1_is_fan:
                                messages.append(f"🔥 {fan_team_map[team1]}님,\n{team1} 현재 {inning} 진행 중. 상대: {team2}{dh_suffix}\n📊 {score_line}\n")
                            if team2_is_fan:
                                messages.append(f"🔥 {fan_team_map[team2]}님,\n{team2} 현재 {inning} 진행 중. 상대: {team1}{dh_suffix}\n📊 {score_line}\n")

                except:
                    continue

        result_text = "\n".join(messages).strip()

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
