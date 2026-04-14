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
# 2. 데이터 관리 함수
# ─────────────────────────────────────────────────────────────
def load_data():
    """파일에서 FAQ 데이터를 불러옵니다. 파일이 없으면 빈 리스트를 반환합니다."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_data(data):
    """FAQ 데이터를 파일에 저장합니다."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 세션 상태에 데이터 로드 (최초 1회)
if "faq_db" not in st.session_state:
    st.session_state.faq_db = load_data()

# ─────────────────────────────────────────────────────────────
# 3. 챗봇 로직
# ─────────────────────────────────────────────────────────────
def get_bot_response(user_input):
    # 특수문자 제거 및 소문자화
    user_input_cleaned = re.sub(r'[^가-힣a-zA-Z0-9\s]', '', user_input).strip().lower()
    if not user_input_cleaned: 
        return "질문을 입력해 주세요. 😊"
    
    best_match = None
    max_keywords = 0
    
    # 지식 베이스 검색
    for item in st.session_state.faq_db:
        match_count = sum(1 for kw in item["keywords"] if kw.lower() in user_input_cleaned)
        if match_count > max_keywords:
            max_keywords = match_count
            best_match = item

    if best_match and max_keywords > 0:
        return best_match["answer"]
    
    return "죄송합니다. 해당 내용에 대한 정보를 찾지 못했습니다. 🧐 사내 교육 담당자에게 문의하시거나 관리자 모드에서 FAQ를 추가해 주세요."

# ─────────────────────────────────────────────────────────────
# 4. 사이드바 - 관리자 및 정보창
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/4e/Veeva_Systems_Logo.svg", width=150)
    
    st.divider()
    st.markdown("### 🛠️ 데이터 관리자 모드")
    
    # 지식 베이스 상태 표시
    st.info(f"현재 등록된 지식: **{len(st.session_state.faq_db)}**개")
    
    with st.expander("➕ 새 FAQ 추가하기"):
        new_q = st.text_input("질문(Question)", placeholder="예: 비밀번호를 잊어버렸어요.")
        new_kw = st.text_input("핵심 키워드 (쉼표로 구분)", placeholder="예: 비밀번호, 분실, 초기화")
        new_cat = st.selectbox("카테고리", [
            "교육 이수", "퀴즈", "커리큘럼", "SOP/규정", 
            "사용자 관리", "시스템 설정", "현장 교육", "일반"
        ])
        new_a = st.text_area("답변(Answer)", placeholder="상세한 해결 방법을 입력하세요.")
        
        if st.button("데이터 저장", use_container_width=True):
            if new_q and new_a and new_kw:
                new_entry = {
                    "question": new_q,
                    "keywords": [k.strip() for k in new_kw.split(",")],
                    "answer": new_a,
                    "category": new_cat
                }
                st.session_state.faq_db.append(new_entry)
                save_data(st.session_state.faq_db)
                st.success("새로운 지식이 추가되었습니다!")
                st.rerun()
            else:
                st.error("모든 필드를 입력해야 합니다.")

    st.divider()
    if st.button("🗑️ 대화 기록 삭제", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()
        
    st.markdown("---")
    st.caption("Veeva Vault Training Support Center v1.1")

# ─────────────────────────────────────────────────────────────
# 5. 메인 채팅 화면
# ─────────────────────────────────────────────────────────────
st.markdown('<h1 style="color:#1e293b;">🎓 LMS Support Center</h1>', unsafe_allow_html=True)
st.markdown("> **Veeva Vault Training** 사용 중 궁금한 점을 물어보세요.")

# 채팅 기록 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 기존 대화 렌더링
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# 사용자 입력 처리
if prompt := st.chat_input("질문을 입력하세요..."):
    # 사용자 메시지 표시
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 봇 응답 생성 및 표시
    response = get_bot_response(prompt)
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
