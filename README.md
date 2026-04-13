[README.md](https://github.com/user-attachments/files/26663799/README.md)
# 🎓 Veeva Vault Training FAQ 챗봇

Veeva Vault Training (LMS) 사용자를 위한 FAQ 기반 Streamlit 챗봇입니다.

## 📋 주요 기능
- FAQ 키워드 매칭 기반 자동 응답 (외부 API 없음)
- 채팅 UI (사용자/봇 구분, 이전 대화 유지)
- 예시 질문 버튼 3개 제공
- 질문 로그 저장 (사이드바)
- 답변 후 "다른 도움이 필요하신가요?" 문구 출력
- 대화 초기화 버튼

## 🗂️ FAQ 카테고리 (총 26개 항목)
| 카테고리 | 항목 수 |
|---|---|
| 교육 이수 | 6개 |
| 퀴즈 | 3개 |
| 커리큘럼 | 3개 |
| 사전 이수 조건 | 1개 |
| 대체 교육 | 2개 |
| 이러닝 | 2개 |
| 강의식 교육 | 3개 |
| 현장 교육 | 2개 |
| 교육 영향 평가(TRIA) | 2개 |
| 교육 변경 요청 | 1개 |
| 보충 자료 | 1개 |
| 교육 반복 | 1개 |
| 일반 | 3개 |

## 🚀 실행 방법

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 챗봇 실행
```bash
streamlit run lms_chatbot.py
```

### 3. 브라우저 접속
실행 후 자동으로 `http://localhost:8501` 이 열립니다.

## 📁 파일 구조
```
lms_chatbot.py       ← 메인 챗봇 앱 (FAQ 데이터 포함)
requirements.txt     ← 필요 패키지
README.md            ← 사용 안내
```

## 🔒 보안
- 외부 API 호출 없음
- 내부 문서 업로드 없음
- 모든 FAQ 데이터는 코드 내부에 정의

## 📌 FAQ 추가 방법
`lms_chatbot.py` 상단의 `FAQ_DATA` 리스트에 아래 형식으로 항목을 추가하세요:
```python
{
    "question": "질문 내용",
    "keywords": ["키워드1", "키워드2"],
    "answer": "답변 내용 (줄바꿈에 \\n 사용)",
    "category": "카테고리명"
}
```

## 📞 참고 출처
- [Veeva Vault Training Help](https://quality.veevavault.help/en/lr/50953/)
