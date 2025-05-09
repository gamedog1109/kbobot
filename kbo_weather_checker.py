import requests
import pandas as pd
from datetime import datetime, timedelta

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

def build_weather_message(csv_path="KBO_2025_May_to_August.csv"):
    tomorrow = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        return f"[오류] CSV 불러오기 실패: {e}"

    games = []
    for _, row in df[df["date"] == tomorrow].iterrows():
        stadium = row["stadium"]
        if stadium in stadium_coords:
            games.append({
                "teams": f"{row['home_team']} vs {row['away_team']}",
                "stadium": stadium,
                "lat": stadium_coords[stadium][0],
                "lon": stadium_coords[stadium][1]
            })

    if not games:
        return f"{tomorrow} 예정된 경기가 없습니다."

    response = f"[{tomorrow} KBO 경기 우천 가능성 안내]\n\n"
    for g in games:
        w = get_weather(g["lat"], g["lon"], g["stadium"])
        response += f"{g['stadium']} ({g['teams']}): {w}\n"

    return response.strip()
