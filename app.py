from kbo_scraper import get_today_kbo_results, get_recent_series_games
from flask import Flask, request, jsonify
from series_checker import analyze_series
import get_next_week_games import predict_matchups

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


from kbo_scraper import get_next_week_games
from series_checker import predict_matchups



@app.route("/next_matchups", methods=["POST"])
def next_matchups():
    try:
        games = get_next_week_games()
        matchups = predict_matchups(games)

        if not matchups:
            msg = "📅 다음 1주일 동안 팬끼리 맞붙는 경기가 없어요!"
        else:
            msg = "📅 예상 내기 대결 안내 (1주일)\n\n"
            for matchup, pairs in matchups.items():
                msg += f"⚾ {matchup}\n"
                for fan1, fan2 in pairs:
                    msg += f"→ {fan1} vs {fan2}\n"
                msg += "\n"

        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [{
                    "simpleText": {
                        "text": msg.strip()
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
                        "text": f"⚠️ 매치업 예측 중 오류 발생:\n{str(e)}"
                    }
                }]
            }
        })


from kbo_scraper import get_kbo_rankings

@app.route("/ranking", methods=["POST"])
def ranking():
    try:
        rank_text = get_kbo_rankings()

        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [{
                    "simpleText": {
                        "text": rank_text
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
                        "text": f"⚠️ 순위 불러오기 실패: {str(e)}"
                    }
                }]
            }
        })




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
