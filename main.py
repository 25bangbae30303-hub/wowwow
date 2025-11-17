import streamlit as st
from googleapiclient.discovery import build

st.set_page_config(page_title="YouTube 댓글 TOP3", layout="wide")

# -----------------------------------------------------------------------------------
# 🔍 1) DEBUG: Streamlit Secrets 출력 (문제 원인 100% 확인용)
# -----------------------------------------------------------------------------------
st.subheader("🔧 DEBUG 정보 (문제 해결용)")
st.write("📌 현재 secrets keys:", list(st.secrets.keys()))
st.write("📌 secrets 전체 내용:", st.secrets)

# -----------------------------------------------------------------------------------
# 2) API KEY 읽기
# -----------------------------------------------------------------------------------
API_KEY = st.secrets.get("YOUTUBE_API_KEY", None)

if not API_KEY:
    st.error("❌ YOUTUBE_API_KEY 가 Streamlit Secrets 에 설정되지 않았습니다.")
    st.info("좌측 메뉴 → Settings → Secrets 에 아래처럼 입력하세요:\n\nYOUTUBE_API_KEY = \"your-key-here\"")
    st.stop()

# -----------------------------------------------------------------------------------
# 3) YouTube 댓글 가져오는 함수
# -----------------------------------------------------------------------------------
def get_top_comments(video_id, max_results=100):
    youtube = build("youtube", "v3", developerKey=API_KEY)

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=max_results,
        textFormat="plainText"
    )
    response = request.execute()

    comments = []
    for item in response.get("items", []):
        snippet = item["snippet"]["topLevelComment"]["snippet"]
        comments.append({
            "author": snippet.get("authorDisplayName"),
            "text": snippet.get("textDisplay"),
            "likes": snippet.get("likeCount"),
            "published": snippet.get("publishedAt")
        })

    comments.sort(key=lambda x: x["likes"], reverse=True)
    return comments[:3]

# -----------------------------------------------------------------------------------
# 4) UI
# -----------------------------------------------------------------------------------
st.title("📌 YouTube 댓글 좋아요 TOP 3 분석기")

video_url = st.text_input(
    "🎥 유튜브 영상 URL 입력",
    placeholder="https://www.youtube.com/watch?v=xxxx"
)

if st.button("조회하기"):
    if "watch?v=" not in video_url:
        st.error("❌ 올바른 YouTube URL을 입력해주세요.")
        st.stop()

    video_id = video_url.split("watch?v=")[-1].split("&")[0]

    with st.spinner("댓글 분석 중..."):
        try:
            top_comments = get_top_comments(video_id)
        except Exception as e:
            st.error(f"API 오류 발생: {e}")
            st.stop()

    if not top_comments:
        st.warning("⚠️ 댓글이 없거나 API가 데이터를 반환하지 않았습니다.")
    else:
        st.success("분석 완료!")

        medals = ["🥇 1위", "🥈 2위", "🥉 3위"]
        for i, c in enumerate(top_comments):
            st.subheader(medals[i])
            st.write(f"**작성자:** {c['author']}")
            st.write(f"**좋아요:** 👍 {c['likes']}")
            st.write(f"**댓글:** {c['text']}")
            st.write("---")
