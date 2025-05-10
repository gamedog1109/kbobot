import json
from datetime import datetime

def generate_fan_messages(games_file='today_games.json', fans_file='fans.json'):
    # fans.json을 불러옴
    with open(fans_file, 'r', encoding='utf-8') as f:
        fans_data = json.load(f)

    # today_games.json 파일 읽기
    with open(games_file, 'r', encoding='utf-8') as f:
        today_games = json.load(f)

    # 경기 결과와 팬 정보 매칭하기
    messages = []

    for result in today_games['games']:
        # 결과에서 팀과 상태 파싱하기
        parts = result.split(" - 상태: ")
        game_info = parts[0].split(" : ")
        
        away_team = game_info[0].strip()
        home_team = game_info[1].strip()
        status = parts[1].strip()
        
        # 경기 상태에 따른 메시지 생성
        if status == "경기종료":
            # 승리한 팀 찾기
            away_score = int(game_info[0].split()[1])
            home_score = int(game_info[1].split()[1])

            if away_score > home_score:
                winner = away_team
            else:
                winner = home_team
            message = f"{winner} 팀의 승리입니다!"
        else:
            message = f"경기는 {away_team}와 {home_team}의 대결로 {status} 중입니다."
        
        # 응원하는 사람 찾기
        for fan, team in fans_data.items():
            if team in away_team:
                messages.append(f"{fan}님, {message} (스코어: {away_team} {away_score} : {home_score} {home_team})")
            elif team in home_team:
                messages.append(f"{fan}님, {message} (스코어: {away_team} {away_score} : {home_score} {home_team})")

    # 생성된 메시지 리스트 반환
    return messages
