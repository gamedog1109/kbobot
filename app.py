from flask import Flask, request, jsonify
from kbo_scraper import get_today_kbo_results
import tomorrow_games
from kbo_weather_checker import build_weather_message


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

@app.route("/weather", methods=["POST"])
def handle_weather():
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





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
