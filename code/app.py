import os
import streamlit as st
import streamlit.components.v1 as components
from recommender import Recommender

st.set_page_config(page_title="MUSEEK", layout="wide")

def apply_custom_style():
    st.markdown("""
    <style>
        /* Thu gọn padding đầu trang */
        .block-container {
            padding-top: 2rem !important; 
            padding-bottom: 3rem !important;
        }
                
        /* Chỉnh font label */
        .input-label {
            font-size: 20px !important;
            font-weight: 700;
            color: #555;
        }
        
        /* Style nút bấm */
        .stButton button {
            height: 45px;
            width: 100%;
            border-radius: 8px;
            font-weight: bold;
        }

        /* Container kết quả cho đẹp */
        div[data-testid="stVerticalBlock"] > div[style*="border"] {
            border-radius: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

apply_custom_style()

@st.cache_resource
def load_recommender():
    try:
        recommender = Recommender()
        if not recommender.songs_db: pass 
        return recommender
    except Exception as e:
        st.error(f"Lỗi load dữ liệu: {e}")
        return None

def get_song_info(title, songs_db):
    for song in songs_db:
        if song['title'] == title:
            return song
    return None

def convert_spotify_link(original_link):
    if not original_link or "embed" in original_link:
        return original_link
    return original_link.replace("/track/", "/embed/track/")

def set_active_media(index, media_type):
    if st.session_state.active_media == {'index': index, 'type': media_type}:
        st.session_state.active_media = None
    else:
        st.session_state.active_media = {'index': index, 'type': media_type}

def reset_callback():
    st.session_state.mood_box = ""
    st.session_state.act_box = ""
    st.session_state.genre_box = ""
    st.session_state.engine_choice = None
    st.session_state.recommendations = None
    st.session_state.active_media = None

# --- 4. STATE ---
if 'recommendations' not in st.session_state: st.session_state.recommendations = None 
if 'active_media' not in st.session_state: st.session_state.active_media = None 
if 'engine_choice' not in st.session_state: st.session_state.engine_choice = None

recommender_system = load_recommender()

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
logo_path = os.path.join(parent_dir, "meta", "logo.png")

c_img1, c_img2, c_img3 = st.columns([2, 2, 2])
with c_img2:
    st.image(logo_path, use_container_width=True)

st.markdown("<p style='text-align: center; color: gray; margin-bottom: 20px; font-size: 24px;'>Chill đúng vibe - Nghe nhạc đúng sì taiii</p>", unsafe_allow_html=True)

with st.container(border=True):
    if recommender_system:
        mood_options = sorted(list(set(m for s in recommender_system.songs_db for m in s.get('moods', []))))
        activity_options = sorted(list(set(a for s in recommender_system.songs_db for a in s.get('activity', []))))
        genre_options = sorted(list(set(g for s in recommender_system.songs_db for g in s.get('genre', []))))

        # Hàng 1: 3 Dropdown (Chia 3 cột)
        c1, c2, c3 = st.columns(3)
        with c1:
            #selected_mood = st.selectbox("Bạn đang cảm thấy thế nào?", options=[""] + mood_options)
            st.markdown('<p class="input-label">Bạn đang cảm thấy thế nào?</p>', unsafe_allow_html=True)
            selected_mood = st.selectbox("Mood", [""] + mood_options, key="mood_box", label_visibility="collapsed")
        with c2:
            st.markdown('<p class="input-label">Bạn đang làm gì?</p>', unsafe_allow_html=True)
            selected_activity = st.selectbox("Activity", [""] + activity_options, key="act_box", label_visibility="collapsed")
        with c3:
            st.markdown('<p class="input-label">Gu nhạc của bạn là thể loại nào?</p>', unsafe_allow_html=True)
            selected_genre = st.selectbox("Genre", [""] + genre_options, key="genre_box", label_visibility="collapsed")

        st.write("") # Spacer


        col1, col2 = st.columns([1, 4], vertical_alignment="center")
        # Hàng 2: Chọn Engine (Radio nằm ngang)
        with col1:
            st.markdown('<p class="input-label">🔥 Chọn cơ chế suy diễn</p>', unsafe_allow_html=True)
        
        # Mapping tên Engine cho ngầu (Tùy ông đặt tên lại nhé)
        with col2:   
            engine_dict = {1: "InferenceEngine", 2: "RuleEngine", 3: "ExpertaEngine"}
        
            selected_engine_id = st.radio(
                "Chọn Engine",
                options=[1, 2, 3],
                format_func=lambda x: engine_dict.get(x, f"Engine {x}"),
                horizontal=True,
                key="engine_choice",
                label_visibility="collapsed",
                index = None
            )

        st.divider()

        # Hàng 3: Nút bấm (Căn giữa hoặc full width)
        b1, b2 = st.columns(2)
        with b1:
            search_clicked = st.button("TÌM NHẠC NGAY", use_container_width=True)
        with b2:
            st.button("RESET", on_click=reset_callback, use_container_width=True)

        # --- LOGIC TÌM KIẾM ---
        if search_clicked:
            user_input = {}
            if selected_mood: user_input["tam_trang"] = selected_mood
            if selected_activity: user_input["hoat_dong"] = selected_activity
            if selected_genre: user_input["the_loai_yeu_thich"] = selected_genre

            if not user_input:
                st.warning("Vui lòng chọn ít nhất một tiêu chí!")
            elif selected_engine_id is None:
                st.warning("Vui lòng chọn cơ chế suy diễn")
            else:
                with st.spinner("Đang tìm kiếm những giai điệu phù hợp...."):
                    # Truyền Engine ID vào hàm suggest
                    st.session_state.recommendations = recommender_system.suggest(
                        user_input, 
                        top_n=10, 
                        Engine=selected_engine_id
                    )
                    st.session_state.active_media = None

# --- KHU VỰC KẾT QUẢ (HIỂN THỊ DƯỚI INPUT) ---
st.write("") 
if st.session_state.recommendations and len(st.session_state.recommendations) > 0:
    st.success("Đây là những giai điệu dành cho bạn lúc này ")
    
    # Grid layout cho kết quả: Chia 2 cột để hiển thị danh sách cho đỡ dài
    # Nếu muốn 1 cột dọc thì xóa dòng `c_res1, c_res2 = ...` và dùng `st` trực tiếp
    
    for i, (song_title, score) in enumerate(st.session_state.recommendations):
        song_data = get_song_info(song_title, recommender_system.songs_db)
        if not song_data: continue

        # Tạo container cho từng bài
        with st.container(border=True):
            # Header bài hát
            raw_artist = song_data.get('artist', "Unknown")
            artist_str = "- ".join(raw_artist) if isinstance(raw_artist, list) else str(raw_artist)
            
            # Layout dòng tiêu đề + score (nếu thích)
            col_info, col_act = st.columns(2, vertical_alignment="center")
            
            with col_info:
                st.markdown(f"#### {i+1}. {song_title}")
                st.caption(f"👤 Nghệ sĩ: {artist_str}")
            
            with col_act:
                # 3 nút thao tác nhỏ gọn
                bt1, bt2, bt3 = st.columns(3)
                with bt1:
                    if st.button("📺 Xem MV", key=f"mv_{i}"): set_active_media(i, 'mv')
                with bt2:
                    if st.button("🎧 Spotify", key=f"sp_{i}"): set_active_media(i, 'spotify')
                with bt3:
                    if st.button("🎤 Karaoke", key=f"ka_{i}"): set_active_media(i, 'karaoke')

            # Phần Player mở rộng
            current_active = st.session_state.active_media
            if current_active and current_active['index'] == i:
                st.divider()
                t = current_active['type']
                if t == 'mv':
                    _ = st.video(song_data.get('youtube')) if song_data.get('youtube') else st.warning("No Video")
                elif t == 'spotify':
                    l = song_data.get('spotify')
                    _ = components.iframe(convert_spotify_link(l), height=80) if l else st.warning("No Spotify")
                elif t == 'karaoke':
                    _ = st.video(song_data.get('karaoke')) if song_data.get('karaoke') else st.warning("No Karaoke")

elif st.session_state.recommendations is not None:
    st.warning("Sì tai nhạc của bạn hơi lạ nên mình botay.com")

else:
    # Màn hình chờ (Placeholder)
    st.info("Sản phẩm demo Project Học phần IT3160: Nhập môn Trí tuệ nhân tạo - Thực hiện bởi Phạm Văn Quyết - 202416331")