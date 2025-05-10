import json
from flask import Flask, request, jsonify
from today_games import get_today_game_info
from kbo_weather_checker import build_weather_message
from next_series import get_next_series_info


app = Flask(__name__)

# GitHub Pages에 JSON 파일이 업로드된 주소로 바꿔주세요
JSON_URL = "https://github.com/gamedog1109/kbobot/today_games.json"


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





# fans.json과 today_games.json 파일을 로드
def load_data():
    with open('fans.json', 'r', encoding='utf-8') as fans_file:
        fans_data = json.load(fans_file)

    with open('today_games.json', 'r', encoding='utf-8') as games_file:
        games_data = json.load(games_file)
    
    return fans_data, games_data

# 메시지 생성 함수
def generate_game_messages(games_data, fans_data):
    messages = []
    
    for game in games_data['games']:
        # 정규 표현식을 이용해 경기 정보 추출
        match = re.match(r'(\S+)\s(\d+)\s*:\s*(\d+)\s*(\S+)\s*-\s*(\S+)', game)
        if match:
            team1 = match.group(1)
            score1 = match.group(2)
            team2 = match.group(4)
            score2 = match.group(3)
            status = match.group(5)  # "상태" 값을 가져옵니다.
        
            # 경기 종료 상태 확인
            if status == "경기종료":  # 경기가 종료된 경우
                winner = team1 if int(score1) > int(score2) else team2
                message = f"{team1} {score1} : {score2} {team2} - {winner} 경기 이겼습니다! 🎉"
                # 승리한 팀을 응원하는 팬을 찾기
                for fan, team in fans_data.items():
                    if team == winner:
                        messages.append(f"{fan}님, {message} - 경기 상태: 경기 종료\n")
            else:  # 경기가 진행 중인 경우
                leader = team1 if int(score1) > int(score2) else team2
                messages.append(f"{team1} {score1} : {score2} {team2} - {leader}가 현재 이기고 있습니다! 💪 - 경기 상태: 진행 중\n")
    
    return messages

# 게임 상태 메시지 반환 라우트
@app.route("/game_updates", methods=["POST"])
def game_updates():
    fans_data, games_data = load_data()
    messages = generate_game_messages(games_data, fans_data)
    return jsonify({"messages": messages})

















@app.route("/")
def index():
    return "✅ KBO 챗봇 서버 정상 실행 중!"

if __name__ == "__main__":
    app.run(debug=True)
