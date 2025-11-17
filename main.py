import streamlit as st
from googleapiclient.discovery import build

# -----------------------------
#  Streamlit Secrets에서 API 키 읽기
# -----------------------------
try:
    API_KEY = st.secrets["YOUTUBE_API_KEY"]
except KeyError:
    API_KEY = None

# -----------------------------
# 페이지 UI
# -----------------------------
st.set_page_config(page_title="YouTube 댓글 좋아요 TOP3", layout="wide")
st.title("📌 YouTube 댓글 좋아요 TOP3 분석기")

if not API_KEY:
    st.error("❌ YOUTUBE_API_KEY 가 Streamlit Secrets 에 설정되지 않았습니다.")
    st.info("좌측 메뉴 ➝ Settings ➝ Secrets 에 YOUTUBE_API_KEY 를 추가하세요.")
    st.stop()

# -----------------------------
# YouTube 댓글 가져오기 함수
# -----------------------------
def get_top_comments(video_id, max_results=100):
    youtube = build("youtube", "v3", developerKey=API_KEY)
    
    comments = []

    # API 요청
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=max_results,
        textFormat="plainText",
        order="relevance"  # 댓글 순서를 어느 정도 정렬
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

# -----------------------------
# 입력창
# -----------------------------
video_url = st.text_input(
    "🎥 유튜브 영상 URL 입력",
    placeholder="https://www.youtube.com/watch?v=xxxx"
)

if st.button("분석하기"):
    if "watch?v=" not in video_url:
        st.error("❌ 올바른 유튜브 영상 URL을 입력해주세요.")
        st.stop()

    video_id = video_url.split("watch?v=")[-1].split("&")[0]

    with st.spinner("댓글 가져오는 중... ⏳"):
        try:
            top_comments = get_top_comments(video_id)
        except Exception as e:
            st.error(f"API 오류 발생: {e}")
            st.stop()

    if not top_comments:
        st.warning("⚠️ 댓글이 없거나 불러오지 못했습니다.")
    else:
        st.success("분석 완료!")
        st.write("---")

        # TOP 3 출력
        medals = ["🥇 1위", "🥈 2위", "🥉 3위"]
        for i, comment in enumerate(top_comments):
            st.subheader(medals[i])
            st.write(f"**작성자:** {comment['author']}")
            st.write(f"**좋아요:** 👍 {comment['likes']}")
            st.write(f"**댓글:** {comment['text']}")
            st.write("---")
