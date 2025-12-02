# 🛍️ 오e마켓 : flask_project2025

> **Flask 기반의 학생 중고 거래 플랫폼 프로젝트** > 사용자 간의 신뢰할 수 있는 물품 거래와 리뷰 시스템을 제공합니다.

<br>

## 📋 프로젝트 소개
이 프로젝트는 **오픈소스 소프트웨어 실습** 수업의 일환으로 개발된 웹 애플리케이션입니다. 
사용자는 상품을 등록하고, 검색하며, 관심 있는 상품에 '좋아요'를 누를 수 있습니다. 거래 후기 시스템을 통해 판매자의 매너 온도를 확인할 수 있는 기능을 중점적으로 구현했습니다.

### 주요 기능
- 사용자 인증: 회원가입, 로그인/로그아웃, 비밀번호 암호화
- 상품 거래: 상품 등록(이미지 업로드), 카테고리별 검색, 상세 조회
- 관심 상품: 좋아요 기능 및 마이페이지 관리
- 리뷰 시스템: 거래 후기 작성 및 판매자 매너 온도(평점) 평가

<br>

## 🛠️ 기술 스택 (Tech Stack)
- **Framework:** Python Flask
- **Frontend:** HTML5, CSS3, JavaScript
- **Database:** Firebase

<br>

## 📂 디렉토리 구조 (Project Structure)
기능별 모듈화(Blueprint)와 정적 파일의 효율적인 관리를 위해 아래와 같은 구조로 설계되었습니다.

```text
FLASK_PROJECT2025/
├── 📂 routes/               # 기능별 라우팅 (Backend Logic)
│   ├── auth_route.py       # 로그인, 회원가입, 인증 관리
│   ├── item_route.py       # 상품 등록, 조회, 검색, 좋아요 기능
│   ├── review_route.py     # 리뷰 작성 및 조회 기능
│   └── user_route.py       # 마이페이지, 사용자 프로필 관리, 좋아요 기능
│
├── 📂 static/               # 정적 파일 (Frontend Assets)
│   ├── 📂 assets/           # 사이트 구성 요소 (Design Assets)
│   │   ├── 📂 css/          # 스타일시트 (기능별 CSS 분리)
│   │   ├── 📂 fonts/        # 폰트 파일
│   │   └── 📂 svg/          # 벡터 아이콘
│   ├── 📂 js/               # 클라이언트 스크립트
│   └── 📂 images/           # 사용자 업로드 이미지 (User Data)
│
├── 📂 templates/            # HTML 템플릿 (View)
│   ├── index.html          # 메인 페이지
│   └── ...                 # 기능별 HTML 페이지
│
├── app.py                  # 애플리케이션 실행 진입점 (Entry Point)
├── database.py             # 데이터베이스 핸들링 모듈
└── requirements.txt        # 의존성 패키지 목록
```

<br>

## 🏗️ 아키텍처 및 협업 전략 (Architecture & Collaboration)
본 프로젝트는 팀원 간의 **협업 효율성(Collaboration Efficiency)**을 극대화하기 위해 **Flask Blueprint**를 사용하여 모듈화된 아키텍처를 채택했습니다.

* **기능별 모듈 분리:** `auth`, `item`, `review` 등으로 라우트 파일을 분리하여, 팀원들이 각 기능 개발 시 코드 충돌(Merge Conflict)을 최소화했습니다.
* **리소스 관리 최적화:** `static` 폴더 내에서 시스템 에셋(`assets`)과 사용자 업로드 데이터(`images`)를 물리적으로 분리하여 유지보수성을 높였습니다.
