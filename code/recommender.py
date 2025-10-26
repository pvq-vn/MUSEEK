from inferenceEngine import load_data, get_recommendations

class Recommender:
    def __init__(self):
        self.songs_db, self.rules_db = load_data()
        if self.songs_db is None or self.rules_db is None:
            raise RuntimeError("Không thể tải dữ liệu cho hệ thống gợi ý. Hãy kiểm tra lại đường dẫn file trong 'inference_engine.py'.")

    def suggest(self, user_input, top_n):
        if not user_input:
            return []
        
        top_n = 5

        return get_recommendations(user_input, self.songs_db, self.rules_db, top_n)