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
FAQ_FILE = "faq_database.json"
LOG_FILE = "user_queries.json"  # 사용자 질문 로그 파일

# ─────────────────────────────────────────────────────────────
# 2. 데이터 관리 함수
# ─────────────────────────────────────────────────────────────
def load_json(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def log_user_query(query, was_answered):
    """사용자 질문을 로그 파일에 저장합니다."""
    logs = load_json(LOG_FILE)
    new_log = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "query": query,
        "was_answered": was_answered
    }
    logs.append(new_log)
    save_json(LOG_FILE, logs)

# 세션 상태 초기화
if "faq_db" not in st.session_state:
    st.session_state.faq_db = load_json(FAQ_FILE)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ─────────────────────────────────────────────────────────────
# 3. 고도화된 챗봇 로직
# ─────────────────────────────────────────────────────────────
def get_bot_response(user_input):
    query = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', user_input).strip().lower()
    query_words = set(query.split())
    
    if not query: 
        return None, []
    
    results = []
    for item in st.session_state.faq_db:
        score = 0
        keywords = [k.lower() for k in item.get("keywords", [])]
        matched_keywords = [kw for kw in keywords if kw in query]
        score += len(matched_keywords) * 10
        
        if query in item["question"].lower() or item["question"].lower() in query:
            score += 15
            
        title_words = set(re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', item["question"]).lower().split())
        common_words = query_words.intersection(title_words)
        score += len(common_words) * 5
        
        if score > 0:
            results.append({"item": item, "score": score})

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    if not results:
        # 답변을 못 찾은 경우 로그 저장 (False)
        log_user_query(user_input, False)
        return None, []

    # 답변을 찾은 경우 로그 저장 (True)
    log_user_query(user_input, True)
    best_match = results[0]["item"]
    related_matches = [r["item"]["question"] for r in results[1:4]]
    
    return best_match["answer"], related_matches

# ─────────────────────────────────────────────────────────────
# 4. 사이드바 - 관리자 모드 (로그 확인 기능 추가)
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/4e/Veeva_Systems_Logo.svg", width=150)
    st.divider()
    
    tab1, tab2 = st.tabs(["✨ FAQ 관리", "📊 질문 로그"])
    
    with tab1:
        st.markdown("### 🛠️ FAQ 등록")
        with st.expander("➕ 새 FAQ 추가"):
            new_q = st.text_input("질문")
            new_kw = st.text_input("키워드 (쉼표 구분)")
            new_cat = st.selectbox("카테고리", ["교육 이수", "퀴즈", "시스템", "일반"])
            new_a = st.text_area("답변")
            if st.button("지식 저장"):
                if new_q and new_a:
                    st.session_state.faq_db.append({
                        "question": new_q, "keywords": [k.strip() for k in new_kw.split(",")],
                        "answer": new_a, "category": new_cat
                    })
                    save_json(FAQ_FILE, st.session_state.faq_db)
                    st.success("저장 완료!")
                    st.rerun()

    with tab2:
        st.markdown("### 📋 수집된 질문")
        logs = load_json(LOG_FILE)
        if logs:
            unanswered = [l for l in logs if not l["was_answered"]]
            st.metric("답변 못한 질문", len(unanswered))
            for l in reversed(logs[-10:]):
                status = "✅" if l["was_answered"] else "❌"
                st.caption(f"{status} [{l['timestamp']}]")
                st.write(f"**{l['query']}**")
        else:
            st.write("로그가 없습니다.")

    st.divider()
    if st.button("🗑️ 대화 삭제"):
        st.session_state.chat_history = []
        st.rerun()

# ─────────────────────────────────────────────────────────────
# 5. 메인 채팅 화면
# ─────────────────────────────────────────────────────────────
st.markdown('<h1 style="color:#1e293b;">🎓 LMS Support Center</h1>', unsafe_allow_html=True)

for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

if prompt := st.chat_input("질문을 입력하세요..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    answer, related = get_bot_response(prompt)
    
    with st.chat_message("assistant"):
        if answer:
            full_response = answer
            if related:
                full_response += "\n\n---\n**💡 연관 질문:**\n" + "\n".join([f"- {r}" for r in related])
            st.markdown(full_response)
        else:
            full_response = "죄송합니다. 지식 베이스에서 답변을 찾지 못했습니다. 🧐\n\n이 질문을 **'답변 요청 목록'**에 등록하시겠습니까? 담당자가 확인 후 업데이트하겠습니다."
            st.markdown(full_response)
            if st.button("📩 이 질문 등록하기"):
                # 이미 log_user_query에서 False로 저장됨
                st.info("질문이 성공적으로 등록되었습니다. 감사합니다!")
                
    st.session_state.chat_history.append({"role": "assistant", "content": full_response})
