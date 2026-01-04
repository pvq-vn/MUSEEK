import os
import streamlit as st
import streamlit.components.v1 as components
from recommender import Recommender
from time import sleep

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
logo_path = os.path.join(parent_dir, "meta", "logo.png")
icon_path = os.path.join(parent_dir, "meta", "icon.png")

st.set_page_config(
    page_title = "MUSEEK",
    page_icon = icon_path,
    layout = "wide",
    initial_sidebar_state = "collapsed",
    menu_items={
        'Get Help': 'https://github.com/pvq-vn/MUSEEK',
        'Report a bug': "https://www.facebook.com/pvq.pvq.pvq.pvq",
        'About': """
        ### MUSEEK - Hệ gợi ý âm nhạc
        Project học phần IT3160 - Nhập môn TTNT
        
        **GVHD:** Đỗ Tiến Dũng

        **Sinh viên thực hiện:**
        * Phạm Văn Quyết - 202416331
        * Lớp: Khoa học máy tính 02 - K69
        * Mail: quyet.pv2416331@sis.hust.edu.vn
        """
    }
)

def apply_custom_style():
    st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem !important; 
            padding-bottom: 3rem !important;
        }
                
        .input-label {
            font-size: 20px !important;
            font-weight: 700;
        }
        
        .stButton button {
            height: 45px;
            width: 100%;
            border-radius: 8px;
            font-weight: bold;
        }     
    </style>
    """, unsafe_allow_html = True)

@st.cache_resource
def load_recommender():
        return Recommender()

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
    st.session_state.mood_box = None
    st.session_state.act_box = None
    st.session_state.genre_box = None
    st.session_state.engine_choice = None
    st.session_state.recommendations = None
    st.session_state.active_media = None

if 'recommendations' not in st.session_state: st.session_state.recommendations = None 
if 'active_media' not in st.session_state: st.session_state.active_media = None 
if 'engine_choice' not in st.session_state: st.session_state.engine_choice = None

recommender_system = load_recommender()
apply_custom_style()

c_img1, c_img2, c_img3 = st.columns(3)
with c_img2:
    st.image(logo_path, use_container_width=True)

st.markdown("<p style='text-align: center; color: gray; margin-bottom: 20px; font-size: 24px;'>Chill đúng vibe - Nghe nhạc đúng sì taiii</p>", unsafe_allow_html=True)

with st.container(border=True):
    if recommender_system:
        mood_options = sorted(list(set(m for s in recommender_system.songs_db for m in s.get('moods', []))))
        activity_options = sorted(list(set(a for s in recommender_system.songs_db for a in s.get('activity', []))))
        genre_options = sorted(list(set(g for s in recommender_system.songs_db for g in s.get('genre', []))))

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown('<p class="input-label">Bạn đang cảm thấy thế nào?</p>', unsafe_allow_html=True)
            selected_mood = st.selectbox("Mood", mood_options, key="mood_box", label_visibility="collapsed", placeholder="Chọn tâm trạng", index=None)
        with c2:
            st.markdown('<p class="input-label">Bạn đang làm gì?</p>', unsafe_allow_html=True)
            selected_activity = st.selectbox("Activity", activity_options, key="act_box", label_visibility="collapsed", placeholder="Chọn hoạt động", index=None)
        with c3:
            st.markdown('<p class="input-label">Gu nhạc của bạn là thể loại nào?</p>', unsafe_allow_html=True)
            selected_genre = st.selectbox("Genre", genre_options, key="genre_box", label_visibility="collapsed", placeholder="Chọn thể loại yêu thích", index=None)

        st.write("")

        col1, col2 = st.columns([1, 4], vertical_alignment="center")
        with col1:
            st.markdown('<p style = "color: #FF9800" class="input-label">🔥 Chọn cơ chế suy diễn</p>', unsafe_allow_html=True)
        with col2:   
            engine_dict = {1: "InferenceEngine", 2: "RuleEngine", 3: "ExpertaEngine"}        
            selected_engine_id = st.radio(
                "Chọn Engine",
                options=[1, 2, 3],
                format_func=lambda x: engine_dict.get(x, f"Engine {x}"),
                horizontal=True,
                key="engine_choice",
                label_visibility="collapsed",
                index = 0
            )

        st.divider()

        b1, b2 = st.columns(2)
        with b1:
            search_clicked = st.button("TÌM NHẠC NGAY", use_container_width=True)
        with b2:
            st.button("RESET", on_click=reset_callback, use_container_width=True)

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
                    sleep(2)
                    st.session_state.recommendations = recommender_system.suggest(
                        user_input, 
                        top_n=10, 
                        Engine=selected_engine_id
                    )
                    st.session_state.active_media = None

st.write("") 
if st.session_state.recommendations and len(st.session_state.recommendations) > 0:
    st.success("##### Đây là những giai điệu dành cho bạn 😊")
    
    for i, item in enumerate(st.session_state.recommendations):
        song_title = item['title']
        score = item['score']
        reasons = item.get('reasons', [])

        song_data = get_song_info(song_title, recommender_system.songs_db)
        if not song_data: continue

        with st.container(border=True):
            raw_artist = song_data.get('artist', "Unknown")
            artist_str = " - ".join(raw_artist) if isinstance(raw_artist, list) else str(raw_artist)
            
            col_info, col_act = st.columns(2, vertical_alignment="center")
            
            with col_info:
                st.markdown(f"#### {i+1}. {song_title}")
                st.caption(f"👤 Nghệ sĩ: {artist_str}")

                if reasons:
                    with st.expander("Tại sao gợi ý bài này?"):
                        for r in reasons:
                            st.markdown(f"- {r}")
                        st.markdown(f"-> **Tổng điểm {score} - Xếp hạng {i+1}**")
            
            with col_act:
                bt1, bt2, bt3 = st.columns(3)
                with bt1:
                    st.button("📺 Xem MV", key=f"mv_{i}", on_click=set_active_media,
                              args=(i, 'mv'), use_container_width=True)
                with bt2:
                    st.button("🎧 Spotify", key=f"sp_{i}", on_click=set_active_media,
                              args=(i, 'spotify'), use_container_width=True)
                with bt3:
                    st.button("🎤 Karaoke", key=f"ka_{i}", on_click=set_active_media,
                              args=(i, 'karaoke'), use_container_width=True)

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
    st.info("**Sản phẩm demo Project Học phần IT3160: Nhập môn Trí tuệ nhân tạo - Thực hiện bởi Phạm Văn Quyết - 202416331**")