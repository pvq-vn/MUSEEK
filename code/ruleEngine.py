import rule_engine

def get_recommendations_rule_engine(user_input, songs, rules, top_n):
    preferred_genres = {}
    preferred_artists = {}

    for rule in rules:
        if not isinstance(rule, dict) or 'condition' not in rule or 'effect' not in rule:
            continue
                
        conditions_list = []
        for key, value in rule['condition'].items():
            if isinstance(value, str):
                conditions_list.append(f'{key} == "{value}"')
            else:
                conditions_list.append(f'{key} == {value}')
        
        rule_string = " and ".join(conditions_list)

        try:
            engine_rule = rule_engine.Rule(rule_string)

            if engine_rule.matches(user_input):
                effect = rule['effect']
                target = effect['target']
                score = effect['score']
                e_type = effect['type']

                if e_type == 'the_loai':
                    preferred_genres[target] = preferred_genres.get(target, 0) + score
                elif e_type == 'nghe_si':
                    preferred_artists[target] = preferred_artists.get(target, 0) + score

        except Exception:
            continue

    song_scores = []

    user_mood = user_input.get('tam_trang')
    user_activity = user_input.get('hoat_dong')
    user_genre = user_input.get('the_loai_yeu_thich')

    for song in songs:
        total_score = 0

        if user_mood and user_mood in song.get('moods', []):
            total_score += 50
        if user_activity and user_activity in song.get('activity', []):
            total_score += 50
        if user_genre and user_genre in song.get('genre', []):
            total_score += 50

        for genre in song.get('genre', []):
            if genre in preferred_genres:
                total_score += preferred_genres[genre]
        
        artists = song.get('artist', [])
        if isinstance(artists, str): artists = [artists]

        for artist in artists:
            if artist in preferred_artists:
                total_score += preferred_artists[artist]

        if total_score > 0:
            song_scores.append((song['title'], total_score))

    song_scores.sort(key=lambda x: x[1], reverse=True)
    return song_scores[:top_n]