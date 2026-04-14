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
# 3. 고도화된 챗봇 로직 (유사도 검색 강화)
# ─────────────────────────────────────────────────────────────
def get_bot_response(user_input):
    # 1. 전처리: 특수문자 제거 및 공백 정규화
    query = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', user_input).strip().lower()
    query_words = set(query.split())
    
    if not query: 
        return "질문을 입력해 주세요. 😊", []
    
    results = []
    
    for item in st.session_state.faq_db:
        score = 0
        
        # 가중치 1: 키워드 매칭 (가장 중요)
        keywords = [k.lower() for k in item.get("keywords", [])]
        matched_keywords = [kw for kw in keywords if kw in query]
        score += len(matched_keywords) * 10
        
        # 가중치 2: 질문 제목에 포함 여부
        if query in item["question"].lower() or item["question"].lower() in query:
            score += 15
            
        # 가중치 3: 단어 단위 부분 일치
        title_words = set(re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', item["question"]).lower().split())
        common_words = query_words.intersection(title_words)
        score += len(common_words) * 5
        
        if score > 0:
            results.append({
                "item": item,
                "score": score
            })

    # 점수 순으로 정렬
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    if not results:
        return "죄송합니다. 해당 내용에 대한 정보를 찾지 못했습니다. 🧐 질문을 좀 더 간단하게 입력해 보시겠어요? (예: '비밀번호', '이수 방법')", []

    # 최상위 결과와 연관 질문 추출
    best_match = results[0]["item"]
    related_matches = [r["item"]["question"] for r in results[1:4]] # 상위 3개 연관 질문
    
    return best_match["answer"], related_matches

# ─────────────────────────────────────────────────────────────
# 4. 사이드바 - 관리자 및 정보창
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/4e/Veeva_Systems_Logo.svg", width=150)
    
    st.divider()
    st.markdown("### 🛠️ 데이터 관리자 모드")
    
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
    st.caption("Veeva Vault Training Support Center v1.2")

# ─────────────────────────────────────────────────────────────
# 5. 메인 채팅 화면
# ─────────────────────────────────────────────────────────────
st.markdown('<h1 style="color:#1e293b;">🎓 LMS Support Center</h1>', unsafe_allow_html=True)
st.markdown("> **Veeva Vault Training** 사용 중 궁금한 점을 자유롭게 물어보세요.")

# 채팅 기록 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 기존 대화 렌더링
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# 사용자 입력 처리
if prompt := st.chat_input("궁금한 점을 입력하세요 (예: 비밀번호 초기화는 어떻게 하나요?)"):
    # 사용자 메시지 표시
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 봇 응답 생성
    answer, related = get_bot_response(prompt)
    
    # 응답 구성
    full_response = answer
    if related:
        full_response += "\n\n---\n**💡 혹시 이런 질문을 찾으시나요?**\n"
        for r_q in related:
            full_response += f"- {r_q}\n"

    with st.chat_message("assistant"):
        st.markdown(full_response)
    
    st.session_state.chat_history.append({"role": "assistant", "content": full_response})
