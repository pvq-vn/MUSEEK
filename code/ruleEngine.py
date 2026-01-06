import rule_engine

COMPILED_RULE_CACHE = []

def preCompile(rules):
    global COMPILED_RULE_CACHE
    COMPILED_RULE_CACHE = []

    for rule in rules:
        if not isinstance(rule, dict) or 'condition' not in rule or 'effect' not in rule:
            continue

        condition_list = []
        display_list = []

        for key, value in rule['condition'].items():
            display_list.append(f'{key} = {value}')
            if isinstance(value, str):
                condition_list.append(f'{key} == "{value}"')
            else:
                condition_list.append(f'{key} == {value}')

        rule_string = " and ".join(condition_list)

        try:
            engine_rule = rule_engine.Rule(rule_string)
            COMPILED_RULE_CACHE.append({
                'ast': engine_rule,
                'effect': rule['effect'],
                'reasons': display_list
            })
        except Exception:
            continue

def get_recommendations_rule_engine(user_input, songs, rules, top_n):
    if not COMPILED_RULE_CACHE: preCompile(rules)

    preferred_genres = {}
    preferred_artists = {}
    rule_reasons = {}

    for item in COMPILED_RULE_CACHE:
        engine_rule = item['ast']

        if engine_rule.matches(user_input):
            effect = item['effect']
            target = effect['target']
            score = effect['score']
            e_type = effect['type']

            if e_type == 'the_loai':
                preferred_genres[target] = preferred_genres.get(target, 0) + score
            elif e_type == 'nghe_si':
                preferred_artists[target] = preferred_artists.get(target, 0) + score

            if target not in rule_reasons: rule_reasons[target] = []
            rule_reasons[target].append(f'Luật khớp "{" ,".join(item['reasons'])}" -> {e_type} {target}: {score:+} điểm')

    song_scores = []

    user_mood = user_input.get('tam_trang')
    user_activity = user_input.get('hoat_dong')
    user_genre = user_input.get('the_loai_yeu_thich')

    for song in songs:
        total_score = 0
        reasons = []

        if user_mood and user_mood in song.get('moods', []):
            total_score += 50
            reasons.append(f'Đang {user_mood} nên +50 điểm')
        if user_activity and user_activity in song.get('activity', []):
            total_score += 50
            reasons.append(f'Đang {user_activity} nên +50 điểm')
        if user_genre and user_genre in song.get('genre', []):
            total_score += 75
            reasons.append(f'Vì thích {user_genre} nên +75 điểm')

        for genre in song.get('genre', []):
            if genre in preferred_genres:
                total_score += preferred_genres[genre]
                reasons.extend(rule_reasons[genre])
        
        artists = song.get('artist', [])
        if isinstance(artists, str): artists = [artists]

        for artist in artists:
            if artist in preferred_artists:
                total_score += preferred_artists[artist]
                reasons.extend(rule_reasons[artist])

        if total_score > 0:
            song_scores.append({
                'title': song['title'],
                'score': total_score,
                'reasons': reasons
            })

    song_scores.sort(key=lambda x: x['score'], reverse=True)
    return song_scores[:top_n]