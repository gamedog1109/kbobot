from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route("/game_message", methods=["POST"])
def game_message():
    try:
        with open('today_games.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        game_list = data.get("games", [])
        if not game_list:
            message = "오늘의 경기가 없습니다."
        else:
            message = "\n".join(game_list)
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": message
                        }
                    }
                ]
            }
        })
    except Exception as e:
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": f"[오류 발생] {str(e)}"
                        }
                    }
                ]
            }
        })