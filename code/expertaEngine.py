import collections
import collections.abc

# Khôi phục các hàm cũ của Experta
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

# Định nghĩa các fact
class UserContext(Fact):
    pass

class Recommendation(Fact):
    pass

# Hàm tạo luật động
def create_dynamic_rule(rule, index):
    conditions = rule.get('condition', {})
    effect = rule.get('effect', {})
    
    # Priority dựa trên độ phức tạp của điều kiện
    priority = len(conditions)
    
    @Rule(UserContext(**conditions), salience=priority)
    def dynamic_rule_func(self):
        self.declare(Recommendation(
            type=effect['type'],
            target=effect['target'],
            score=effect['score']
        ))
    
    # Đặt tên function để experta không bị nhầm lẫn khi inspect
    dynamic_rule_func.__name__ = f'generated_rule_{index}'
    return dynamic_rule_func

def get_recommendations_experta(user_input, songs, rules, top_n):

    # Dùng class động để kết quả của lần trước không ảnh hưởng đến lần sau
    class TemporaryEngine(KnowledgeEngine):
        def __init__(self):
            super().__init__()
            self.scores_genre = {}
            self.scores_artist = {}

        @Rule(Recommendation(type=MATCH.Type, target=MATCH.target, score=MATCH.score))
        def collect_score(self, Type, target, score):
            if Type == 'the_loai':
                self.scores_genre[target] = self.scores_genre.get(target, 0) + score
            elif Type == 'nghe_si':
                self.scores_artist[target] = self.scores_artist.get(target, 0) + score

    # 2. Gắn luật UserContext vào class TemporaryEngine
    for i, rule in enumerate(rules):
        if not isinstance(rule, dict) or 'condition' not in rule or 'effect' not in rule: 
            continue
        rule_func = create_dynamic_rule(rule, i)
        setattr(TemporaryEngine, rule_func.__name__, rule_func)

    # 3. Khởi tạo engine từ class tạm
    engine = TemporaryEngine()
    engine.reset()

    # 4. Đẩy dữ liệu vào
    clean_input = {k: v for k, v in user_input.items() if v}
    if clean_input:
        engine.declare(UserContext(**clean_input))

    engine.run()

    # 5. Lấy kết quả từ engine
    preferred_genres = engine.scores_genre
    preferred_artists = engine.scores_artist
    
    # 6. Tính điểm tổng hợp (Hybrid Filtering)
    song_scores = []
    user_mood = user_input.get('tam_trang')
    user_activity = user_input.get('hoat_dong')
    user_genre_input = user_input.get('the_loai_yeu_thich')

    for song in songs:
        total_score = 0
        
        # Điểm từ đối sánh trực tiếp
        song_moods = set(song.get('moods', []))
        song_activities = set(song.get('activity', []))
        song_genres = song.get('genre', [])

        if user_mood and user_mood in song_moods: 
            total_score += 35
        
        if user_activity and user_activity in song_activities: 
            total_score += 35

        if user_genre_input and user_genre_input in song_genres: 
            total_score += 35

        # Điểm từ suy diễn
        for genre in song_genres:
            if genre in preferred_genres:
                total_score += preferred_genres[genre]
        
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