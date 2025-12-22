import json
import matplotlib.pyplot as plt
import collections

# Load rules
try:
    with open('data/rules.json', 'r', encoding='utf-8') as f:
        rules = json.load(f)
except:
    rules = []

if rules:
    # Tách target theo loại
    genre_targets = []
    
    for rule in rules:
        effect = rule.get('effect', {})
        if effect.get('type') == 'the_loai':
            genre_targets.append(effect.get('target'))

    # Đếm tần suất
    genre_counts = collections.Counter(genre_targets)
    # Sắp xếp để vẽ đẹp
    sorted_genres = dict(sorted(genre_counts.items(), key=lambda item: item[1]))

    # Vẽ biểu đồ ngang (Horizontal Bar) cho dễ đọc tên
    plt.figure(figsize=(10, 8))
    plt.barh(list(sorted_genres.keys()), list(sorted_genres.values()), color='mediumpurple')
    
    plt.title('Mức độ ưu tiên của các Thể loại trong tập Luật')
    plt.xlabel('Số lượng luật suy diễn trỏ đến (Rule Count)')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Hiển thị số liệu trên cột
    for i, v in enumerate(sorted_genres.values()):
        plt.text(v + 0.1, i, str(v), va='center')

    plt.tight_layout()
    plt.savefig('data/chart_rules_analysis.png')
    print("Đã xuất biểu đồ phân tích luật: data/chart_rules_analysis.png")