from flask import Flask, request, jsonify
from kbo_scraper import get_today_kbo_results
import tomorrow_games

app = Flask(__name__)

@app.route("/today_results", methods=["POST"])
def today_results():
    result_text = get_today_kbo_results()

    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [{
                "simpleText": {
                    "text": result_text
                }
            }]
        }
    })

@app.route('/')
def index():
    return 'KBO 챗봇 서버가 실행 중입니다!'

@app.route('/tomorrow_games', methods=['POST'])
def get_tomorrow_games():
    result = tomorrow_games.get_tomorrow_game_info()
    return jsonify({"version": "2.0", "template": {"outputs": [{"simpleText": {"text": result}}]}})




app = Flask(__name__)

API_KEY = "9fd6e52a7c66dd82574f4f87cc79e17b"
stadium_coords = {
    "잠실": (37.51332, 127.07259),
    "고척": (37.49812, 126.86710),
    "문학": (37.43500, 126.68921),
    "수원": (37.29823, 127.00948),
    "대전": (36.31718, 127.42852),
    "대구": (35.84194, 128.58820),
    "광주": (35.16805, 126.88823),
    "사직": (35.19442, 129.06344),
    "창원": (35.22260, 128.58312),
}

def get_weather(lat, lon, stadium_name):
    if stadium_name == "고척":
        return "허구연이 좋아하는 돔구장 🌟 (우천 취소 없음)"
    
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&lang=kr&units=metric"
    res = requests.get(url)
    if res.status_code != 200:
        return "🔴 날씨 정보 불러오기 실패"
    data = res.json()
    weather = data["weather"][0]["description"]
    if "비" in weather or "소나기" in weather:
        return f"{weather} 🌧 (우천 가능성 있음)"
    else:
        return f"{weather} ☁️ (우천 가능성 낮음)"

@app.route("/", methods=["POST"])
def kbo_weather_bot():
    tomorrow = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    df = pd.read_csv("KBO_2025_May_to_August.csv")
    tomorrow_games = df[df["date"] == tomorrow]

    games = []
    for _, row in tomorrow_games.iterrows():
        stadium = row["stadium"]
        if stadium in stadium_coords:
            games.append({
                "teams": f"{row['home_team']} vs {row['away_team']}",
                "stadium": stadium,
                "lat": stadium_coords[stadium][0],
                "lon": stadium_coords[stadium][1]
            })

    response = f"[{tomorrow} KBO 경기 우천 가능성 안내]\n\n"
    for game in games:
        result = get_weather(game["lat"], game["lon"], game["stadium"])
        response += f"{game['stadium']} ({game['teams']}): {result}\n"

    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [{
                "simpleText": {
                    "text": response.strip()
                }
            }]
        }
    })




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
