import rule_engine

def get_recommendations_rule_engine(user_input, songs, rules, top_n):
    
    # Bước 1: Suy diễn dùng thư viện Rule-Engine
    
    preferred_genres = {user_input.get('the_loai_yeu_thich'): 35} if user_input.get('the_loai_yeu_thich') else {}
    preferred_artists = {}

    # Duyệt qua tập luật
    for rule in rules:
        # Bỏ qua những rule đánh dấu
        if not isinstance(rule, dict) or 'condition' not in rule or 'effect' not in rule:
            continue

        # 1. Chuyển đổi JSON condition sang cú pháp của Rule-Engine
                
        conditions_list = []
        for key, value in rule['condition'].items():
            if isinstance(value, str):
                conditions_list.append(f'{key} == "{value}"')
            else:
                conditions_list.append(f'{key} == {value}')
        
        # Nối các điều kiện bằng logic AND
        rule_string = " and ".join(conditions_list)

        try:
            # 2. Định nghĩa Rule
            rule = rule_engine.Rule(rule_string)

            # 3. So khớp với facts là user_input
            if rule.matches(user_input):
                # Nếu luật khớp thì kích hoạt effect
                effect = rule['effect']
                target = effect['target']
                score = effect['score']
                e_type = effect['type']

                if e_type == 'the_loai':
                    preferred_genres[target] = preferred_genres.get(target, 0) + score
                elif e_type == 'nghe_si':
                    preferred_artists[target] = preferred_artists.get(target, 0) + score

        except rule_engine.RuleSyntaxError as e:
            print(f"Lỗi cú pháp luật: {rule_string} - {e}")
            continue
        except Exception as e:
            continue

    # Bước 2: Tính điểm cho từng bài hát

    song_scores = []

    user_mood = user_input.get('tam_trang')
    user_activity = user_input.get('hoat_dong')

    for song in songs:
        total_score = 0

        # 1. Điểm từ moods và activity thông qua đối sánh trực tiếp
        if user_mood and user_mood in song.get('moods', []): total_score += 35
        if user_activity and user_activity in song.get('activity', []): total_score += 35

        # 2. Điểm từ genre thông qua suy diễn
        for genre in song.get('genre', []):
            if genre in preferred_genres:
                total_score += preferred_genres[genre]
        
        # 3. Điểm từ artist thông qua suy diễn
        artists = song.get('artist', [])
        if isinstance(artists, str): artists = [artists]

        for artist in artists:
            if artist in preferred_artists:
                total_score += preferred_artists[artist]

        if total_score > 0:
            song_scores.append((song['title'], total_score))

    # Sắp xếp giảm dần để lấy ra top_n bài hát có điểm cao nhất
    song_scores.sort(key=lambda x: x[1], reverse=True)
    return song_scores[:top_n]