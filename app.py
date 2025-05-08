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



@app.route("/series_real", methods=["POST"])
def series_real():
    try:
        recent_games = get_recent_series_games(days=4)  # 최근 4일 경기 긁기
        summary, penalties = analyze_series(recent_games)

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

    except Exception as e:
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [{
                    "simpleText": {
                        "text": f"⚠️ 시리즈 분석 중 오류 발생:\n{str(e)}"
                    }
                }]
            }
        })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
