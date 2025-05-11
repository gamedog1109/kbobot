@app.route("/fan_message", methods=["POST"])
def fan_message():
    try:
        with open('fans.json', 'r', encoding='utf-8') as f:
            fan_data = json.load(f)
        with open('today_games.json', 'r', encoding='utf-8') as f:
            game_data = json.load(f)

        games_by_date = game_data.get("games", {})
        today_str = datetime.now().strftime("%Y-%m-%d")
        yesterday_str = sorted(games_by_date.keys())[-2] if today_str in games_by_date else sorted(games_by_date.keys())[-1]
        fan_team_map = {v: k for k, v in fan_data.items()}

        messages = []

        for date, games in games_by_date.items():
            for game in games:
                try:
                    parts, status_raw = game.split(" - ")
                    status = status_raw.strip().replace("상태:", "").strip()
                    team_match = re.match(r"(.*) (\d+|vs) : (\d+|vs) (.*)", parts)

                    if not team_match:
                        continue  # 잘못된 형식

                    team1, score1_raw, score2_raw, team2 = team_match.groups()
                    team1_is_fan = team1 in fan_team_map
                    team2_is_fan = team2 in fan_team_map
                    score_line = f"{team1} {score1_raw} : {score2_raw} {team2}"

                    if score1_raw == "vs" or score2_raw == "vs":
                        # 경기 취소 또는 미진행
                        if team1_is_fan:
                            messages.append(f"☁️ {fan_team_map[team1]}님, {team1} 경기 진행되지 않았습니다. ({status})")
                        if team2_is_fan:
                            messages.append(f"☁️ {fan_team_map[team2]}님, {team2} 경기 진행되지 않았습니다. ({status})")
                        continue

                    score1, score2 = int(score1_raw), int(score2_raw)

                    if date == yesterday_str:
                        if team1_is_fan and team2_is_fan:
                            if score1 > score2:
                                messages.append(f"🎉 {fan_team_map[team1]}님 축하합니다! {team1}이 {team2}에게 승리했습니다. ({score_line})")
                            elif score2 > score1:
                                messages.append(f"🎉 {fan_team_map[team2]}님 축하합니다! {team2}이 {team1}에게 승리했습니다. ({score_line})")
                            else:
                                messages.append(f"⚖️ {fan_team_map[team1]}님과 {fan_team_map[team2]}님, {team1}과 {team2}가 비겼습니다. ({score_line})")
                        elif team1_is_fan or team2_is_fan:
                            team = team1 if team1_is_fan else team2
                            opp = team2 if team1_is_fan else team1
                            fan_name = fan_team_map[team]
                            team_score = score1 if team1_is_fan else score2
                            opp_score = score2 if team1_is_fan else score1
                            if team_score > opp_score:
                                messages.append(f"🎉 {fan_name}님 축하합니다! {team}이 {opp}에게 승리했습니다. ({score_line})")
                            elif team_score < opp_score:
                                messages.append(f"😢 {fan_name}님 아쉽습니다. {team}이 {opp}에게 패배했습니다. ({score_line})")
                            else:
                                messages.append(f"⚖️ {fan_name}님, {team}이 {opp}와 비겼습니다. ({score_line})")

                    elif date == today_str:
                        if "예정" in status:
                            if team1_is_fan:
                                messages.append(f"📅 {fan_team_map[team1]}님, {team1} 경기는 아직 시작되지 않았습니다.")
                            if team2_is_fan:
                                messages.append(f"📅 {fan_team_map[team2]}님, {team2} 경기는 아직 시작되지 않았습니다.")
                        elif "회" in status:
                            inning = status
                            if team1_is_fan:
                                messages.append(f"🔥 {fan_team_map[team1]}님, {team1}이 {team2}와 {inning} 경기 중입니다. ({score_line})")
                            if team2_is_fan:
                                messages.append(f"🔥 {fan_team_map[team2]}님, {team2}이 {team1}와 {inning} 경기 중입니다. ({score_line})")

                except:
                    continue

        result_text = "\n".join(messages)

        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [{
                    "simpleText": {"text": result_text}
                }]
            }
        })

    except Exception as e:
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [{
                    "simpleText": {"text": f"❌ 오류 발생: {str(e)}"}
                }]
            }
        })
