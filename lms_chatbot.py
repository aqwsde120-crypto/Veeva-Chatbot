"""
=============================================================
Veeva Vault Training FAQ 챗봇 — CHAT A.I+ 스타일 UI
=============================================================
디자인: CHAT A.I+ UI 스타일 (좌측 사이드바 + 우측 채팅 영역)
실행:   streamlit run lms_chatbot.py
=============================================================
"""

import streamlit as st
import re
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# 1. FAQ 데이터 정의
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
# 2. 상수 정의
# ─────────────────────────────────────────────────────────────
EXAMPLE_QUESTIONS = [
    "교육 이수는 어떻게 하나요?",
    "퀴즈에서 떨어졌어요. 다시 볼 수 있나요?",
    "커리큘럼 다음 교육이 잠겨서 안 열려요.",
]

SAMPLE_HISTORY_TODAY = ["이러닝이 실행이 안 돼요", "교육 마감일 확인 방법"]
SAMPLE_HISTORY_WEEK  = ["ILT 등록 방법", "TRIA가 무엇인가요", "사전 이수 조건 안내"]

# ─────────────────────────────────────────────────────────────
# 3. 핵심 로직 함수
# ─────────────────────────────────────────────────────────────

def normalize_text(text: str) -> str:
    """텍스트 정규화 (소문자 + 특수문자 제거)"""
    text = text.lower()
    text = re.sub(r"[^\w\s가-힣]", " ", text)
    return text.strip()


def calculate_match_score(user_input: str, faq_item: dict) -> int:
    """키워드 매칭 점수 계산"""
    score = 0
    norm = normalize_text(user_input)
    for kw in faq_item["keywords"]:
        nkw = normalize_text(kw)
        if nkw == norm:
            score += 3
        elif nkw in norm:
            score += 2
        elif norm in nkw:
            score += 1
    return score


def find_best_faq(user_input: str) -> dict | None:
    """최적 FAQ 반환 (점수 1 이상)"""
    scored = [(calculate_match_score(user_input, item), item) for item in FAQ_DATA]
    scored.sort(key=lambda x: x[0], reverse=True)
    best_score, best_item = scored[0]
    return best_item if best_score >= 1 else None


def get_bot_response(user_input: str) -> str:
    """챗봇 응답 생성"""
    if not user_input.strip():
        return "질문을 입력해 주세요."
    result = find_best_faq(user_input)
    return result["answer"] if result else "관련된 정보를 찾지 못했습니다. 다른 표현으로 질문해주세요."


def init_session_state() -> None:
    """세션 상태 초기화"""
    defaults = {
        "chat_history": [],
        "question_log": [],
        "pending_input": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ─────────────────────────────────────────────────────────────
# 4. HTML/CSS 렌더링
# ─────────────────────────────────────────────────────────────

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* ── Reset & Base ─────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background: #ECEEF8 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

.block-container { padding: 0 !important; max-width: 100% !important; }
header[data-testid="stHeader"] { display: none !important; }
.stDeployButton { display: none !important; }
#MainMenu { display: none !important; }
footer { display: none !important; }

/* ── 사이드바 ─────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E8EAFB !important;
    min-width: 255px !important;
    max-width: 255px !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
}
section[data-testid="stSidebar"] .block-container {
    padding: 0 !important;
}

/* 사이드바 HTML 구조 */
.sb-wrap {
    padding: 22px 14px 20px;
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}
.sb-logo {
    font-size: 17px;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #111827;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.sb-logo-accent {
    background: linear-gradient(135deg, #5B6AF0 0%, #8B5CF6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* 새 대화 버튼 */
.sb-newchat {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 7px;
    width: 100%;
    padding: 10px;
    background: linear-gradient(135deg, #5B6AF0, #7C6EF5);
    color: white;
    border: none;
    border-radius: 12px;
    font-size: 13.5px;
    font-weight: 600;
    cursor: pointer;
    margin-bottom: 16px;
    font-family: 'Plus Jakarta Sans', sans-serif;
    transition: opacity 0.2s, transform 0.15s;
}
.sb-newchat:hover { opacity: 0.9; transform: translateY(-1px); }

/* 검색창 */
.sb-search {
    display: flex;
    align-items: center;
    gap: 8px;
    background: #F4F5FF;
    border: 1px solid #E8EAFB;
    border-radius: 10px;
    padding: 8px 12px;
    margin-bottom: 18px;
}
.sb-search-icon { font-size: 14px; opacity: 0.5; }
.sb-search-txt {
    font-size: 12.5px;
    color: #9CA3AF;
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* 대화 목록 */
.sb-group-label {
    font-size: 10.5px;
    font-weight: 700;
    color: #C4C9D4;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    padding: 0 4px;
    margin: 14px 0 6px;
}
.sb-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 10px;
    border-radius: 10px;
    font-size: 12.5px;
    color: #4B5563;
    cursor: pointer;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 1px;
    transition: background 0.15s;
}
.sb-item:hover { background: #F0F2FF; }
.sb-item.active {
    background: #EEF0FF;
    color: #5B6AF0;
    font-weight: 600;
}
.sb-item-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #D1D5DB;
    flex-shrink: 0;
}
.sb-item.active .sb-item-dot { background: #5B6AF0; }

/* 사이드바 하단 */
.sb-divider {
    margin: auto 0 0;
    border-top: 1px solid #F0F1F8;
    padding-top: 14px;
}
.sb-bottom-item {
    display: flex;
    align-items: center;
    gap: 9px;
    padding: 8px 10px;
    border-radius: 10px;
    font-size: 12.5px;
    color: #6B7280;
    cursor: pointer;
    transition: background 0.15s;
}
.sb-bottom-item:hover { background: #F4F5FF; }
.sb-avatar {
    width: 28px; height: 28px;
    border-radius: 50%;
    background: linear-gradient(135deg, #5B6AF0, #8B5CF6);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 11px;
    font-weight: 700;
    flex-shrink: 0;
}

/* ── 메인 채팅 ─────────────────────────────────── */

/* 메시지 행 */
.msg-row {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 4px;
    animation: msgIn 0.28s ease;
}
@keyframes msgIn {
    from { opacity:0; transform: translateY(10px); }
    to   { opacity:1; transform: translateY(0); }
}
.msg-row.user { justify-content: flex-end; }
.msg-row.bot  { justify-content: flex-start; }

/* 아바타 */
.msg-avatar {
    width: 34px; height: 34px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
    flex-shrink: 0;
    margin-top: 2px;
}
.msg-avatar.user-av {
    background: linear-gradient(135deg, #5B6AF0, #7C6EF5);
    color: white;
    font-size: 12px;
    font-weight: 700;
}
.msg-avatar.bot-av {
    background: linear-gradient(135deg, #5B6AF0, #8B5CF6);
}

/* 사용자 버블 */
.user-bubble {
    background: linear-gradient(135deg, #5B6AF0, #7C6EF5);
    color: white;
    padding: 11px 17px;
    border-radius: 18px 18px 4px 18px;
    max-width: 62%;
    font-size: 14px;
    line-height: 1.6;
    font-weight: 500;
    box-shadow: 0 3px 14px rgba(91,106,240,0.28);
    word-break: break-word;
}

/* 봇 응답 영역 */
.bot-wrap { display:flex; flex-direction:column; gap:5px; max-width: 66%; }
.bot-label {
    display: flex;
    align-items: center;
    gap: 6px;
}
.bot-label-name {
    font-size: 11.5px;
    font-weight: 700;
    color: #5B6AF0;
}
.bot-label-badge {
    font-size: 10px;
    background: #EEF0FF;
    color: #7C6EF5;
    padding: 1px 7px;
    border-radius: 20px;
    font-weight: 600;
}
.bot-bubble {
    background: #F7F8FF;
    border: 1px solid #E8EAFB;
    color: #1F2937;
    padding: 13px 17px;
    border-radius: 4px 18px 18px 18px;
    font-size: 13.5px;
    line-height: 1.78;
    box-shadow: 0 2px 8px rgba(91,106,240,0.06);
    word-break: break-word;
}
.bot-bubble strong { color: #111827; font-weight: 600; }
.bot-followup {
    font-size: 11.5px;
    color: #B0B5C9;
    padding-left: 2px;
}
.bot-actions {
    display: flex;
    gap: 4px;
    align-items: center;
}
.b-btn {
    background: none;
    border: 1px solid #E8EAFB;
    border-radius: 8px;
    padding: 3px 9px;
    font-size: 12px;
    cursor: pointer;
    color: #9CA3AF;
    transition: all 0.12s;
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.b-btn:hover { background:#EEF0FF; color:#5B6AF0; border-color:#C7CAFB; }
.regen-btn {
    display: flex;
    align-items: center;
    gap: 5px;
    background: none;
    border: none;
    font-size: 11.5px;
    color: #9CA3AF;
    cursor: pointer;
    margin-left: auto;
    font-family: 'Plus Jakarta Sans', sans-serif;
    transition: color 0.12s;
}
.regen-btn:hover { color: #5B6AF0; }

/* 환영 화면 */
.welcome-screen {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 70px 40px 30px;
    text-align: center;
}
.welcome-logo { font-size: 54px; margin-bottom: 18px; }
.welcome-h {
    font-size: 22px;
    font-weight: 800;
    color: #111827;
    letter-spacing: -0.6px;
    margin-bottom: 10px;
}
.welcome-sub {
    font-size: 13.5px;
    color: #9CA3AF;
    line-height: 1.75;
    max-width: 380px;
}

/* ── Streamlit 요소 재정의 ──────────────────────── */

/* 채팅 메시지 컨테이너 (st.container) */
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
    background: white;
    border-radius: 20px 20px 0 0;
}

/* 텍스트 입력창 */
.stTextInput > div > div > input {
    border: 1.5px solid #E8EAFB !important;
    border-radius: 50px !important;
    padding: 13px 22px !important;
    font-size: 14px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #111827 !important;
    background: #F9FAFF !important;
    transition: all 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #5B6AF0 !important;
    background: #fff !important;
    box-shadow: 0 0 0 3px rgba(91,106,240,0.1) !important;
}
.stTextInput > div > div > input::placeholder { color: #C4C9D4 !important; }
.stTextInput label { display: none !important; }

/* 전송 버튼 */
.stFormSubmitButton > button {
    border-radius: 50px !important;
    background: linear-gradient(135deg, #5B6AF0, #7C6EF5) !important;
    color: white !important;
    border: none !important;
    padding: 12px 24px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    box-shadow: 0 4px 14px rgba(91,106,240,0.35) !important;
    transition: all 0.2s !important;
}
.stFormSubmitButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(91,106,240,0.45) !important;
}

/* 예시 버튼 */
div[data-testid="stHorizontalBlock"] .stButton > button {
    border-radius: 50px !important;
    background: white !important;
    border: 1.5px solid #E8EAFB !important;
    color: #5B6AF0 !important;
    font-size: 12.5px !important;
    font-weight: 500 !important;
    padding: 7px 15px !important;
    transition: all 0.15s !important;
    white-space: nowrap !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
div[data-testid="stHorizontalBlock"] .stButton > button:hover {
    background: #EEF0FF !important;
    border-color: #BABFFF !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(91,106,240,0.15) !important;
}

/* 초기화 버튼 */
.stButton > button {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    border-radius: 10px !important;
}

/* 스크롤바 */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: #E0E3F0; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: #B0B5D0; }

/* 구분선 */
hr { border-color: #F0F1F8 !important; }

/* Streamlit form border 제거 */
[data-testid="stForm"] { border: none !important; padding: 0 !important; }
</style>
"""


def build_sidebar_html() -> str:
    """사이드바 HTML 생성"""
    # 현재 세션 첫 질문
    current_html = ""
    if st.session_state.chat_history:
        first_q = next((m["content"] for m in st.session_state.chat_history if m["role"] == "user"), None)
        if first_q:
            label = first_q[:24] + "…" if len(first_q) > 24 else first_q
            current_html = f"""
            <div class="sb-group-label">현재 대화</div>
            <div class="sb-item active">
                <span class="sb-item-dot"></span>{label}
            </div>
            """

    today_html = "\n".join(
        f'<div class="sb-item"><span class="sb-item-dot"></span>{t}</div>'
        for t in SAMPLE_HISTORY_TODAY
    )
    week_html = "\n".join(
        f'<div class="sb-item"><span class="sb-item-dot"></span>{t}</div>'
        for t in SAMPLE_HISTORY_WEEK
    )

    return f"""
<div class="sb-wrap">
    <!-- 로고 -->
    <div class="sb-logo">
        🎓 <span class="sb-logo-accent">LMS Helper</span>
    </div>

    <!-- 새 대화 -->
    <button class="sb-newchat" onclick="window.location.reload()">
        ＋ &nbsp;새 대화 시작
    </button>

    <!-- 검색 -->
    <div class="sb-search">
        <span class="sb-search-icon">🔍</span>
        <span class="sb-search-txt">대화 검색...</span>
    </div>

    <!-- 대화 목록 -->
    {current_html}
    <div class="sb-group-label">오늘</div>
    {today_html}
    <div class="sb-group-label">최근 7일</div>
    {week_html}

    <!-- 하단 메뉴 -->
    <div class="sb-divider">
        <div class="sb-bottom-item">⚙️ &nbsp;설정</div>
        <div class="sb-bottom-item">
            <div class="sb-avatar">V</div>
            Vault 사용자
        </div>
    </div>
</div>
"""


def render_user_msg(content: str) -> str:
    """사용자 메시지 버블 HTML"""
    safe = content.replace("<", "&lt;").replace(">", "&gt;")
    return f"""
<div class="msg-row user">
    <div class="user-bubble">{safe}</div>
    <div class="msg-avatar user-av">나</div>
</div>
"""


def render_bot_msg(content: str, show_followup: bool = True) -> str:
    """봇 응답 HTML — **굵게**, \n → <br> 처리"""
    # 마크다운 bold 처리
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", content)
    # 줄바꿈
    html = html.replace("\n", "<br>")

    followup = '<div class="bot-followup">💬 다른 도움이 필요하신가요?</div>' if show_followup else ""

    return f"""
<div class="msg-row bot">
    <div class="msg-avatar bot-av">🤖</div>
    <div class="bot-wrap">
        <div class="bot-label">
            <span class="bot-label-name">LMS 도우미</span>
            <span class="bot-label-badge">✦ AI</span>
        </div>
        <div class="bot-bubble">{html}</div>
        {followup}
        <div class="bot-actions">
            <button class="b-btn" title="도움이 됐어요">👍</button>
            <button class="b-btn" title="도움이 안 됐어요">👎</button>
            <button class="b-btn" title="복사">⧉</button>
            <button class="regen-btn" title="다시 생성">↺ Regenerate</button>
        </div>
    </div>
</div>
"""


def render_welcome() -> str:
    """환영 화면 HTML"""
    return """
<div class="welcome-screen">
    <div class="welcome-logo">🎓</div>
    <div class="welcome-h">Veeva Vault Training FAQ 도우미</div>
    <div class="welcome-sub">
        LMS 관련 궁금한 점을 무엇이든 물어보세요.<br>
        아래 예시 질문을 클릭하거나 직접 입력하세요.
    </div>
</div>
"""

# ─────────────────────────────────────────────────────────────
# 5. 메인 앱
# ─────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="LMS FAQ 도우미",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_session_state()

    # CSS 주입
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # ── 사이드바 ─────────────────────────────────────────────
    with st.sidebar:
        st.markdown(build_sidebar_html(), unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("🗑️ 대화 초기화", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.question_log = []
            st.rerun()
        # FAQ 통계
        total = len(FAQ_DATA)
        cats = len(set(i["category"] for i in FAQ_DATA))
        st.markdown(
            f"<div style='font-size:11px;color:#C4C9D4;text-align:center;margin-top:10px;'>"
            f"FAQ {total}개 · 카테고리 {cats}개</div>",
            unsafe_allow_html=True,
        )

    # ── 메인 레이아웃 ────────────────────────────────────────
    # 채팅 메시지 영역
    chat_area = st.container()
    with chat_area:
        # 흰 배경 카드 열기
        st.markdown(
            "<div style='background:white;border-radius:20px 20px 0 0;"
            "padding:24px 48px 16px;min-height:65vh;max-height:65vh;"
            "overflow-y:auto;box-shadow:0 -2px 24px rgba(91,106,240,0.07);'>",
            unsafe_allow_html=True,
        )

        if not st.session_state.chat_history:
            st.markdown(render_welcome(), unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(render_user_msg(msg["content"]), unsafe_allow_html=True)
                else:
                    st.markdown(
                        render_bot_msg(msg["content"], msg.get("show_followup", True)),
                        unsafe_allow_html=True,
                    )

        st.markdown("</div>", unsafe_allow_html=True)

    # ── 입력 영역 ─────────────────────────────────────────────
    st.markdown(
        "<div style='background:white;padding:12px 48px 20px;"
        "border-top:1px solid #F0F1F8;border-radius:0 0 20px 20px;'>",
        unsafe_allow_html=True,
    )

    # 예시 질문 버튼
    ex_cols = st.columns(3)
    labels = ["📚 " + EXAMPLE_QUESTIONS[0], "📝 " + EXAMPLE_QUESTIONS[1], "🔒 " + EXAMPLE_QUESTIONS[2]]
    for col, label, q in zip(ex_cols, labels, EXAMPLE_QUESTIONS):
        with col:
            if st.button(label, key=f"ex_{q[:10]}"):
                st.session_state.pending_input = q
                st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # 입력 폼
    with st.form("chat_form", clear_on_submit=True):
        f_cols = st.columns([11, 1])
        with f_cols[0]:
            default = st.session_state.get("pending_input", "")
            user_input = st.text_input(
                "msg",
                value=default,
                placeholder="✦  What's in your mind?  궁금한 점을 입력하세요...",
                label_visibility="collapsed",
            )
        with f_cols[1]:
            submitted = st.form_submit_button("전송 ➤")

    st.markdown("</div>", unsafe_allow_html=True)

    # pending 초기화
    if st.session_state.get("pending_input"):
        st.session_state.pending_input = ""

    # ── 질문 처리 ─────────────────────────────────────────────
    if submitted and user_input and user_input.strip():
        q = user_input.strip()

        st.session_state.chat_history.append({"role": "user", "content": q})

        answer = get_bot_response(q)
        show_fu = "찾지 못했습니다" not in answer

        st.session_state.chat_history.append({
            "role": "bot",
            "content": answer,
            "show_followup": show_fu,
        })

        st.session_state.question_log.append({
            "time": datetime.now().strftime("%H:%M"),
            "q": q,
            "a": answer[:60] + "…",
        })

        st.rerun()


# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
