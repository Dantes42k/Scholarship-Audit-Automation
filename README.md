# Scholarship Audit Automation System

RPA와 LLM을 활용한 장학금 심사 자동화 시스템



🎓 Scholarship Audit Automation System

&nbsp;	RPA와 LLM을 결합하여 비정형 행정 프로세스를 혁신하는 '비정형 서류 지능형 검토'



본 프로젝트는 대학 행정의 페인 포인트(Pain Point)인 '교육장학금 증빙 서류 심사'를 자동화하기 위해 구축된 인텔리전스 파이프라인입니다. 단순히 반복 업무를 줄이는 것을 넘어, 행정 지식을 코드북(Codebook) 기반의 정형 데이터로 전환하는 '지식 엔지니어링'을 지향합니다.



🚀 Key Achievements

* 효율성 혁신: 건당 처리 시간 50.4s -> 27.1s로 약 46% 단축.
* 정확도 확보: 1,800건의 코퍼스 분석을 통한 반려 사유 표준화(Codebook) 및 AI 매핑 정확도 99.9% 달성.
* 신뢰성 보장: PII(개인정보) 자동 비식별화 로직을 통한 데이터 보안 및 윤리적 행정 구현.





🛠 Tech Stack



* Language: Python v3.12



* Automation: Playwright, Chrome DevTools Protocol(CDP)



* Intelligence: Google Gemini 2.0 Flash, EasyOCR



* Data Handling: OpenPyXL, PDFPlumber, PyMuPDF





🏗 System Architecture

1. THE HAND (수집): Playwright를 통한 행정망 자동 접속 및 증빙 서류 강제 다운로드.
   
2. THE EYE (추출): OCR 하이브리드 엔진을 활용하여 이미지/PDF 내 텍스트 데이터화.
   
3. THE BRAIN (판단): Gemini 2.0 기반의 비정형 문서 의미 분석 및 코드북 기반 적합성 심사.
   
4. OUTPUT (리포트): 개인정보가 비식별화된 통합 검증 결과 보고서(Excel) 자동 생성.



💡 Engineering Hurdles \& Solutions

* CDP 기반 보안 우회: 브라우저의 자동 다운로드 차단 정책을 Chrome DevTools Protocol 주입으로 해결.



* Magic Number 파일 복원: .jsp로 저장되는 파일 헤더의 바이너리를 분석하여 실제 확장자(.pdf, .jpg)로 자동 변환.



* PII 비식별화 파이프라인: 분석 시에는 원본을 사용하되, 결과 저장 시 학번/성명/파일명/승인번호를 자동 마스킹 처리하여 보안 무결성 확보.
