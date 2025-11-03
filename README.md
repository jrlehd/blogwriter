# 🚀 AI 블로그 올인원 시스템 (BlogWriter)

네이버 블로그 검색 데이터와 ChatGPT를 활용하여 키워드 분석부터 블로그 글 작성까지 자동화하는 데스크톱 애플리케이션

![Python](https://img.shields.io/badge/Python-3.13.4-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

## ✨ 주요 기능

- 🔍 **네이버 블로그 검색**: 키워드로 상위 30개 블로그 제목 자동 수집
- 🤖 **AI 제목 분석**: ChatGPT를 활용한 5가지 심층 분석
- ✍️ **최적화된 제목 생성**: 분석 기반 10개의 새로운 제목 자동 생성
- 📝 **블로그 글 자동 작성**: SEO/GEO 최적화된 완성된 글 생성
- 🎨 **현대적인 GUI**: CustomTkinter 기반 직관적 인터페이스
- 📊 **실시간 진행률 표시**: 작업 진행 상황 시각화

## 📋 목차

- [설치 방법](#설치-방법)
- [사용 방법](#사용-방법)
- [API 키 설정](#api-키-설정)
- [기능 상세](#기능-상세)
- [프로젝트 구조](#프로젝트-구조)
- [기술 스택](#기술-스택)
- [문제 해결](#문제-해결)
- [라이선스](#라이선스)

## 🔧 설치 방법

### 방법 1: 실행 파일 사용 (권장)

1. [Releases](https://github.com/your-username/blog-writer/releases) 페이지에서 최신 버전 다운로드
2. `BlogWriter.exe` 실행
3. `.env` 파일에 API 키 입력

### 방법 2: 소스 코드 실행

```bash
# 저장소 클론
git clone https://github.com/your-username/blog-writer.git
cd blog-writer

# 의존성 설치
pip install -r requirements.txt

# 실행
python BlogWriter.py
```

## 🔑 API 키 설정

### 1. `.env` 파일 생성

`.env.example` 파일을 복사하여 `.env` 파일을 만들고 실제 API 키를 입력하세요.

```bash
cp .env.example .env
```

### 2. API 키 발급

#### 네이버 검색 API
1. [네이버 개발자 센터](https://developers.naver.com/) 접속
2. 애플리케이션 등록
3. `검색` API 선택
4. Client ID와 Client Secret 발급

#### OpenAI API
1. [OpenAI Platform](https://platform.openai.com/) 접속
2. API Keys 메뉴에서 새 키 생성
3. API 키 복사

### 3. `.env` 파일 작성

```env
NAVER_CLIENT_ID=실제_클라이언트_ID
NAVER_CLIENT_SECRET_KEY=실제_시크릿_키
OPEN_AI_API_KEY=실제_OpenAI_키
```

⚠️ **주의**: `.env` 파일을 절대 GitHub에 업로드하지 마세요!

## 📖 사용 방법

### 기본 워크플로우

1. **키워드 입력**
   - 검색할 키워드를 입력창에 입력

2. **제목 생성**
   - "🚀 제목 생성 시작" 버튼 클릭
   - 네이버 검색 → AI 분석 → 제목 생성 자동 진행

3. **제목 선택**
   - 생성된 10개 제목 중 원하는 제목 체크
   - "✅ 선택 완료 → 글 작성 설정으로 이동" 클릭

4. **글 작성 설정**
   - GPT 모델 선택 (GPT-4o-mini, GPT-4o, GPT-4-turbo)
   - 글자 수 범위 설정 (최소: 500~5000자, 최대: 1000~10000자)

5. **블로그 글 생성**
   - "✍️ 블로그 글 작성 시작" 클릭
   - 저장 경로 선택
   - 자동으로 `.txt` 파일 생성

### 주요 탭 설명

| 탭 | 설명 |
|---|---|
| 🔍 검색 결과 | 네이버에서 수집한 30개 블로그 제목 |
| 📊 분석 결과 | ChatGPT가 분석한 5가지 인사이트 |
| ✨ 생성된 제목 | AI가 생성한 10개의 최적화된 제목 |
| ⚙️ 글 작성 설정 | GPT 모델 및 글자 수 설정 |
| 📝 작성 중인 글 | 현재 작성 중인 블로그 글 실시간 표시 |

## 🎯 기능 상세

### AI 제목 분석 (5가지)
1. **제목 형태 분석**: 길이, 문장 유형, 특수문자 사용 패턴
2. **핵심 키워드**: 주요 키워드 추출 및 조합 방식
3. **제목 구조**: 구조적 특징 및 순서 패턴
4. **콘텐츠 패턴**: 내용 유형 및 전략
5. **차별화 포인트**: 효과적인 제목의 공통점

### 블로그 글 최적화
- ✅ SEO 최적화 (키워드 자연스러운 배치)
- ✅ GEO 타겟팅 (지역 정보 포함)
- ✅ 구조화된 콘텐츠 (서론, 본론, 결론)
- ✅ 독자 참여 유도 (Call-to-Action)
- ✅ 마크다운 자동 제거

### 사용자 경험
- 📊 실시간 진행률 표시
- ⛔ 작성 중단 기능
- ✅ 제목 선택/해제 (체크박스)
- 🎨 현대적인 다크/라이트 테마

## 📂 프로젝트 구조

```
blog-writer/
├── BlogWriter.py              # 메인 애플리케이션
├── naversearch.py             # 네이버 검색 API 모듈
├── title_prompt.py            # 제목 분석/생성 프롬프트
├── blog_content_prompt.py     # 블로그 글 작성 프롬프트
├── .env                       # API 키 설정 (Git 제외)
├── .env.example               # API 키 템플릿
├── requirements.txt           # 의존성 패키지
├── .gitignore                 # Git 제외 파일 목록
└── README.md                  # 프로젝트 설명
```

## 🛠 기술 스택

### 프로그래밍 언어
- **Python 3.13.4**

### 주요 라이브러리
| 라이브러리 | 버전 | 용도 |
|-----------|------|------|
| customtkinter | ≥5.2.0 | 현대적인 GUI |
| openai | ≥1.0.0 | ChatGPT API |
| python-dotenv | 1.0.0 | 환경변수 관리 |
| httpx | ≥0.24.0 | HTTP 통신 |
| pyinstaller | ≥6.0.0 | exe 빌드 |

### 외부 API
- **Naver Search API**: 블로그 검색
- **OpenAI API**: GPT-4o-mini, GPT-4o, GPT-4-turbo

## 💾 실행 파일 빌드

```bash
pyinstaller --onefile --windowed --icon=NONE --add-data ".env;." --name=BlogWriter BlogWriter.py
```

빌드된 파일 위치: `dist/BlogWriter.exe`

## 🐛 문제 해결

### 오류: "네이버 API 인증 정보가 없습니다"
- `.env` 파일이 실행 파일과 같은 폴더에 있는지 확인
- `.env` 파일 형식 확인 (공백 없이 `KEY=VALUE`)

### OpenAI API 오류
- API 키가 유효한지 확인
- 계정에 크레딧이 남아있는지 확인
- 인터넷 연결 상태 확인

### GUI가 표시되지 않음
- Python 버전 확인 (3.8 이상 필요)
- `pip install -r requirements.txt` 재실행

## 📊 예상 비용 (OpenAI API)

| 모델 | 블로그 글 1개당 비용 |
|------|---------------------|
| GPT-4o-mini | ~$0.01-0.02 |
| GPT-4o | ~$0.10-0.20 |
| GPT-4-turbo | ~$0.05-0.10 |

## 🔐 보안 주의사항

- ⚠️ `.env` 파일을 절대 공개 저장소에 업로드하지 마세요
- ⚠️ API 키를 코드에 직접 작성하지 마세요
- ⚠️ 주기적으로 API 키를 재발급하세요
- ✅ `.gitignore`에 `.env` 파일이 포함되어 있는지 확인하세요

## 🚀 향후 개선 계획

- [ ] 이미지 자동 생성 및 삽입
- [ ] HTML 형식 출력 지원
- [ ] 워드프레스 자동 업로드
- [ ] 배치 모드 (여러 키워드 동시 처리)
- [ ] macOS/Linux 지원

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🤝 기여하기

이슈와 풀 리퀘스트는 언제나 환영합니다!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 문의

프로젝트에 대한 질문이나 제안사항이 있으시면 이슈를 등록해주세요.

## 🙏 감사의 말

- [Naver Developers](https://developers.naver.com/) - 검색 API 제공
- [OpenAI](https://openai.com/) - GPT API 제공
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - 현대적인 GUI 프레임워크

---

**⭐ 이 프로젝트가 도움이 되셨다면 스타를 눌러주세요!**

