import requests
import pandas as pd
from datetime import datetime

# API 키 (네 키)
API_KEY = "9fd6e52a7c66dd82574f4f87cc79e17b"

# 구장 좌표
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

# 날씨 텍스트 받아오는 함수
def get_weather(lat, lon, stadium_name):
    if stadium_name == "고척":
        return "🌟 허구연의 돔구장 (우천 취소 없음)"
    
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&lang=kr&units=metric"
    res = requests.get(url)
    
    if res.status_code != 200:
        return "❌ 날씨 정보 불러오기 실패"
    
    data = res.json()
    weather = data["weather"][0]["description"]
    
    if "비" in weather or "소나기" in weather:
        return f"{weather} 🌧 (우천 가능성 있음)"
    else:
        return f"{weather} ☁️ (우천 가능성 낮음)"

# 오늘 경기 기준 메시지 만들기
def build_weather_message(csv_path="KBO_2025_May_to_August.csv"):
    today = datetime.today().strftime("%Y-%m-%d")
    
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        return f"[오류] 일정 파일을 불러올 수 없습니다:\n{e}"
    
    games = []
    for _, row in df[df["date"] == today].iterrows():
        stadium = row["stadium"]
        if stadium in stadium_coords:
            games.append({
                "teams": f"{row['home_team']} vs {row['away_team']}",
                "stadium": stadium,
                "lat": stadium_coords[stadium][0],
                "lon": stadium_coords[stadium][1]
            })
    
    if not games:
        return f"📅 오늘({today}) 예정된 경기가 없습니다."
    
    # 메시지 포맷팅
    output = [f"📅 오늘({today}) KBO 구장 날씨 안내 🌤", ""]
    
    for g in games:
        weather_result = get_weather(g["lat"], g["lon"], g["stadium"])
        block = (
            f"🏟️ {g['stadium']}\n"
            f"🆚 {g['teams']}\n"
            f"{weather_result}\n"
        )
        output.append(block)
    
    return "\n".join(output).strip()
