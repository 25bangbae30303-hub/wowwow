import streamlit as st
from googleapiclient.discovery import build

# ---- 페이지 기본 설정 ----
st.set_page_config(page_title="유튜브 댓글 TOP3 분석기", layout="wide")
st.title("📌 유튜브 영상 댓글 '좋아요' TOP 3 분석기")

# ---- API 설정 ----
API_KEY = st.secrets["YOUTUBE_API_KEY"] if "YOUTUBE_API_KEY" in st.secrets else ""


if not API_KEY:
    st.warning("⚠️ Streamlit secrets.toml 또는 환경변수에 YOUTUBE_API_KEY 를 설정해주세요.")
    
# ---- 함수: 유튜브 댓글 가져오기 ----
def get_top_comments(video_id, max_results=50):
    youtube = build("youtube", "v3", developerKey=API_KEY)

    comments = []

    # YouTube API 요청
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=max_results,
        textFormat="plainText"
    )

    response = request.execute()

    for item in response.get("items", []):
        snippet = item["snippet"]["topLevelComment"]["snippet"]
        comments.append({
            "author": snippet.get("authorDisplayName"),
            "text": snippet.get("textDisplay"),
            "likes": snippet.get("likeCount"),
            "published": snippet.get("publishedAt")
        })

    # 좋아요순 정렬
    comments.sort(key=lambda x: x["likes"], reverse=True)
    return comments[:3]


# ---- UI ----
video_url = st.text_input("🎥 유튜브 영상 URL을 입력하세요:", placeholder="https://www.youtube.com/watch?v=xxxx")

if st.button("댓글 분석하기"):
    if not API_KEY:
        st.error("❌ API 키가 없습니다. Streamlit secrets에 YOUTUBE_API_KEY를 추가하세요.")
    elif "watch?v=" not in video_url:
        st.error("❌ 올바른 유튜브 URL을 입력해주세요.")
    else:
        video_id = video_url.split("watch?v=")[-1].split("&")[0]

        with st.spinner("댓글 분석 중... ⏳"):
            try:
                top_comments = get_top_comments(video_id)
                if not top_comments:
                    st.warning("댓글을 가져올 수 없습니다.")
                else:
                    st.success("분석 완료!")

                    for idx, c in enumerate(top_comments, start=1):
                        st.write(f"### 🥇 TOP {idx}")
                        st.write(f"**작성자:** {c['author']}")
                        st.write(f"**좋아요:** 👍 {c['likes']}")
                        st.write(f"**댓글:** {c['text']}")
                        st.write("---")

            except Exception as e:
                st.error(f"오류 발생: {e}")
