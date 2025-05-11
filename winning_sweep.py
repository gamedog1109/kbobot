def check_winning_series_and_sweep(series_games, fan_data):
    results = []
    for team, games in series_games.items():
        # 팀이 2연승 이상 하면 위닝시리즈
        if len(games) >= 2:
            consecutive_wins = sum(1 for game in games if game['status'] == '승리')
            if consecutive_wins >= 2:
                fan_name = [name for name, team_name in fan_data.items() if team_name == team]
                for fan in fan_name:
                    results.append(f"🎉 {fan}님, {team}은 위닝 시리즈를 달성했습니다! 🎉\n💰 찬조금 5,000원 납부해주세요.")

        # 팀이 3연승 이상 하면 스윕
        if len(games) >= 3:
            consecutive_wins = sum(1 for game in games if game['status'] == '승리')
            if consecutive_wins >= 3:
                fan_name = [name for name, team_name in fan_data.items() if team_name == team]
                for fan in fan_name:
                    results.append(f"🎉 {fan}님, {team}은 스윕을 달성했습니다! 🎉\n💰 찬조금 10,000원 납부해주세요.")

    return results