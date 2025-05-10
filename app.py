from flask import Flask, request, jsonify
from crawler import get_live_scores
from today_games import get_today_games_info
from next_series import get_next_series
from kbo_weather_checker import get_weather_forecast

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    result = get_live_scores()
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [{
                "simpleText": {"text": result}
            }]
        }
    })

@app.route("/games_today", methods=["POST"])
def games_today():
    message = get_today_games_info()
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": message}}]
        }
    })

@app.route("/next_series", methods=["POST"])
def next_series():
    message = get_next_series()
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": message}}]
        }
    })

@app.route("/weather_today", methods=["POST"])
def weather_today():
    message = get_weather_forecast()
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": message}}]
        }
    })

@app.route("/")
def index():
    return "✅ KBO 챗봇 서버 정상 실행 중!"

if __name__ == "__main__":
    app.run(debug=True)
