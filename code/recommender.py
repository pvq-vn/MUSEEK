import json, os

from inferenceEngine import get_recommendations
from ruleEngine import get_recommendations_rule_engine
from expertaEngine import get_recommendations_experta

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
    except Exception:
        return None, None

class Recommender:
    def __init__(self):
        self.songs_db, self.rules_db = load_data()
        if self.songs_db is None or self.rules_db is None:
            raise RuntimeError("Không thể tải dữ liệu cho hệ thống gợi ý.")

    def suggest(self, user_input, top_n, Engine):
        if not user_input:
            return []

        if Engine == 1:
            return get_recommendations(user_input, self.songs_db, self.rules_db, top_n)
        elif Engine == 2:
            return get_recommendations_rule_engine(user_input, self.songs_db, self.rules_db, top_n)
        elif Engine == 3:
            return get_recommendations_experta(user_input, self.songs_db, self.rules_db, top_n)