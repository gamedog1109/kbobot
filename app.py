from flask import Flask, request, jsonify
from kbo_scraper import get_today_kbo_results

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
