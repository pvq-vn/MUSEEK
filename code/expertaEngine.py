import collections
import collections.abc

try:
    if not hasattr(collections, 'Mapping'):
        collections.Mapping = collections.abc.Mapping
    if not hasattr(collections, 'MutableMapping'):
        collections.MutableMapping = collections.abc.MutableMapping
    if not hasattr(collections, 'Sequence'):
        collections.Sequence = collections.abc.Sequence
    if not hasattr(collections, 'Iterable'):
        collections.Iterable = collections.abc.Iterable
except Exception:
    pass

from experta import *

class UserContext(Fact): pass
class Recommendation(Fact): pass

class GlobalEngine(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.scores_genre = {}
        self.scores_artist = {}
        self.rule_reasons = {}

    @Rule(Recommendation(type = MATCH.Type, target = MATCH.target, score = MATCH.score, reason = MATCH.reason))
    def collect_score(self, Type, target, score, reason):
        if Type == 'the_loai':
            self.scores_genre[target] = self.scores_genre.get(target, 0) + score
        elif Type == 'nghe_si':
            self.scores_artist[target] = self.scores_artist.get(target, 0) + score
        
        if target not in self.rule_reasons: self.rule_reasons[target] = []
        self.rule_reasons[target].append(reason)

ENGINE_INSTANCE = None

def create_dynamic_rule(rule, index):
    conditions = rule.get('condition', {})
    effect = rule.get('effect', {})    
    priority = len(conditions)

    condition_str = " ,".join([f"{k} = {v}" for k, v in conditions.items()])
    reason_text = f"Luật khớp '{condition_str}' -> {effect['type']} {effect['target']}: {effect['score']:+} điểm"
    
    @Rule(UserContext(**conditions), salience=priority)
    def dynamic_rule_func(self):
        self.declare(Recommendation(
            type=effect['type'],
            target=effect['target'],
            score=effect['score'],
            reason = reason_text
        ))
    
    dynamic_rule_func.__name__ = f'generated_rule_{index}'
    return dynamic_rule_func

def init_engine_once(rules):
    global ENGINE_INSTANCE

    if ENGINE_INSTANCE is None:
        for i, rule in enumerate(rules):
            if not isinstance(rule, dict): continue
            rule_func = create_dynamic_rule(rule, i)
            setattr(GlobalEngine, rule_func.__name__, rule_func)

        ENGINE_INSTANCE = GlobalEngine()

def get_recommendations_experta(user_input, songs, rules, top_n):
    init_engine_once(rules)
    engine = ENGINE_INSTANCE

    engine.reset()
    engine.scores_genre = {}
    engine.scores_artist = {}
    engine.rule_reasons = {}

    clean_input = {k: v for k, v in user_input.items() if v}
    if clean_input:
        engine.declare(UserContext(**clean_input))

    engine.run()

    preferred_genres = engine.scores_genre
    preferred_artists = engine.scores_artist
    rule_reasons = engine.rule_reasons
    
    song_scores = []
    user_mood = user_input.get('tam_trang')
    user_activity = user_input.get('hoat_dong')
    user_genre_input = user_input.get('the_loai_yeu_thich')

    for song in songs:
        total_score = 0
        reasons = []
        
        song_moods = set(song.get('moods', []))
        song_activities = set(song.get('activity', []))
        song_genres = song.get('genre', [])

        if user_mood and user_mood in song_moods: 
            total_score += 50
            reasons.append(f"Đang {user_mood} nên +50 điểm")
        
        if user_activity and user_activity in song_activities: 
            total_score += 50
            reasons.append(f"Đang {user_activity} nên +50 điểm")

        if user_genre_input and user_genre_input in song_genres: 
            total_score += 75
            reasons.append(f"Vì thích {user_genre_input} nên +75 điểm")

        for genre in song_genres:
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