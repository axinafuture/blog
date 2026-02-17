# Blog

Django 기반 개인 블로그 프로젝트. Editor.js 블록 에디터와 OpenAI 기반 AI 기능을 포함합니다.

## 주요 기능

- **Editor.js 블록 에디터** — 텍스트, 제목, 리스트, 이미지, 코드, 표, 인용 등 12가지 블록 타입 지원
- **AI 작문 제안** — 글 작성 중 문장을 자동 분석하여 개선안 제시, Tab 키로 즉시 적용 (gpt-4o-mini)
- **AI 블로그 요약** — 공개된 글을 분석하여 작가의 최근 관심사를 에세이 형식으로 정리 (gpt-4o)
- **AI 프롬프트 편집** — 관리 페이지에서 시스템 메시지와 프롬프트를 직접 수정 가능
- **글 관리** — 카테고리/태그 분류, 공개/비공개, 메인 배치 설정, 인라인 편집, 글 현황 표시
- **에세이 페이지** — 카테고리 필터링, 검색, 페이지네이션 (20개/페이지), 글 상세 보기
- **메인 페이지** — 히어로 카드 레이아웃 + AI 추천 가이드 사이드바
- **미리보기** — 작성 중인 글을 발행 형태로 미리 확인
- **인증** — 로그인/로그아웃, 글 관련 페이지 접근 제한

## 기술 스택

- Python 3 / Django 5.2
- Editor.js 2.28 (로컬)
- Bootstrap 5.3 (로컬)
- OpenAI API (gpt-4o, gpt-4o-mini)
- SQLite (로컬) / MySQL (프로덕션)

## 로컬 설치

```bash
git clone https://github.com/axinafuture/blog.git
cd blog
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
echo "OPENAI_API_KEY=your-api-key-here" > .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## PythonAnywhere 배포

```bash
# Bash 콘솔에서
git clone https://github.com/axinafuture/blog.git
mkvirtualenv blog --python=python3.10
cd blog
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

Web 탭 설정:
- Source code: `/home/USERNAME/blog`
- Virtualenv: `/home/USERNAME/.virtualenvs/blog`
- WSGI: `load_dotenv` + `config.settings`
- Static: `/static/` → `/home/USERNAME/blog/staticfiles`
- Media: `/media/` → `/home/USERNAME/blog/media`

## 환경변수

`.env` 파일을 프로젝트 루트에 생성:

```
OPENAI_API_KEY=your-api-key-here

# 프로덕션 (PythonAnywhere)
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=USERNAME.pythonanywhere.com
MYSQL_NAME=USERNAME$dbname
MYSQL_USER=USERNAME
MYSQL_PASSWORD=your-mysql-password
MYSQL_HOST=USERNAME.mysql.pythonanywhere-services.com
```

## 프로젝트 구조

```
blog/
├── config/          # Django 설정 (settings, urls)
├── structure/       # 메인 페이지, 에세이 목록/상세
├── writing/         # 글 작성, 관리, AI 기능
├── accounts/        # 로그인/로그아웃
├── templates/       # HTML 템플릿
├── static/          # CSS, JS, 폰트, 이미지
└── requirements.txt
```

## 변경 이력

### 2026-02-17
- PythonAnywhere 배포 전환 (Railway에서 이전)
- MySQL 지원 추가, WhiteNoise 제거
- AI 제안 프롬프트 관리 페이지에서 편집 가능하도록 개선
- Google Fonts CDN으로 NotoSansKR 전환

### 2026-02-16
- 인라인 스타일을 페이지별 CSS 파일로 분리 (main.css, essay.css, manage.css)
- 클래스명 체계화 — essay-/article-/manage- 접두사로 충돌 방지
- Editor.js CDN을 로컬 static/js/로 전환 (오프라인 동작)
- 푸터 추가 (base.html)
- 관리 페이지 필터 드롭다운 한 줄 배치

### 2026-02-15
- AI 프롬프트 편집 기능 추가 (관리 페이지에서 시스템 메시지/프롬프트 수정 가능)
- 관리 페이지 AI 요약 카드 개선 (글 현황 표시, 생성 결과 즉시 표시)
- 에세이 상세 페이지 추가 (사이드바 유지, 글 내용 렌더링)
- 메인 페이지 카드 클릭 시 상세 페이지 연결
- AI 작문 제안 기능 추가 (글 작성 중 1.5초 멈추면 AI 교정 제안, Tab으로 적용)
- URL 라우팅 순서 수정 및 코드 정리
