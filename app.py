from kbo_scraper import get_today_kbo_results
from flask import Flask, request, jsonify


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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
