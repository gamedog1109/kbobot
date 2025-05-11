import json
import re
import pandas as pd
from collections import defaultdict

# JSON 불러오기
with open("series_games.json", "r", encoding="utf-8") as f:
    game_data = json.load(f)

with open("fans.json", "r", encoding="utf-8") as f:
    fans = json.load(f)

# 팀별 승패 정리
pattern = re.compile(r"(.+?)\s(\d+)\s:\s(\d+)\s(.+)")
team_records = defaultdict(lambda: {'wins': 0, 'losses': 0})

for date, games in game_data['games'].items():
    for game in games:
        try:
            game_part, status_part = game.split(" - ")
            status = status_part.strip().replace("상태:", "").strip()
        except ValueError:
            continue
        if status != "경기종료":
            continue
        match = pattern.match(game_part)
        if not match:
            continue
        team1, score1, score2, team2 = match.groups()
        score1, score2 = int(score1), int(score2)
        team_records[team1]
        team_records[team2]
        if score1 > score2:
            team_records[team1]['wins'] += 1
            team_records[team2]['losses'] += 1
        elif score2 > score1:
            team_records[team2]['wins'] += 1
            team_records[team1]['losses'] += 1

# 데이터프레임 생성 및 remark 추가
df = pd.DataFrame.from_dict(team_records, orient="index")
df.index.name = "team"
df = df.reset_index()
df['remark'] = df['wins'].apply(lambda w: '스윕 🎉' if w == 3 else ('위닝 👍' if w == 2 else ''))

# 팬별 안내 메시지 구성
messages = []
for name, team in fans.items():
    row = df[df['team'] == team]
    if row.empty:
        msg = f"[{name}] {team} | 경기 없음"
    else:
        wins = row.iloc[0]['wins']
        losses = row.iloc[0]['losses']
        remark = row.iloc[0]['remark']
        if remark == '스윕 🎉':
            donation = 10000
        elif remark == '위닝 👍':
            donation = 5000
        else:
            donation = 0
        msg = f"[{name}] {team} {wins}승 {losses}패 | {remark or '노 위닝'} | 찬조금 {donation:,}원"
    messages.append(msg)

# 출력
print("\n📢 이번 시리즈 찬조금 납부:\n")
for m in messages:
    print(m)
