import streamlit as st
import re
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# 1. 페이지 설정 및 디자인 커스텀
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Veeva Vault Training Help Center",
    page_icon="🎓",
    layout="wide"
)

# 커스텀 CSS 주입 (고급스러운 디자인 적용)
st.markdown("""
    <style>
    /* 전체 배경색 및 폰트 설정 */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* 사이드바 스타일링 */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e9ecef;
    }
    
    /* 챗봇 메시지 스타일 개선 */
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    
    /* 헤더 스타일링 */
    .main-header {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        color: #64748b;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* 카드형 UI (사이드바 메뉴용) */
    .info-card {
        background-color: #f1f5f9;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# 2. FAQ 데이터 정의
# ─────────────────────────────────────────────────────────────
FAQ_DATA = [
    # ── 교육 이수 ───────────────────────────────────────────
    {
        "question": "교육 이수는 어떻게 하나요?",
        "keywords": ["이수", "완료", "어떻게", "방법", "교육 완료", "training assignment", "이수 방법"],
        "answer": (
            "📋 **교육 이수 방법**\n\n"
            "1. **My Tasks** 또는 **Learner Homepage**에서 교육 과제를 클릭합니다.\n"
            "2. 문서를 읽은 후 **전자 서명(eSignature)**을 입력하여 완료 처리합니다.\n"
            "3. 퀴즈나 강의 참석이 필요한 경우 해당 단계를 추가로 완료해야 합니다."
        ),
        "category": "교육 이수"
    },
    {
        "question": "교육이 완료됐는데 이수 처리가 안 돼요.",
        "keywords": ["이수 안 됨", "완료 안 됨", "처리 안 됨", "이수 처리", "반영 안 됨", "완료했는데", "안 됨"],
        "answer": (
            "⚠️ **이수 미반영 원인 확인**\n\n"
            "1. **전자 서명 미입력** — 과제를 다시 열어 eSignature를 완료하세요.\n"
            "2. **퀴즈 미통과 또는 ILT 미참석** — 해당 단계를 완료하세요.\n"
            "3. **시스템 처리 지연** — 잠시 후 페이지를 새로고침해 보세요."
        ),
        "category": "교육 이수"
    },
    {
        "question": "모바일에서 교육을 들을 수 있나요?",
        "keywords": ["모바일", "휴대폰", "스마트폰", "앱", "mobile", "vault mobile", "핸드폰"],
        "answer": (
            "📱 **모바일 교육 수강 방법**\n\n"
            "1. **모바일 브라우저** 또는 **Vault Mobile 앱**으로 교육 과제에 접근 가능합니다.\n"
            "2. 여러 문서는 **View Training** 탭 → **Next** 버튼으로 순서대로 진행합니다.\n"
            "3. 완료 가능한 과제는 **Complete** 버튼이 활성화됩니다. (대리 접속자는 타인 대신 처리 불가)"
        ),
        "category": "교육 이수"
    },
    {
        "question": "교육 과제가 목록에 안 보여요.",
        "keywords": ["안 보임", "안보임", "없음", "안 보여", "목록에 없", "learner homepage", "과제 없음", "교육 없음"],
        "answer": (
            "🔍 **교육이 보이지 않는 경우 확인사항**\n\n"
            "1. **필터/탭 확인** — '완료됨' 필터를 해제하고 '진행 중'으로 변경하세요.\n"
            "2. **선행 교육 잠금** — 사전 이수(Prerequisite)가 완료되지 않아 잠겼을 수 있습니다.\n"
            "3. **미배정 상태** — 교육이 아직 배정되지 않은 경우 관리자에게 문의하세요."
        ),
        "category": "교육 이수"
    },
    {
        "question": "교육 마감일이 언제인가요?",
        "keywords": ["마감일", "기한", "due date", "마감", "기한 초과", "언제까지", "데드라인"],
        "answer": (
            "📅 **교육 마감일 확인 방법**\n\n"
            "1. **Learner Homepage** 또는 **My Tasks**에서 각 과제의 Due Date를 확인하세요.\n"
            "2. 마감일이 없는 경우, 관리자가 선택적(Optional) 마감일로 설정한 것입니다.\n"
            "3. 마감일이 지난 과제는 **'Overdue'** 상태로 표시됩니다."
        ),
        "category": "교육 이수"
    },
    {
        "question": "이미 읽은 문서인데 또 교육받아야 하나요?",
        "keywords": ["재교육", "retraining", "또", "다시", "반복", "이미 읽음", "또 나옴"],
        "answer": (
            "🔄 **재교육이 배정되는 이유**\n\n"
            "1. **문서 개정** — 문서가 새 버전으로 업데이트된 경우 자동으로 재교육이 생성됩니다.\n"
            "2. **정기 반복(Recurrence)** — 주기적 교육(예: 연 1회)으로 설정된 경우입니다.\n"
            "3. **관리자 발행** — 담당자가 Retraining을 별도로 발행한 경우입니다."
        ),
        "category": "교육 이수"
    },
 
    # ── 퀴즈 ─────────────────────────────────────────────────
    {
        "question": "퀴즈에서 떨어졌어요. 다시 볼 수 있나요?",
        "keywords": ["퀴즈", "quiz", "떨어짐", "불합격", "failed", "재시험", "다시 볼", "퀴즈 실패"],
        "answer": (
            "📝 **퀴즈 재응시 안내**\n\n"
            "1. 불합격 시 **'Failed'** 상태로 기록되며, 새 퀴즈 인스턴스를 통해 재응시할 수 있습니다.\n"
            "2. 이전 응시 기록과 독립적으로 새로운 퀴즈가 생성됩니다.\n"
            "3. 최대 재응시 횟수가 설정된 경우, 횟수 초과 시 관리자에게 문의하세요."
        ),
        "category": "퀴즈"
    },
    {
        "question": "퀴즈 합격 점수가 몇 점인가요?",
        "keywords": ["통과 점수", "합격 점수", "passing score", "몇 점", "기준 점수", "퀴즈 점수", "커트라인"],
        "answer": (
            "🎯 **퀴즈 합격 기준 확인**\n\n"
            "1. 퀴즈 시작 전 또는 퀴즈 페이지에서 **합격 기준 점수(Passing Score)**를 확인하세요.\n"
            "2. 합격 기준은 관리자가 설정하므로 교육마다 다를 수 있습니다.\n"
            "3. 정확한 기준은 교육 담당자(Training Admin)에게 문의하세요."
        ),
        "category": "퀴즈"
    },
    {
        "question": "퀴즈 제출이 안 돼요.",
        "keywords": ["퀴즈 제출", "submit", "제출 안 됨", "버튼 없음", "퀴즈 완료 안 됨", "제출 오류"],
        "answer": (
            "🛠️ **퀴즈 제출 문제 해결**\n\n"
            "1. **모든 문항에 답변**했는지 확인하세요 (미답변 시 제출 불가).\n"
            "2. 브라우저를 **새로고침** 후 재시도, 또는 **Chrome 최신 버전**을 사용해보세요.\n"
            "3. 문제가 지속되면 스크린샷과 함께 관리자에게 문의하세요."
        ),
        "category": "퀴즈"
    },
 
    # ── 커리큘럼 ──────────────────────────────────────────────
    {
        "question": "커리큘럼이란 무엇인가요?",
        "keywords": ["커리큘럼", "curriculum", "curricula", "교육 과정", "과정"],
        "answer": (
            "📚 **커리큘럼(Curriculum) 안내**\n\n"
            "1. 커리큘럼은 관련 교육 요건(Training Requirements)을 묶어 관리하는 단위입니다.\n"
            "2. 내부 교육은 **순서(Sequencing)**가 정해질 수 있어 앞 단계 이수 후 다음이 열립니다.\n"
            "3. 커리큘럼 이수 현황은 **Curriculum Completion Tracking** 화면에서 확인하세요."
        ),
        "category": "커리큘럼"
    },
    {
        "question": "커리큘럼 다음 교육이 잠겨서 안 열려요.",
        "keywords": ["잠김", "locked", "다음 교육", "순서", "sequencing", "열리지 않음", "커리큘럼 순서"],
        "answer": (
            "🔒 **커리큘럼 잠금 해제 방법**\n\n"
            "1. 커리큘럼 **순서(Sequencing)** 설정 시, 이전 교육을 완료해야 다음이 열립니다.\n"
            "2. 이전 단계 교육의 이수 상태를 확인하고 먼저 완료하세요.\n"
            "3. **사전 이수(Prerequisite)**가 별도 설정된 경우도 있으니 과제 세부사항을 확인하세요."
        ),
        "category": "커리큘럼"
    },
    {
        "question": "커리큘럼 이수 현황은 어디서 보나요?",
        "keywords": ["커리큘럼 현황", "이수 현황", "진행 상황", "completion tracking", "완료 현황"],
        "answer": (
            "📊 **커리큘럼 이수 현황 확인**\n\n"
            "1. **Learner Homepage** 또는 **Curriculum Completion Tracking** 화면에서 확인하세요.\n"
            "2. 각 교육 과제의 완료 여부와 전체 커리큘럼 진행률을 볼 수 있습니다.\n"
            "3. **My Tasks** 탭에서도 개별 과제 상태를 확인할 수 있습니다."
        ),
        "category": "커리큘럼"
    },
 
    # ── 사전 이수 ─────────────────────────────────────────────
    {
        "question": "사전 이수 조건이 있는 교육은 어떻게 되나요?",
        "keywords": ["사전 이수", "prerequisite", "선수 교육", "먼저", "선행", "선수과목"],
        "answer": (
            "📌 **사전 이수(Prerequisite) 교육 안내**\n\n"
            "1. 특정 교육은 다른 교육을 **먼저 이수**해야 접근할 수 있습니다.\n"
            "2. 사전 이수 미완료 시 해당 교육 과제가 잠기거나 목록에 표시되지 않을 수 있습니다.\n"
            "3. 어떤 교육이 선행 조건인지 모를 경우 교육 담당자에게 문의하세요."
        ),
        "category": "사전 이수 조건"
    },
 
    # ── 대체 교육 ─────────────────────────────────────────────
    {
        "question": "대체 교육이 배정됐는데 뭔가요?",
        "keywords": ["대체 교육", "substitute", "대체", "다른 교육", "대신", "대체과목"],
        "answer": (
            "🔀 **대체 교육(Substitute Training) 안내**\n\n"
            "1. 대체 교육은 원래 교육(Primary) 대신 배정되는 **대체 교육 과제**입니다.\n"
            "2. 언어, 역할, 지역 등 조건에 따라 관리자가 규칙을 설정해 자동 배정됩니다.\n"
            "3. 대체 교육 이수 시 원래 교육 요건도 **충족된 것으로 처리**됩니다."
        ),
        "category": "대체 교육"
    },
    {
        "question": "동등 교육(Equivalent)으로 이수 인정이 되나요?",
        "keywords": ["동등", "equivalent", "인정", "크레딧", "동등 교육", "동등 인정"],
        "answer": (
            "✅ **동등 교육(Equivalent Rule) 인정 안내**\n\n"
            "1. 관리자가 Equivalent Rule 설정 시, 특정 교육 이수로 관련 교육도 함께 이수 처리됩니다.\n"
            "2. **양방향(Bi-directional)** 설정 시, 둘 중 하나만 완료해도 양쪽 모두 인정됩니다.\n"
            "3. 해당 교육에 동등 인정 규칙이 있는지 교육 담당자에게 확인하세요."
        ),
        "category": "대체 교육"
    },
 
    # ── 이러닝 ────────────────────────────────────────────────
    {
        "question": "이러닝(E-Learning)이 실행이 안 돼요.",
        "keywords": ["이러닝", "e-learning", "elearning", "실행 안 됨", "열리지 않음", "콘텐츠 오류", "동영상", "영상"],
        "answer": (
            "💻 **이러닝 실행 오류 해결**\n\n"
            "1. **Chrome 최신 버전** 브라우저를 사용하고 있는지 확인하세요.\n"
            "2. **팝업 차단 해제** 또는 브라우저 **캐시 삭제** 후 재시도하세요.\n"
            "3. 문제가 지속되면 IT 또는 교육 관리자에게 브라우저 정보와 오류 메시지를 전달하세요."
        ),
        "category": "이러닝"
    },
    {
        "question": "이러닝을 다 봤는데 완료 처리가 안 돼요.",
        "keywords": ["이러닝 완료", "scorm", "완료 처리 안 됨", "다 봤는데", "이수 안 됨 이러닝", "이러닝 이수"],
        "answer": (
            "⚙️ **이러닝 완료 처리 확인사항**\n\n"
            "1. 이러닝 내 **모든 슬라이드/섹션을 끝까지** 진행했는지 확인하세요.\n"
            "2. 완료 기준이 **'전체 열람' 또는 '퀴즈 통과'**인 경우 해당 조건을 충족해야 합니다.\n"
            "3. 이러닝 창을 닫기 전 콘텐츠 내 **완료 버튼(Finish/Exit)**을 반드시 클릭하세요."
        ),
        "category": "이러닝"
    },
 
    # ── ILT ───────────────────────────────────────────────────
    {
        "question": "집합 교육(ILT)은 어떻게 등록하나요?",
        "keywords": ["집합 교육", "ilt", "instructor-led", "강의", "오프라인 교육", "등록", "세션"],
        "answer": (
            "🏫 **강의식 교육(ILT) 등록 방법**\n\n"
            "1. **Learner Homepage** 또는 My Tasks에서 해당 ILT 과제를 확인하세요.\n"
            "2. 세션 일정을 선택해 **Enroll(등록)**하거나, 관리자가 등록을 대행할 수 있습니다.\n"
            "3. 등록 후 **이메일 알림**이 발송되며, 참석 후 강사가 출석 확인 시 이수 처리됩니다."
        ),
        "category": "강의식 교육"
    },
    {
        "question": "ILT에 참석했는데 이수가 안 됐어요.",
        "keywords": ["ilt 이수", "집합 교육 이수", "출석 확인", "참석 확인", "세션 완료", "참석했는데"],
        "answer": (
            "📋 **ILT 이수 미완료 시 확인사항**\n\n"
            "1. **강사(또는 관리자)가 출석을 확인(Mark Attendance)**해야 이수 처리됩니다.\n"
            "2. 출석이 확인됐는지 교육 담당자에게 문의하세요.\n"
            "3. 추가로 **전자 서명이나 퀴즈**가 요구되는 경우 해당 단계도 완료해야 합니다."
        ),
        "category": "강의식 교육"
    },
 
    # ── OJT / 외부 교육 ────────────────────────────────────────
    {
        "question": "현장 교육(OJT)은 어떻게 이수 처리하나요?",
        "keywords": ["ojt", "현장 교육", "on-the-job", "현장", "실습"],
        "answer": (
            "🏭 **현장 교육(OJT) 이수 처리**\n\n"
            "1. OJT 과제를 열고 현장 교육 완료 후 **전자 서명**을 제출합니다.\n"
            "2. **평가자(Assessor) 또는 관리자 승인**이 필요한 경우도 있습니다.\n"
            "3. 이수 방법이 불확실하면 교육 담당자에게 OJT 완료 절차를 문의하세요."
        ),
        "category": "현장 교육"
    },
    {
        "question": "외부 교육 이수 결과를 시스템에 등록하고 싶어요.",
        "keywords": ["외부 교육", "external training", "외부 과정", "외부 이수", "사외 교육"],
        "answer": (
            "🌐 **외부 교육 이수 등록 방법**\n\n"
            "1. External Training Requirement로 설정된 과제가 있다면 **이수 증빙을 업로드**해 완료 처리하세요.\n"
            "2. 시스템에 과제가 없는 경우 교육 담당자에게 **과제 생성을 요청**하세요.\n"
            "3. 이수 증빙(수료증 등)을 미리 준비해 두세요."
        ),
        "category": "현장 교육"
    },
 
    # ── TRIA ──────────────────────────────────────────────────
    {
        "question": "TRIA가 무엇인가요?",
        "keywords": ["tria", "영향 평가", "training requirement impact", "문서 변경", "트리아"],
        "answer": (
            "🔬 **TRIA(Training Requirement Impact Assessment) 안내**\n\n"
            "1. TRIA는 **문서 변경 시 교육 요건에 미치는 영향을 평가**하는 프로세스입니다.\n"
            "2. 문서 개정 후 재교육이 필요한지 여부를 결정하는 데 사용됩니다.\n"
            "3. TRIA 결과에 따라 사용자에게 자동으로 교육 과제가 배정될 수 있습니다."
        ),
        "category": "교육 영향 평가"
    },
    {
        "question": "문서가 개정됐는데 왜 교육이 새로 생겼나요?",
        "keywords": ["문서 개정", "새 교육", "버전 변경", "업데이트 교육", "문서 변경 교육", "개정 후 교육"],
        "answer": (
            "📄 **문서 개정 후 교육 재배정 이유**\n\n"
            "1. 문서의 새 버전 승인 시 **TRIA 또는 자동화 규칙**에 의해 재교육 과제가 생성됩니다.\n"
            "2. 변경된 내용을 숙지했음을 확인하는 **전자 서명**이 필요합니다.\n"
            "3. **Delta 교육** 배정 시, 전체 문서 대신 **변경 사항만** 학습하면 됩니다."
        ),
        "category": "교육 영향 평가"
    },
 
    # ── 일반 ──────────────────────────────────────────────────
    {
        "question": "교육 관련 이메일 알림이 안 와요.",
        "keywords": ["알림", "이메일", "notification", "메일", "공지", "알림 없음"],
        "answer": (
            "📧 **교육 알림 미수신 시 확인사항**\n\n"
            "1. **스팸 메일함** 또는 '정크 메일'에 Veeva 알림이 필터링됐는지 확인하세요.\n"
            "2. Vault 계정의 **이메일 주소**가 올바르게 등록됐는지 프로필에서 확인하세요.\n"
            "3. 알림 설정이 비활성화된 경우 **시스템 관리자**에게 활성화를 요청하세요."
        ),
        "category": "일반"
    },
    {
        "question": "Vault에 로그인이 안 돼요.",
        "keywords": ["로그인", "login", "접속 불가", "비밀번호", "password", "계정", "로그인 오류"],
        "answer": (
            "🔑 **Vault 로그인 문제 해결**\n\n"
            "1. 비밀번호 오입력이 잦으면 계정이 잠깁니다 → **관리자에게 잠금 해제** 요청하세요.\n"
            "2. **'비밀번호 재설정(Forgot Password)'** 기능으로 비밀번호를 재설정하세요.\n"
            "3. **SSO(싱글 사인온)** 환경이라면 사내 IT팀에 문의하세요."
        ),
        "category": "일반"
    },
    {
        "question": "내 교육 이수 기록은 어디서 확인하나요?",
        "keywords": ["이수 기록", "이수 현황", "기록 확인", "이수 내역", "완료 기록", "training record", "교육 기록"],
        "answer": (
            "🗂️ **교육 이수 기록 확인 방법**\n\n"
            "1. **Learner Homepage** → '완료된 교육(Completed)' 탭에서 이수 목록을 확인하세요.\n"
            "2. **My Tasks** → 상태 필터를 '완료(Completed)'로 설정해도 확인 가능합니다.\n"
            "3. 상세 이수 이력(날짜·서명 정보)은 각 교육 과제 **상세 페이지**에서 확인하세요."
        ),
        "category": "일반"
    },
    {
        "question": "교육 담당자에게 어떻게 문의하나요?",
        "keywords": ["담당자", "문의", "연락", "관리자", "admin", "도움", "contact"],
        "answer": (
            "📞 **교육 담당자 문의 방법**\n\n"
            "1. 회사 내부 교육 담당 부서 **(HR 또는 Quality/Compliance팀)**으로 연락하세요.\n"
            "2. Vault 시스템 내 **Help / Support 링크**를 통해 티켓을 제출할 수 있습니다.\n"
            "3. 긴급한 경우 **시스템 관리자(Vault Admin)**에게 직접 연락하세요."
        ),
        "category": "일반"
    },
    {
        "question": "교육 반복 주기(Recurrence)가 뭔가요?",
        "keywords": ["반복", "recurrence", "주기", "정기 교육", "재교육 주기", "매년"],
        "answer": (
            "🔁 **교육 반복(Training Recurrence) 안내**\n\n"
            "1. 반복 교육은 일정 주기(예: 1년마다)로 **자동 재배정**되는 교육 과제입니다.\n"
            "2. 이전 이수 완료 날짜를 기준으로 **다음 교육이 생성**됩니다.\n"
            "3. **Refresher 교육** 설정 시, 전체 교육 대신 핵심 내용 복습 교육이 배정됩니다."
        ),
        "category": "교육 반복"
    },
]

# ─────────────────────────────────────────────────────────────
# 3. 세션 상태 초기화
# ─────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "question_log" not in st.session_state:
    st.session_state.question_log = []

# ─────────────────────────────────────────────────────────────
# 4. 로직 함수
# ─────────────────────────────────────────────────────────────
def get_bot_response(user_input):
    user_input_cleaned = re.sub(r'[^가-힣a-zA-Z0-9\s]', '', user_input).strip()
    
    if not user_input_cleaned:
        return "질문을 입력해 주세요. 😊"

    best_match = None
    max_keywords = 0

    for item in FAQ_DATA:
        match_count = sum(1 for kw in item["keywords"] if kw.lower() in user_input_cleaned.lower())
        if match_count > max_keywords:
            max_keywords = match_count
            best_match = item

    if best_match and max_keywords > 0:
        return best_match["answer"]
    else:
        return "죄송합니다. 해당 질문에 대한 정보를 찾지 못했습니다. 🧐\n키워드를 바꿔서 질문하시거나, 구체적인 내용을 교육 담당자에게 문의해 주세요."

# ─────────────────────────────────────────────────────────────
# 5. 사이드바 디자인
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/4e/Veeva_Systems_Logo.svg", width=150)
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="info-card"><strong>ℹ️ 시스템 가이드</strong><br>Veeva Vault Training FAQ 전용 챗봇입니다.</div>', unsafe_allow_html=True)
    
    # 카테고리 정보
    st.markdown("### 📂 FAQ 카테고리")
    categories = sorted(set(item["category"] for item in FAQ_DATA))
    for cat in categories:
        st.caption(f"• {cat}")
    
    st.divider()
    
    # 로그 섹션
    st.markdown("### 📋 최근 질문 로그")
    if st.session_state.question_log:
        for log in reversed(st.session_state.question_log[-5:]):
            st.text(f"[{log['timestamp']}]")
            st.caption(log['question'][:20] + "...")
    else:
        st.info("로그가 없습니다.")

    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.question_log = []
        st.rerun()

# ─────────────────────────────────────────────────────────────
# 6. 메인 화면 레이아웃
# ─────────────────────────────────────────────────────────────
st.markdown('<h1 class="main-header">🎓 LMS Support Center</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Veeva Vault Training에 대해 궁금한 점을 물어보세요.</p>', unsafe_allow_html=True)

# 대화 내용 표시
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# ─────────────────────────────────────────────────────────────
# 7. 채팅 입력 및 응답 처리
# ─────────────────────────────────────────────────────────────
# 추천 질문 버튼 (가로 배치)
col1, col2, col3 = st.columns(3)
quick_queries = ["교육 이수 방법", "퀴즈 재응시", "커리큘럼이란?"]

with col1:
    if st.button(f"🔍 {quick_queries[0]}", use_container_width=True):
        prompt = quick_queries[0]
        st.session_state.temp_prompt = prompt
with col2:
    if st.button(f"🔍 {quick_queries[1]}", use_container_width=True):
        prompt = quick_queries[1]
        st.session_state.temp_prompt = prompt
with col3:
    if st.button(f"🔍 {quick_queries[2]}", use_container_width=True):
        prompt = quick_queries[2]
        st.session_state.temp_prompt = prompt

# 채팅 입력창
if prompt := st.chat_input("질문을 입력하세요..."):
    # 사용자 메시지 추가
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 봇 메시지 생성 및 추가
    response = get_bot_response(prompt)
    
    # 로그 기록
    st.session_state.question_log.append({
        "question": prompt,
        "answer": response[:30] + "...",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

    with st.chat_message("assistant"):
        st.markdown(response)
        st.caption("💡 다른 도움이 더 필요하신가요?")
    
    st.session_state.chat_history.append({"role": "assistant", "content": response})

# 버튼 클릭 시 처리 로직 (st.chat_input 외부에서 실행되도록 세션 활용 가능)
if 'temp_prompt' in st.session_state:
    p = st.session_state.pop('temp_prompt')
    # 아래 로직을 통해 버튼 클릭 시 자동으로 질문이 입력된 것처럼 동작
    st.session_state.chat_history.append({"role": "user", "content": p})
    response = get_bot_response(p)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.rerun()
