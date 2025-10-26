import json
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SONGS_PATH = os.path.join(PROJECT_ROOT, 'data', 'songs.json')
RULES_PATH = os.path.join(PROJECT_ROOT, 'data', 'rules.json')

def load_data():
    try:
        with open(SONGS_PATH, 'r', encoding='utf-8') as f:
            songs = json.load(f)
        with open(RULES_PATH, 'r', encoding='utf-8') as f:
            rules = json.load(f)
        return songs, rules
    except FileNotFoundError as e:
        return None, None
    except json.JSONDecodeError as e:
        return None, None

def get_recommendations(user_input, songs, rules, top_n):
    if not songs or not rules:
        return []

    song_scores = {song['title']: 0 for song in songs}

    user_mood = user_input.get('tam_trang')
    user_activity = user_input.get('hoat_dong')
    user_genre = user_input.get('the_loai_yeu_thich')

    for song in songs:
        if user_mood and user_mood in song.get('moods', []):
            song_scores[song['title']] += 35
        if user_activity and user_activity in song.get('activity', []):
            song_scores[song['title']] += 35
        if user_genre and user_genre in song.get('genre', []):
            song_scores[song['title']] += 35

    for rule in rules:
        condition_key, condition_value = list(rule['condition'].items())[0]
        
        if condition_key in user_input and user_input[condition_key] == condition_value:
            effect = rule['effect']
            effect_type = effect['type']
            effect_target = effect['target']
            effect_score = effect['score']

            for song in songs:
                if effect_type == 'the_loai':
                    if effect_target in song.get('genre', []):
                        song_scores[song['title']] += effect_score
                
                elif effect_type == 'nghe_si':
                    artist_field = song.get('artist', [])
                    if isinstance(artist_field, list):
                        if effect_target in artist_field:
                            song_scores[song['title']] += effect_score
                    elif isinstance(artist_field, str):
                        if effect_target == artist_field:
                            song_scores[song['title']] += effect_score

    sorted_songs = sorted(song_scores.items(), key=lambda item: item[1], reverse=True)
    final_recommendations = [(song, score) for song, score in sorted_songs if score > 0]
    return final_recommendations[:top_n]