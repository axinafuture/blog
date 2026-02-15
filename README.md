# Blog

Django 기반 개인 블로그 프로젝트. Editor.js 블록 에디터와 OpenAI 기반 AI 기능을 포함합니다.

## 주요 기능

- **Editor.js 블록 에디터** — 텍스트, 제목, 리스트, 이미지, 코드, 표, 인용 등 12가지 블록 타입 지원
- **AI 작문 제안** — 글 작성 중 문장을 자동 분석하여 개선안 제시, Tab 키로 즉시 적용
- **AI 블로그 요약** — 공개된 글을 분석하여 작가의 최근 관심사를 에세이 형식으로 정리
- **글 관리** — 카테고리/태그 분류, 공개/비공개, 메인 배치 설정, 인라인 편집
- **에세이 페이지** — 카테고리 필터링, 검색, 페이지네이션 (20개/페이지)
- **미리보기** — 작성 중인 글을 발행 형태로 미리 확인

## 기술 스택

- Python 3 / Django 5.2
- Editor.js (CDN)
- Bootstrap 5.3 (로컬)
- OpenAI API (gpt-4o, gpt-4o-mini)
- SQLite

## 설치 및 실행

```bash
# 저장소 클론
git clone https://github.com/axinafuture/blog.git
cd blog

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일에 OPENAI_API_KEY 입력

# 데이터베이스 마이그레이션
python manage.py migrate

# 관리자 계정 생성
python manage.py createsuperuser

# 서버 실행
python manage.py runserver
환경변수
.env 파일을 프로젝트 루트에 생성:


OPENAI_API_KEY=your-api-key-here
프로젝트 구조

blog/
├── config/          # Django 설정 (settings, urls)
├── structure/       # 메인 페이지, 에세이 목록/상세
├── writing/         # 글 작성, 관리, AI 기능
├── accounts/        # 로그인/로그아웃
├── templates/       # HTML 템플릿
├── static/          # CSS, JS, 폰트, 이미지
└── requirements.txt
