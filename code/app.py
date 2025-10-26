import streamlit as st
from recommender import Recommender

st.set_page_config(page_title="MUSEEK", layout="centered")

@st.cache_resource
def load_recommender():
    try:
        recommender = Recommender()
        if not recommender.songs_db or not recommender.rules_db:
            raise RuntimeError        
        return Recommender()
    except RuntimeError as e:
        st.error(e)
        return None
    except FileNotFoundError as e:
        st.error(e)
        return None
    except Exception as e:
        st.error(e)
        return None

recommender_system = load_recommender()

st.title("Project IT3160 - MUSEEK 🎵")
st.write("Chill đúng vibe - Nghe nhạc đúng sì taiii")

if 'selected_mood' not in st.session_state:
    st.session_state.selected_mood = ""
if 'selected_activity' not in st.session_state:
    st.session_state.selected_activity = ""
if 'selected_genre' not in st.session_state:
    st.session_state.selected_genre = ""
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None

if recommender_system:
    mood_options = sorted(list(set(mood for song in recommender_system.songs_db for mood in song.get('moods', []))))
    activity_options = sorted(list(set(act for song in recommender_system.songs_db for act in song.get('activity', []))))
    genre_options = sorted(list(set(g for song in recommender_system.songs_db for g in song.get('genre', []))))

    selected_mood = st.selectbox("Bạn đang cảm thấy thế nào?", options=[""] + mood_options)
    selected_activity = st.selectbox("Giờ bạn đang làm gì đó?", options=[""] + activity_options)
    selected_genre = st.selectbox("Hãy nói cho tôi gu nhạc của bạn.", options=[""] + genre_options)

    if st.button("Tìm nhạc ngay", use_container_width=True):
        user_input = {}
        if selected_mood:
            user_input["tam_trang"] = selected_mood
        if selected_activity:
            user_input["hoat_dong"] = selected_activity
        if selected_genre:
            user_input["the_loai_yeu_thich"] = selected_genre

        if not user_input:
            st.warning("Vui lòng chọn ít nhất một tiêu chí.")
        else:
            with st.spinner("Đang tìm kiếm những giai điệu phù hợp..."):
                recommendations = recommender_system.suggest(user_input, top_n=5)

                if recommendations:
                    st.success("Nghe thử những giai điệu này xem đã đúng vibe chưa nhé:")
                    for i, (song_title, score) in enumerate(recommendations):
                        st.write(f"{i+1}. **{song_title}** (Điểm phù hợp: {score})")
                else:
                    st.info("Sì tai nhạc của bạn hơi lạ nên mình botay.com")