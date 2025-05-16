# React + TypeScript + Vite 프론트엔드

이 프로젝트는 React와 TypeScript, Vite 기반의 프론트엔드 애플리케이션입니다.  
백엔드와는 FastAPI를 사용하며, `concurrently`로 프론트/백을 동시에 실행할 수 있습니다.

---

## 🔍 주요 기능

- 사용자가 자연어로 검색 요청을 입력하면, 앱이 자동으로 주제(축제, 공연 등)를 인식하여 관련 정보를 검색합니다.
- 인식된 주제와 질의어를 바탕으로 FastAPI 백엔드에 GET 요청을 보내 결과를 표시합니다.
- 예: "서울 장미 축제 알려줘" → `category=축제`, `query=서울 장미`
- 결과로는 축제명, 장소, 기간, 거리 정보가 표시됩니다.

---

## 프로젝트 구조

```
frontend/
├── public/             
│
├── src/
│    ├── assets/               # 이미지, 정적 파일
│    ├── pages/                # 라우팅되는 주요 페이지
│    │     ├── ChatBotPage.tsx
│    │     └── QuotePage.tsx
│    │
│    ├── App.tsx               # 라우터 설정 포함
│    └── main.tsx              # 앱 진입점
│
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
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
- `main.tsx`: 앱 진입점
- `App.tsx`: 전체 컴포넌트 트리 루트
- `pages/SearchApp.tsx`: 현재 메인 화면
- `assets/`: 이미지 등 정적 파일 저장

