# React + TypeScript + Vite 프론트엔드

이 프로젝트는 React와 TypeScript, Vite 기반의 프론트엔드 애플리케이션입니다.  
백엔드와는 FastAPI를 사용하며, `concurrently`로 프론트/백을 동시에 실행할 수 있습니다.

---

## 🔍 주요 기능

- 사용자가 검색하고 싶은 주제를 선택 후 메시지를 입력해 검색 요청하면, 앱이 주제(축제, 공연 등)를 인식하여 관련 정보를 검색합니다.
- 인식된 주제와 질의어를 바탕으로 FastAPI 백엔드에 GET 요청을 보내 결과를 표시합니다.
- 예: "서울 장미 축제 알려줘" → `category=축제`, `query=서울 장미`
   결과로는 축제명, 장소, 기간, 거리 정보가 표시됩니다.

---

## 프로젝트 구조

```
frontend/
├── public/             
│     └── logo,fruit.png...    	    # 로고와 아이콘
│
├── src/
│    ├── assets/                	# 이미지, 정적 파일
│    ├── pages/                 	# 라우팅되는 주요 페이지
│    │    ├─ WelcomePage.tsx    	# 메인(주제선택) 페이지
│    │    ├─ WelcomePage.css    	# WelcomePage 전용 스타일
│    │    ├─ ChatBotPage.tsx    	# 챗봇 메인 페이지
│    │    ├─ ChatBotPage.css   	    # ChatBotPage 전용 스타일
│    │    ├─ TopicSelectPage.tsx    # 보조(주제선택) 페이지
│    │    ├─ TopicSelectPage.css    # TopicSelectPage 전용 스타일
│    │    └─ Common.css        	    # 공통 스타일
│    │
│    ├── App.tsx                 	# 라우터 설정 포함
│    └── main.tsx                	# React 진입점
│
├── index.html			            # 웹페이지 뼈대
├── package.json		    	    # Node 기반 환경 설정 파일
├── tsconfig.json		    	    # TypeScript 컴파일 옵션을 정의한 설정 파일
└── vite.config.ts			        # 타입 환경파일

```

---

## 사용 기술 스택

- **React 19**
- **TypeScript**
- **Vite**
- **Axios** (API 통신)
- **ESLint + Typescript-ESLint**
- **Concurrently** (프론트+백 서버 동시 실행)

---

## 설치 및 실행 방법

### 1. 의존성 설치

```bash
npm install
```
### 2. 개발 서버 실행

```bash
npm run dev
```
### 3. 프론트 + 백엔드 동시에 실행

```bash
npm run dev:all
```
---

## 프로젝트 구조 요약
- `index.html`: 웹페이지 뼈대
- `main.tsx`: React 진입점
- `App.tsx`: 전체 컴포넌트 트리 루트
- `pages/WelcomePage.tsx `: 주제선택 페이지
- `pages/ChatBotPage.tsx `: 챗봇 메인 페이지
- `public/`: 이미지, 정적 파일 저장. 직접 URL로 접근 가능.

