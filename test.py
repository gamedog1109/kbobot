import re
import json

# fans.json과 today_games.json 파일을 로드
def load_data():
    with open('fans.json', 'r', encoding='utf-8') as fans_file:
        fans_data = json.load(fans_file)

    with open('today_games.json', 'r', encoding='utf-8') as games_file:
        games_data = json.load(games_file)
    
    return fans_data, games_data

# 메시지 생성 함수
def generate_game_messages(games_data, fans_data):
    messages = []
    
    for game in games_data['games']:
        # 정규 표현식을 이용해 경기 정보 추출
        match = re.match(r'(\S+)\s(\d+)\s*:\s*(\d+)\s*(\S+)\s*-\s*상태:\s*(\S+)', game)
        if match:
            team1 = match.group(1)
            score1 = match.group(2)
            team2 = match.group(4)
            score2 = match.group(3)
            status = match.group(5)  # "상태" 값을 가져옵니다.
        
            # 경기 종료 상태 확인
            if status == "경기종료":  # 경기가 종료된 경우
                winner = team1 if int(score1) > int(score2) else team2
                message = f"{team1} {score1} : {score2} {team2} - {winner} 경기 이겼습니다! 🎉"
                # 승리한 팀을 응원하는 팬을 찾기
                for fan, team in fans_data.items():
                    if team == winner:
                        messages.append(f"{fan}님, {message} - 경기 상태: 경기 종료\n")
            else:  # 경기가 진행 중인 경우
                leader = team1 if int(score1) > int(score2) else team2
                messages.append(f"{team1} {score1} : {score2} {team2} - {leader}가 현재 이기고 있습니다! 💪 - 경기 상태: 진행 중\n")
    
    return messages

# 데이터를 로드하고 메시지 생성
fans_data, games_data = load_data()
messages = generate_game_messages(games_data, fans_data)

# 메시지 출력
for msg in messages:
    print(msg)
