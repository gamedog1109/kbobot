from kbo_scraper import get_today_kbo_results
from flask import Flask, request, jsonify
from series_checker import analyze_series


app = Flask(__name__)

@app.route("/kbo_results", methods=["POST"])
def kbo_results():
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



@app.route("/series_test", methods=["POST"])
def series_test():
    fake_series = [
        {"home": "LG", "away": "두산", "home_score": 4, "away_score": 2, "stadium": "잠실"},
        {"home": "두산", "away": "LG", "home_score": 3, "away_score": 6, "stadium": "잠실"},
        {"home": "LG", "away": "두산", "home_score": 2, "away_score": 1, "stadium": "잠실"}
    ]

    summary, penalties = analyze_series(fake_series)

    msg = summary + "\n"
    if penalties:
        msg += "\n💸 벌금 낼 사람:\n"
        for name, amount in penalties:
            msg += f"- {name}: {amount}원\n"
    else:
        msg += "\n벌금 낼 사람 없음!"

    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [{
                "simpleText": {
                    "text": msg
                }
            }]
        }
    })



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
