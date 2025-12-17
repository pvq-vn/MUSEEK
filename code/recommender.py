import json, os

from inferenceEngine import get_recommendations
from ruleEngine import get_recommendations_rule_engine
from expertaEngine import get_recommendations_experta

# Xác định đường dẫn tuyệt đối đến cơ sở tri thức
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SONGS_PATH = os.path.join(PROJECT_ROOT, 'data', 'songs.json')
RULES_PATH = os.path.join(PROJECT_ROOT, 'data', 'rules.json')

# 1. Hàm đọc dữ liệu từ cơ sở tri thức
def load_data():
    try:
        # Dùng with để chắc chắn f.close() luôn được thực hiện
        # mode 'r': chỉ đọc

        with open(SONGS_PATH, 'r', encoding='utf-8') as f:
            # load: đọc dữ liệu từ file và chuyển đổi sang kiểu dữ liệu Python tương ứng
            songs = json.load(f)
        with open(RULES_PATH, 'r', encoding='utf-8') as f:
            rules = json.load(f)
        return songs, rules
    
    # return None nếu có bất kỳ một lỗi nào xảy ra
    except Exception as e:
        print("Không thể đọc dữ liệu. Vui lòng thử lại!")
        return None, None

# 2. Lớp điều phối chính giúp giao tiếp giữa giao diện và bộ máy suy diễn
class Recommender:
    def __init__(self):
        self.songs_db, self.rules_db = load_data()
        if self.songs_db is None or self.rules_db is None:
            raise RuntimeError("Không thể tải dữ liệu cho hệ thống gợi ý. Hãy kiểm tra lại đường dẫn file.")

    def suggest(self, user_input, top_n, Engine):
        if not user_input:
            return []

        if Engine == 1:
            return get_recommendations(user_input, self.songs_db, self.rules_db, top_n)
        elif Engine == 2:
            return get_recommendations_rule_engine(user_input, self.songs_db, self.rules_db, top_n)
        elif Engine == 3:
            return get_recommendations_experta(user_input, self.songs_db, self.rules_db, top_n)