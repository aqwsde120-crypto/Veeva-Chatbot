import streamlit as st
import re
import json
import os
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# 1. 페이지 설정 및 디자인
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Veeva Vault Training Support Center",
    page_icon="🎓",
    layout="wide"
)

# 데이터 파일 경로
DATA_FILE = "faq_database.json"

# ─────────────────────────────────────────────────────────────
# 2. 데이터 관리 함수 (데이터 축적을 위한 로직)
# ─────────────────────────────────────────────────────────────
def load_data():
    """파일에서 FAQ 데이터를 불러옵니다."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # 파일이 없을 경우 기본 초기 데이터
        return [
            {
                "question": "LMS 교육관리 SOP 정보",
                "keywords": ["sop", "버전", "시행일"],
                "answer": "📄 **SOP 정보 (CKD-SOP-1931)**: 최신 버전 Revision 4입니다.",
                "category": "SOP/규정"
            }
        ]

def save_data(data):
    """FAQ 데이터를 파일에 저장합니다."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 세션 상태에 데이터 로드
if "faq_db" not in st.session_state:
    st.session_state.faq_db = load_data()

# ─────────────────────────────────────────────────────────────
# 3. 챗봇 로직
# ─────────────────────────────────────────────────────────────
def get_bot_response(user_input):
    user_input_cleaned = re.sub(r'[^가-힣a-zA-Z0-9\s]', '', user_input).strip()
    if not user_input_cleaned: return "질문을 입력해 주세요. 😊"
    
    best_match = None
    max_keywords = 0
    for item in st.session_state.faq_db:
        match_count = sum(1 for kw in item["keywords"] if kw.lower() in user_input_cleaned.lower())
        if match_count > max_keywords:
            max_keywords = match_count
            best_match = item

    if best_match and max_keywords > 0:
        return best_match["answer"]
    return "해당 내용에 대한 정보를 찾지 못했습니다. 🧐"

# ─────────────────────────────────────────────────────────────
# 4. 사이드바 - 관리자 기능 (데이터 축적 화면)
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/4e/Veeva_Systems_Logo.svg", width=150)
    
    st.divider()
    st.markdown("### 🛠️ 데이터 관리자 모드")
    with st.expander("➕ 새 FAQ 추가하기"):
        new_q = st.text_input("질문(Question)")
        new_kw = st.text_input("키워드 (쉼표로 구분)")
        new_cat = st.selectbox("카테고리", ["교육 이수", "퀴즈", "커리큘럼", "SOP/규정", "일반"])
        new_a = st.text_area("답변(Answer)")
        
        if st.button("데이터 저장"):
            if new_q and new_a and new_kw:
                new_entry = {
                    "question": new_q,
                    "keywords": [k.strip() for k in new_kw.split(",")],
                    "answer": new_a,
                    "category": new_cat
                }
                st.session_state.faq_db.append(new_entry)
                save_data(st.session_state.faq_db)
                st.success("데이터가 성공적으로 추가되었습니다!")
                st.rerun()
            else:
                st.error("모든 필드를 입력해주세요.")

    st.divider()
    st.markdown(f"**현재 등록된 지식:** {len(st.session_state.faq_db)}개")
    if st.button("🗑️ 대화 초기화"):
        st.session_state.chat_history = []
        st.rerun()

# ─────────────────────────────────────────────────────────────
# 5. 메인 화면
# ─────────────────────────────────────────────────────────────
st.markdown('<h1 style="color:#1e293b;">🎓 LMS Support Center</h1>', unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

if prompt := st.chat_input("질문을 입력하세요..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    response = get_bot_response(prompt)
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
