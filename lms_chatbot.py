"""
=============================================================
Veeva Vault Training (LMS) FAQ 챗봇 - Streamlit 웹 애플리케이션
=============================================================
대상: Veeva Vault Training LMS 일반 사용자
기능: FAQ 기반 키워드 매칭 챗봇 (외부 API 없음, 내부 데이터 처리)
실행: streamlit run lms_chatbot.py
=============================================================
"""

import streamlit as st
import re
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# 1. FAQ 데이터 정의
#    출처: Veeva Vault Help (quality.veevavault.help)
#    카테고리: 교육 이수, 퀴즈, 커리큘럼, 사전 이수, 대체 교육,
#              이러닝, ILT, OJT, TRIA, 일반
# ─────────────────────────────────────────────────────────────
FAQ_DATA = [

    # ── 교육 이수 (Completing Training Assignments) ──────────────
    {
        "question": "교육 이수는 어떻게 하나요?",
        "keywords": ["이수", "완료", "어떻게", "방법", "교육 완료", "training assignment"],
        "answer": (
            "교육 이수 방법:\n"
            "① My Tasks 또는 Learner Homepage에서 교육 과제를 클릭합니다.\n"
            "② 문서를 읽은 후 전자 서명(eSignature)을 입력하여 완료 처리합니다.\n"
            "③ 퀴즈나 강의 참석이 필요한 경우 해당 단계를 추가로 완료해야 합니다."
        ),
        "category": "교육 이수"
    },
    {
        "question": "교육이 완료됐는데 이수 처리가 안 돼요.",
        "keywords": ["이수 안 됨", "완료 안 됨", "처리 안 됨", "이수 처리", "반영 안 됨", "완료했는데"],
        "answer": (
            "이수가 반영되지 않는 주요 원인:\n"
            "① 전자 서명(eSignature)을 입력하지 않은 경우 → 다시 과제를 열어 서명을 완료하세요.\n"
            "② 퀴즈 미통과 또는 ILT 세션 미참석 상태인 경우 → 해당 단계를 완료하세요.\n"
            "③ 시스템 처리 지연이 있을 수 있으므로 잠시 후 페이지를 새로고침하세요."
        ),
        "category": "교육 이수"
    },
    {
        "question": "모바일에서 교육을 들을 수 있나요?",
        "keywords": ["모바일", "휴대폰", "스마트폰", "앱", "mobile", "vault mobile"],
        "answer": (
            "모바일 교육 수강 방법:\n"
            "① 모바일 브라우저 또는 Vault Mobile 앱을 통해 교육 과제에 접근할 수 있습니다.\n"
            "② 여러 문서가 있는 경우 'View Training'을 탭하여 시작하고, 'Next'로 다음 문서로 이동합니다.\n"
            "③ 모바일에서 완료 가능한 과제는 'Complete' 버튼이 활성화됩니다. 단, 대리 접속자는 타인 대신 퀴즈 응시나 이수 처리가 불가합니다."
        ),
        "category": "교육 이수"
    },
    {
        "question": "교육 과제가 Learner Homepage에 안 보여요.",
        "keywords": ["안 보임", "안보임", "없음", "안 보여", "목록에 없", "learner homepage", "과제 없음"],
        "answer": (
            "교육이 보이지 않는 경우 확인사항:\n"
            "① Learner Homepage 또는 My Tasks 화면의 필터·탭 설정을 확인하세요 (예: '완료됨' 필터 해제).\n"
            "② 사전 이수(Prerequisite) 교육이 완료되지 않아 잠겨 있을 수 있습니다.\n"
            "③ 교육 과제가 아직 배정되지 않았을 수 있으니 관리자에게 문의하세요."
        ),
        "category": "교육 이수"
    },
    {
        "question": "교육 마감일이 언제인가요?",
        "keywords": ["마감일", "기한", "due date", "마감", "기한 초과", "언제까지"],
        "answer": (
            "교육 마감일 확인 방법:\n"
            "① Learner Homepage 또는 My Tasks에서 각 교육 과제의 Due Date 항목을 확인하세요.\n"
            "② 마감일이 없는 경우, 관리자가 선택적(Optional) 마감일로 설정한 것일 수 있습니다.\n"
            "③ 마감일이 지난 과제는 'Overdue' 상태로 표시됩니다."
        ),
        "category": "교육 이수"
    },
    {
        "question": "이전에 읽은 문서인데 또 교육을 받아야 하나요?",
        "keywords": ["재교육", "retraining", "또", "다시", "반복", "이미 읽음"],
        "answer": (
            "재교육이 배정되는 주요 이유:\n"
            "① 문서가 새 버전으로 개정되어 내용이 변경된 경우 새 교육 과제가 자동 생성됩니다.\n"
            "② Training Recurrence(정기 반복 교육)가 설정된 경우 주기적으로 재교육이 부여됩니다.\n"
            "③ 관리자가 별도로 Retraining을 발행한 경우입니다. 과제 세부사항에서 'Creation Reason'을 확인하세요."
        ),
        "category": "교육 이수"
    },

    # ── 퀴즈 (Training Quizzes) ────────────────────────────────
    {
        "question": "퀴즈에서 떨어졌어요. 다시 볼 수 있나요?",
        "keywords": ["퀴즈", "quiz", "떨어짐", "불합격", "failed", "재시험", "다시 볼"],
        "answer": (
            "퀴즈 재응시 안내:\n"
            "① 퀴즈 불합격 시 'Failed' 상태로 기록되며, 새 퀴즈 인스턴스를 통해 재응시할 수 있습니다.\n"
            "② 이전 응시 기록과는 독립적으로 새로운 퀴즈가 생성됩니다.\n"
            "③ 최대 재응시 횟수가 설정된 경우, 횟수 초과 시 관리자에게 문의하세요."
        ),
        "category": "퀴즈"
    },
    {
        "question": "퀴즈 통과 점수가 몇 점인가요?",
        "keywords": ["통과 점수", "합격 점수", "passing score", "몇 점", "기준 점수", "퀴즈 점수"],
        "answer": (
            "퀴즈 합격 기준 확인 방법:\n"
            "① 퀴즈 시작 전 또는 퀴즈 페이지에서 합격 기준 점수(Passing Score)를 확인할 수 있습니다.\n"
            "② 합격 기준은 관리자가 설정하므로 교육마다 다를 수 있습니다.\n"
            "③ 정확한 기준을 모를 경우 교육 담당자(Training Admin)에게 문의하세요."
        ),
        "category": "퀴즈"
    },
    {
        "question": "퀴즈가 제출이 안 돼요.",
        "keywords": ["퀴즈 제출", "submit", "제출 안 됨", "버튼 없음", "퀴즈 완료 안 됨"],
        "answer": (
            "퀴즈 제출 문제 해결 방법:\n"
            "① 모든 문항에 답변했는지 확인하세요 (미답변 문항이 있으면 제출 불가).\n"
            "② 브라우저를 새로고침한 후 다시 시도하거나, 다른 브라우저(Chrome 권장)를 사용해보세요.\n"
            "③ 문제가 지속되면 관리자에게 스크린샷과 함께 문의하세요."
        ),
        "category": "퀴즈"
    },

    # ── 커리큘럼 (Curricula) ──────────────────────────────────
    {
        "question": "커리큘럼이란 무엇인가요?",
        "keywords": ["커리큘럼", "curriculum", "curricula", "교육 과정", "과정"],
        "answer": (
            "커리큘럼(Curriculum) 개요:\n"
            "① 커리큘럼은 관련 교육 요건(Training Requirements)을 묶어 관리하는 단위입니다.\n"
            "② 커리큘럼 내 교육은 순서(Sequencing)가 정해질 수 있어, 앞 단계 이수 후 다음 교육이 열립니다.\n"
            "③ 커리큘럼 이수 현황은 Curriculum Completion Tracking 화면에서 확인할 수 있습니다."
        ),
        "category": "커리큘럼"
    },
    {
        "question": "커리큘럼의 다음 교육이 잠겨서 열리지 않아요.",
        "keywords": ["잠김", "locked", "다음 교육", "순서", "sequencing", "열리지 않음", "커리큘럼 순서"],
        "answer": (
            "커리큘럼 순서 잠금 해제 방법:\n"
            "① 커리큘럼 내 교육은 순서(Sequencing)가 설정된 경우 이전 교육을 완료해야 다음이 열립니다.\n"
            "② 이전 단계 교육의 이수 상태를 확인하고 완료하세요.\n"
            "③ 사전 이수(Prerequisite)가 별도로 설정된 경우도 있으니 교육 세부사항을 확인하세요."
        ),
        "category": "커리큘럼"
    },
    {
        "question": "커리큘럼 이수 현황은 어디서 보나요?",
        "keywords": ["커리큘럼 현황", "이수 현황", "진행 상황", "completion tracking", "완료 현황"],
        "answer": (
            "커리큘럼 이수 현황 확인:\n"
            "① Learner Homepage 또는 Curriculum Completion Tracking 화면에서 확인할 수 있습니다.\n"
            "② 각 교육 과제의 완료 여부와 전체 커리큘럼 진행률을 볼 수 있습니다.\n"
            "③ 상세 현황은 My Tasks 탭에서도 확인 가능합니다."
        ),
        "category": "커리큘럼"
    },

    # ── 사전 이수 조건 (Prerequisites) ──────────────────────────
    {
        "question": "사전 이수 조건이 있는 교육은 어떻게 되나요?",
        "keywords": ["사전 이수", "prerequisite", "선수 교육", "먼저", "선행"],
        "answer": (
            "사전 이수(Prerequisite) 교육 안내:\n"
            "① 특정 교육은 다른 교육을 먼저 이수해야 접근할 수 있습니다.\n"
            "② 사전 이수가 완료되지 않으면 해당 교육 과제가 잠기거나 목록에 표시되지 않을 수 있습니다.\n"
            "③ 어떤 교육이 사전 이수 조건인지 모를 경우 교육 담당자에게 문의하세요."
        ),
        "category": "사전 이수 조건"
    },

    # ── 대체 교육 (Substitute Training) ─────────────────────────
    {
        "question": "대체 교육이 배정됐는데 뭔가요?",
        "keywords": ["대체 교육", "substitute", "대체", "다른 교육", "대신"],
        "answer": (
            "대체 교육(Substitute Training) 안내:\n"
            "① 대체 교육은 원래 교육(Primary) 대신 배정되는 대체 교육 과제입니다.\n"
            "② 언어, 역할, 지역 등 조건에 따라 관리자가 규칙을 설정해 자동 배정됩니다.\n"
            "③ 대체 교육을 이수하면 원래 교육 요건도 충족된 것으로 처리됩니다."
        ),
        "category": "대체 교육"
    },
    {
        "question": "동등 교육(Equivalent)으로 이수 인정이 되나요?",
        "keywords": ["동등", "equivalent", "인정", "크레딧", "동등 교육"],
        "answer": (
            "동등 교육(Equivalent Rule) 인정 안내:\n"
            "① 관리자가 Equivalent Rule을 설정한 경우, 특정 교육 이수 시 관련 다른 교육도 함께 이수 처리될 수 있습니다.\n"
            "② 양방향(Bi-directional) 설정 시, 두 교육 중 하나만 완료해도 양쪽 모두 이수 인정됩니다.\n"
            "③ 해당 교육에 동등 인정 규칙이 있는지 교육 담당자에게 확인하세요."
        ),
        "category": "대체 교육"
    },

    # ── 이러닝 (E-Learning) ────────────────────────────────────
    {
        "question": "이러닝(E-Learning)이 실행이 안 돼요.",
        "keywords": ["이러닝", "e-learning", "elearning", "실행 안 됨", "열리지 않음", "콘텐츠 오류", "동영상"],
        "answer": (
            "이러닝 실행 오류 해결 방법:\n"
            "① 지원 브라우저(Chrome 최신 버전 권장)를 사용하고 있는지 확인하세요.\n"
            "② 팝업 차단 설정을 해제하거나, 브라우저 캐시를 삭제한 후 다시 시도하세요.\n"
            "③ 문제가 지속되면 IT 또는 교육 관리자에게 브라우저 정보와 오류 메시지를 전달하세요."
        ),
        "category": "이러닝"
    },
    {
        "question": "이러닝을 다 봤는데 완료 처리가 안 돼요.",
        "keywords": ["이러닝 완료", "scorm", "완료 처리 안 됨", "다 봤는데", "이수 안 됨 이러닝"],
        "answer": (
            "이러닝 완료 처리 확인사항:\n"
            "① 이러닝 콘텐츠 내 모든 슬라이드·섹션을 끝까지 진행했는지 확인하세요.\n"
            "② 완료 기준이 '전체 열람' 또는 '퀴즈 통과'인 경우 해당 조건을 충족해야 합니다.\n"
            "③ 이러닝 창을 닫기 전에 콘텐츠 내 완료 버튼(Finish/Exit)을 클릭했는지 확인하세요."
        ),
        "category": "이러닝"
    },

    # ── 강의식 교육 (Instructor-Led Training, ILT) ──────────────
    {
        "question": "집합 교육(ILT)은 어떻게 등록하나요?",
        "keywords": ["집합 교육", "ilt", "instructor-led", "강의", "오프라인 교육", "등록", "세션"],
        "answer": (
            "강의식 교육(ILT) 등록 방법:\n"
            "① Learner Homepage 또는 My Tasks에서 해당 ILT 교육 과제를 확인하세요.\n"
            "② 세션 일정을 선택하여 등록(Enroll)하거나, 관리자가 등록을 대행할 수 있습니다.\n"
            "③ 등록 후 이메일 알림이 발송되며, 세션 참석 후 강사가 출석 확인을 하면 이수 처리됩니다."
        ),
        "category": "강의식 교육"
    },
    {
        "question": "ILT 세션에 참석했는데 이수가 안 됐어요.",
        "keywords": ["ilt 이수", "집합 교육 이수", "출석 확인", "참석 확인", "세션 완료"],
        "answer": (
            "ILT 이수 처리 미완료 시 확인사항:\n"
            "① 강사(또는 관리자)가 출석을 확인(Mark Attendance)해야 이수 처리됩니다.\n"
            "② 출석이 확인됐는지 교육 담당자에게 문의하세요.\n"
            "③ 추가로 전자 서명이나 퀴즈가 요구되는 경우 해당 단계도 완료해야 합니다."
        ),
        "category": "강의식 교육"
    },

    # ── 현장 교육 / 외부 교육 (OJT / External Training) ──────────
    {
        "question": "현장 교육(OJT)은 어떻게 이수 처리하나요?",
        "keywords": ["ojt", "현장 교육", "on-the-job", "현장", "실습"],
        "answer": (
            "현장 교육(OJT) 이수 처리 방법:\n"
            "① OJT 과제를 열고 현장에서 교육을 완료한 후 전자 서명을 제출합니다.\n"
            "② 평가자(Assessor) 또는 관리자가 별도로 승인해야 이수 처리되는 경우도 있습니다.\n"
            "③ 이수 방법이 불확실하면 교육 담당자에게 OJT 완료 절차를 문의하세요."
        ),
        "category": "현장 교육"
    },
    {
        "question": "외부 교육 이수 결과를 시스템에 등록하고 싶어요.",
        "keywords": ["외부 교육", "external training", "외부 과정", "외부 이수", "사외 교육"],
        "answer": (
            "외부 교육 이수 등록 방법:\n"
            "① 관리자가 External Training Requirement로 설정한 과제가 있는 경우, 이수 증빙을 업로드하여 완료 처리할 수 있습니다.\n"
            "② 외부 교육이 시스템에 없는 경우 교육 담당자에게 과제 생성을 요청하세요.\n"
            "③ 이수 증빙(수료증 등)을 미리 준비해 두세요."
        ),
        "category": "현장 교육"
    },

    # ── 퍼실리테이션 교육 (Facilitated Training) ──────────────
    {
        "question": "Facilitated Training(퍼실리테이션 교육)이 뭔가요?",
        "keywords": ["facilitated", "퍼실리테이션", "facilitated training", "진행자"],
        "answer": (
            "Facilitated Training 안내:\n"
            "① 퍼실리테이션 교육은 진행자(Facilitator)가 이끄는 그룹 학습 또는 워크숍 형태의 교육입니다.\n"
            "② 학습자는 배정된 세션에 참여하고, 진행자가 완료 처리를 합니다.\n"
            "③ 자신의 과제 목록에서 해당 교육을 확인하거나 교육 담당자에게 문의하세요."
        ),
        "category": "강의식 교육"
    },

    # ── 교육 영향 평가 (TRIA) ──────────────────────────────────
    {
        "question": "TRIA가 무엇인가요?",
        "keywords": ["tria", "영향 평가", "training requirement impact", "문서 변경"],
        "answer": (
            "TRIA(Training Requirement Impact Assessment) 안내:\n"
            "① TRIA는 문서가 변경될 때 해당 변경이 교육 요건에 미치는 영향을 평가하는 프로세스입니다.\n"
            "② 문서 개정 후 재교육이 필요한지 여부를 결정하는 데 사용됩니다.\n"
            "③ 일반 사용자는 TRIA 결과에 따라 자동으로 교육 과제가 배정될 수 있습니다."
        ),
        "category": "교육 영향 평가"
    },
    {
        "question": "문서가 개정됐는데 왜 교육이 새로 생겼나요?",
        "keywords": ["문서 개정", "새 교육", "버전 변경", "업데이트 교육", "문서 변경 교육"],
        "answer": (
            "문서 개정 후 교육 재배정 이유:\n"
            "① 문서가 새 버전으로 승인되면 TRIA 또는 자동화 규칙에 의해 재교육 과제가 생성됩니다.\n"
            "② 변경된 내용을 숙지했음을 확인하는 전자 서명이 필요합니다.\n"
            "③ Delta 교육(변경 사항 중심)이 배정된 경우 전체 문서 대신 변경 부분만 학습하면 됩니다."
        ),
        "category": "교육 영향 평가"
    },

    # ── 교육 변경 요청 (Training Change Request) ────────────────
    {
        "question": "교육 변경 요청(Training Change Request)은 어떻게 하나요?",
        "keywords": ["변경 요청", "training change request", "tcr", "교육 수정 요청"],
        "answer": (
            "교육 변경 요청(TCR) 안내:\n"
            "① Training Change Request는 교육 요건이나 교육 과제를 변경하기 위한 공식 요청 프로세스입니다.\n"
            "② 교육 담당자(Training Admin)에게 변경 요청을 제출하거나, 시스템 내 TCR 기능을 활용하세요.\n"
            "③ 일반 사용자는 보통 변경 요청 제출 권한이 제한되므로 관리자를 통해 진행하세요."
        ),
        "category": "교육 변경 요청"
    },

    # ── 보충 자료 (Supplemental Materials) ──────────────────────
    {
        "question": "보충 자료는 어디서 볼 수 있나요?",
        "keywords": ["보충 자료", "supplemental", "참고 자료", "추가 자료"],
        "answer": (
            "보충 자료(Supplemental Materials) 확인 방법:\n"
            "① 교육 과제 상세 페이지 내 '보충 자료(Supplemental Materials)' 섹션에서 확인할 수 있습니다.\n"
            "② 보충 자료는 교육 이수와 무관하게 참고용으로 제공되는 문서입니다.\n"
            "③ 목록에 없는 경우 교육 담당자에게 문의하세요."
        ),
        "category": "보충 자료"
    },

    # ── 교육 반복 (Training Recurrence) ─────────────────────────
    {
        "question": "교육 주기(Recurrence)가 뭔가요?",
        "keywords": ["반복", "recurrence", "주기", "정기 교육", "재교육 주기"],
        "answer": (
            "교육 반복(Training Recurrence) 안내:\n"
            "① 반복 교육은 일정 주기(예: 1년마다)로 자동 재배정되는 교육 과제입니다.\n"
            "② 이전 이수 완료 날짜를 기준으로 다음 교육이 생성됩니다.\n"
            "③ Refresher 교육이 설정된 경우, 전체 교육 대신 핵심 내용 복습 교육이 배정될 수 있습니다."
        ),
        "category": "교육 반복"
    },

    # ── 알림 / 일반 ────────────────────────────────────────────
    {
        "question": "교육 관련 이메일 알림이 오지 않아요.",
        "keywords": ["알림", "이메일", "notification", "메일", "공지"],
        "answer": (
            "교육 알림 미수신 시 확인사항:\n"
            "① 스팸 메일함 또는 '정크 메일'에 Veeva 알림이 필터링됐는지 확인하세요.\n"
            "② Vault 계정의 이메일 주소가 올바르게 등록됐는지 프로필에서 확인하세요.\n"
            "③ 알림 설정이 비활성화된 경우 시스템 관리자에게 활성화를 요청하세요."
        ),
        "category": "일반"
    },
    {
        "question": "Vault에 로그인이 안 돼요.",
        "keywords": ["로그인", "login", "접속 불가", "비밀번호", "password", "계정"],
        "answer": (
            "Vault 로그인 문제 해결:\n"
            "① 비밀번호 오입력이 잦으면 계정이 잠길 수 있습니다 → 관리자에게 계정 잠금 해제를 요청하세요.\n"
            "② '비밀번호 재설정(Forgot Password)' 기능을 사용해 비밀번호를 재설정하세요.\n"
            "③ SSO(싱글 사인온) 환경이라면 사내 IT팀에 문의하세요."
        ),
        "category": "일반"
    },
    {
        "question": "내 교육 이수 기록은 어디서 확인하나요?",
        "keywords": ["이수 기록", "이수 현황", "기록 확인", "이수 내역", "완료 기록", "training record"],
        "answer": (
            "교육 이수 기록 확인 방법:\n"
            "① Learner Homepage의 '완료된 교육(Completed)' 탭에서 이수한 교육 목록을 확인할 수 있습니다.\n"
            "② My Tasks에서 상태 필터를 '완료(Completed)'로 설정해도 확인 가능합니다.\n"
            "③ 상세 이수 이력(날짜·서명 정보)은 각 교육 과제 상세 페이지에서 확인하세요."
        ),
        "category": "일반"
    },
    {
        "question": "교육 담당자에게 어떻게 연락하나요?",
        "keywords": ["담당자", "문의", "연락", "관리자", "admin", "도움"],
        "answer": (
            "교육 담당자 문의 방법:\n"
            "① 회사 내부 교육 담당 부서(HR 또는 Quality/Compliance팀)로 연락하세요.\n"
            "② Vault 시스템 내 Help 또는 Support 링크를 통해 티켓을 제출할 수 있습니다.\n"
            "③ 긴급한 경우 시스템 관리자(Vault Admin)에게 직접 연락하세요."
        ),
        "category": "일반"
    },
]


# ─────────────────────────────────────────────────────────────
# 2. 핵심 함수 정의
# ─────────────────────────────────────────────────────────────

def normalize_text(text: str) -> str:
    """
    사용자 입력 텍스트를 정규화합니다.
    - 소문자 변환
    - 특수문자 제거 (한글·영문·숫자·공백 유지)
    """
    text = text.lower()
    text = re.sub(r"[^\w\s가-힣]", " ", text)
    return text.strip()


def calculate_match_score(user_input: str, faq_item: dict) -> int:
    """
    사용자 입력과 FAQ 항목 간의 키워드 매칭 점수를 계산합니다.
    - 키워드 완전 일치: 2점
    - 키워드 부분 포함(또는 역포함): 1점
    반환: 정수형 점수
    """
    score = 0
    normalized_input = normalize_text(user_input)

    for keyword in faq_item["keywords"]:
        normalized_keyword = normalize_text(keyword)
        if normalized_keyword == normalized_input:
            score += 3  # 완전 일치 보너스
        elif normalized_keyword in normalized_input:
            score += 2  # 키워드가 입력에 포함
        elif normalized_input in normalized_keyword:
            score += 1  # 입력이 키워드에 포함 (부분 매칭)

    return score


def find_best_faq(user_input: str, faq_data: list, min_score: int = 1) -> dict | None:
    """
    사용자 입력에 가장 잘 매칭되는 FAQ를 반환합니다.
    - 점수 기준 정렬 후 최고 점수 FAQ 반환
    - 최소 점수(min_score) 미달 시 None 반환
    """
    scores = []
    for item in faq_data:
        score = calculate_match_score(user_input, item)
        scores.append((score, item))

    # 점수 내림차순 정렬
    scores.sort(key=lambda x: x[0], reverse=True)

    best_score, best_item = scores[0]
    if best_score >= min_score:
        return best_item
    return None


def get_bot_response(user_input: str) -> str:
    """
    사용자 입력을 받아 챗봇 응답 문자열을 반환합니다.
    - FAQ 매칭 성공 시 해당 답변 반환
    - 매칭 실패 시 안내 메시지 반환
    """
    if not user_input.strip():
        return "질문을 입력해 주세요."

    result = find_best_faq(user_input, FAQ_DATA, min_score=1)

    if result:
        return result["answer"]
    else:
        return "관련된 정보를 찾지 못했습니다. 다른 표현으로 질문해주세요."


def log_question(question: str, answer: str) -> None:
    """
    사용자 질문과 챗봇 답변을 세션 로그에 저장합니다.
    st.session_state.question_log 리스트에 딕셔너리로 기록합니다.
    """
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "question": question,
        "answer": answer[:80] + "..." if len(answer) > 80 else answer,
    }
    st.session_state.question_log.append(log_entry)


def render_chat_message(role: str, content: str) -> None:
    """
    채팅 메시지를 역할(role)에 따라 스타일링하여 렌더링합니다.
    - role: "user" 또는 "bot"
    """
    if role == "user":
        st.markdown(
            f"""
            <div style="
                display: flex;
                justify-content: flex-end;
                margin: 6px 0;
            ">
                <div style="
                    background: #0055A4;
                    color: white;
                    padding: 10px 16px;
                    border-radius: 18px 18px 4px 18px;
                    max-width: 75%;
                    font-size: 14px;
                    line-height: 1.5;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                ">{content}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        # 줄바꿈(\n) → HTML <br> 변환
        formatted = content.replace("\n", "<br>")
        st.markdown(
            f"""
            <div style="
                display: flex;
                justify-content: flex-start;
                margin: 6px 0;
            ">
                <div style="
                    font-size: 22px;
                    margin-right: 8px;
                    align-self: flex-end;
                ">🤖</div>
                <div style="
                    background: #F1F3F5;
                    color: #212529;
                    padding: 10px 16px;
                    border-radius: 18px 18px 18px 4px;
                    max-width: 75%;
                    font-size: 14px;
                    line-height: 1.6;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                ">{formatted}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────
# 3. 세션 상태 초기화
# ─────────────────────────────────────────────────────────────

def init_session_state() -> None:
    """Streamlit 세션 상태를 초기화합니다."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []  # [{role, content}, ...]
    if "question_log" not in st.session_state:
        st.session_state.question_log = []  # 질문 로그 리스트
    if "pending_input" not in st.session_state:
        st.session_state.pending_input = ""  # 예시 버튼 클릭 시 임시 저장


# ─────────────────────────────────────────────────────────────
# 4. 예시 질문 버튼 처리
# ─────────────────────────────────────────────────────────────

EXAMPLE_QUESTIONS = [
    "📚 교육 이수는 어떻게 하나요?",
    "📝 퀴즈에서 떨어졌어요. 다시 볼 수 있나요?",
    "🔒 커리큘럼의 다음 교육이 잠겨서 열리지 않아요.",
]

def handle_example_click(question: str) -> None:
    """예시 질문 버튼 클릭 시 pending_input에 저장합니다."""
    st.session_state.pending_input = question.split(" ", 1)[1]  # 이모지 제거


# ─────────────────────────────────────────────────────────────
# 5. 메인 앱 렌더링
# ─────────────────────────────────────────────────────────────

def main() -> None:
    """Streamlit 앱 메인 함수"""

    # ── 페이지 설정 ────────────────────────────────────────────
    st.set_page_config(
        page_title="Veeva Vault Training FAQ 챗봇",
        page_icon="🎓",
        layout="centered",
    )

    # ── 세션 초기화 ─────────────────────────────────────────────
    init_session_state()

    # ── CSS 스타일 ──────────────────────────────────────────────
    st.markdown(
        """
        <style>
            /* 전체 배경 */
            .stApp { background-color: #FAFBFC; }

            /* 헤더 영역 */
            .chat-header {
                background: linear-gradient(135deg, #0055A4, #0077CC);
                color: white;
                padding: 20px 24px;
                border-radius: 12px;
                margin-bottom: 16px;
                text-align: center;
            }
            .chat-header h2 { margin: 0; font-size: 20px; }
            .chat-header p  { margin: 4px 0 0; font-size: 13px; opacity: 0.85; }

            /* 채팅 컨테이너 */
            .chat-container {
                background: white;
                border: 1px solid #DEE2E6;
                border-radius: 12px;
                padding: 16px;
                min-height: 380px;
                max-height: 480px;
                overflow-y: auto;
                margin-bottom: 12px;
            }

            /* 예시 질문 버튼 */
            .stButton > button {
                border-radius: 20px !important;
                font-size: 13px !important;
                padding: 6px 14px !important;
                border: 1px solid #0055A4 !important;
                color: #0055A4 !important;
                background: white !important;
                transition: 0.2s;
            }
            .stButton > button:hover {
                background: #0055A4 !important;
                color: white !important;
            }

            /* 입력창 */
            .stTextInput > div > div > input {
                border-radius: 24px !important;
                border: 1px solid #CED4DA !important;
                padding: 10px 18px !important;
                font-size: 14px !important;
            }

            /* 사이드바 */
            section[data-testid="stSidebar"] {
                background: #F8F9FA;
            }

            /* 구분선 */
            hr { margin: 10px 0; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ── 헤더 ────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="chat-header">
            <h2>🎓 Veeva Vault Training FAQ 챗봇</h2>
            <p>LMS 관련 질문을 입력하시면 바로 답변해드립니다.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── 예시 질문 버튼 ──────────────────────────────────────────
    st.markdown("**💡 예시 질문:**")
    cols = st.columns(len(EXAMPLE_QUESTIONS))
    for col, q in zip(cols, EXAMPLE_QUESTIONS):
        with col:
            if st.button(q, key=f"ex_{q}"):
                handle_example_click(q)

    st.markdown("---")

    # ── 채팅 히스토리 표시 ──────────────────────────────────────
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    if not st.session_state.chat_history:
        st.markdown(
            """
            <div style="text-align:center; color:#ADB5BD; padding: 40px 0; font-size:14px;">
                👆 위의 예시 질문을 클릭하거나<br>아래에 직접 질문을 입력해 보세요!
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        for msg in st.session_state.chat_history:
            render_chat_message(msg["role"], msg["content"])
            if msg["role"] == "bot" and msg.get("show_followup"):
                st.markdown(
                    '<div style="color:#6C757D; font-size:12px; margin-left:38px; margin-top:2px;">'
                    "💬 다른 도움이 필요하신가요?</div>",
                    unsafe_allow_html=True,
                )

    st.markdown("</div>", unsafe_allow_html=True)

    # ── 사용자 입력 폼 ──────────────────────────────────────────
    with st.form(key="chat_form", clear_on_submit=True):
        # 예시 버튼 클릭 시 pending_input 값 사전 로드
        default_val = st.session_state.get("pending_input", "")
        user_input = st.text_input(
            label="질문 입력",
            value=default_val,
            placeholder="예: 교육 이수는 어떻게 하나요?",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("전송 ➤", use_container_width=True)

    # 예시 버튼 pending 초기화
    if default_val:
        st.session_state.pending_input = ""

    # ── 질문 처리 ───────────────────────────────────────────────
    if submitted and user_input.strip():
        # 사용자 메시지 저장
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input.strip(),
        })

        # 챗봇 응답 생성
        bot_reply = get_bot_response(user_input.strip())

        # 챗봇 메시지 저장 (follow-up 문구 포함 여부 플래그)
        show_followup = "찾지 못했습니다" not in bot_reply
        st.session_state.chat_history.append({
            "role": "bot",
            "content": bot_reply,
            "show_followup": show_followup,
        })

        # 질문 로그 저장
        log_question(user_input.strip(), bot_reply)

        # 페이지 재렌더링
        st.rerun()

    # ── 사이드바: 질문 로그 & 안내 ─────────────────────────────
    with st.sidebar:
        st.markdown("### ℹ️ 챗봇 안내")
        st.markdown(
            """
            - **LMS**: Veeva Vault Training
            - **답변 방식**: FAQ 키워드 매칭
            - **관리자 기능** 질문은 교육 담당자에게 직접 문의하세요.
            """
        )
        st.markdown("---")

        # 카테고리 목록 표시
        categories = sorted(set(item["category"] for item in FAQ_DATA))
        st.markdown("### 📂 FAQ 카테고리")
        for cat in categories:
            count = sum(1 for item in FAQ_DATA if item["category"] == cat)
            st.markdown(f"- **{cat}** ({count}개)")

        st.markdown("---")

        # 질문 로그 표시
        st.markdown("### 📋 질문 로그")
        if st.session_state.question_log:
            for i, log in enumerate(reversed(st.session_state.question_log[-10:]), 1):
                with st.expander(f"#{len(st.session_state.question_log) - i + 1} {log['timestamp']}"):
                    st.write(f"**Q:** {log['question']}")
                    st.write(f"**A 요약:** {log['answer']}")
        else:
            st.info("아직 질문 기록이 없습니다.")

        # 대화 초기화 버튼
        st.markdown("---")
        if st.button("🗑️ 대화 초기화", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.question_log = []
            st.rerun()

        # FAQ 총 개수
        st.markdown(f"---\n*총 FAQ: {len(FAQ_DATA)}개*")


# ─────────────────────────────────────────────────────────────
# 6. 엔트리 포인트
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
