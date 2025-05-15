ap/src/backend/requirements.txt -- Python 백엔드용 의존성파일
ap/src/frontend/package.json -- React 프론트엔드용

---

각 설치방법

백엔드
cd src/backend
pip install -r requirements.txt

프론트엔드
cd src/frontend
npm install

---

react 설치
npm create vite@latest . -- --template react-ts
npm install

frontend실행
ap\src\frontend>npm run dev
npm run dev --- Vite로 만들었을경우
npm start --- CRA로 만든경우

backend실행
ap\src\backend>uvicorn main:app --reload --port 8000
http://localhost:8000/docs

FrontEnd 구조
src/
├── assets/ # CSS, 이미지 등 정적 파일
│ ├── App.css
├── App.tsx # 루트 컴포넌트 (SearchApp을 여기에 연결)
├── main.tsx # React 앱 진입점
├── index.css # 글로벌 스타일
├── index.html # HTML 템플릿
├── vite.config.ts # Vite 설정
├── tsconfig.json # TypeScript 설정
├── package.json # 프로젝트 설정 및 의존성
├── .gitignore # Git 제외 항목

---

## 브라우저 동작 구조

React (http://localhost:5173)
↓ axios GET
FastAPI (http://localhost:8000)
↓ mock_engine.py → 결과 응답
React 결과 렌더링

---

## 최종 실행법 (현재 ap/ 디렉토리 기준)

터미널1
conda activate "NAME"
cd src/backend
uvicorn main:app --reload --port 8000

터미널2
conda activate "NAME"
cd src/frontend
npm run dev

---

## 동시에 실행

conda activate "NAME"
cd src/frontend
npm run dev:all

---

## 전체 구조

src/
├── backend/
│ ├── main.py # FastAPI 엔트리포인트
│ ├── engine.py # 실제 검색/추천 엔진 (mock 대체)
│ ├── mock_engine.py # 테스트용 데이터 유지
│ ├── data/
│ │ ├── festivals.json # 원본 또는 정제된 API 데이터
│ │ ├── performances.json
│ ├── database/
│ │ ├── models.py # SQLAlchemy 테이블 정의
│ │ ├── crud.py # 삽입/조회 함수
│ │ ├── db.py # DB 연결 관리
│ ├── nlp/
│ │ ├── parser.py # 문장 → intent + entity 추출
│ │ ├── matcher.py # entity 기반 DB 조회 알고리즘
│ ├── utils/
│ │ ├── fetch_api.py # 공공 데이터 API 수집 모듈
│ │ ├── preprocess.py # 전처리 로직
│ └── .env # 환경변수 저장 (로컬에만 존재)
