---
goal: Implement React + Vite + TypeScript + Tailwind CSS Web App Skeleton for PDF Chatbot Agent
version: 1.0
date_created: 2026-04-07
last_updated: 2026-04-07
owner: KAIST Big Data Analysis Team
status: 'Planned'
tags: [feature, react, vite, typescript, tailwindcss, frontend, spa, rag, chatbot]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

이 계획서는 `kaist-ai-webapp/` 경로에 React + Vite + TypeScript + Tailwind CSS 기반 프론트엔드 웹 애플리케이션 뼈대를 구성하는 구현 단계를 정의합니다.
사용자가 PDF 문서를 업로드하고, AI Agent(RAG 파이프라인)와 대화하며 채팅 이력을 확인할 수 있는 세련된 현대적 UI를 제공합니다.
API 서버는 `kaist-ai-functions/` 백엔드(Azure Functions)이며, 로컬 개발 시 `http://localhost:7071`, 프로덕션 시 Azure Functions 배포 URL을 사용합니다.

구성 대상:

- **Vite (latest stable)** — TypeScript SPA 빌드 도구 (Vite 8 베타 제외, `vite@latest` stable 버전 사용)
- **React 19** — UI 컴포넌트 라이브러리
- **TypeScript** — 정적 타입 언어
- **Tailwind CSS v3** — 유틸리티 기반 CSS 프레임워크
- **React Router v7** — SPA 경로 관리
- **TanStack Query (React Query) v5** — 서버 상태 관리 및 API 캐싱
- **PDF 관리 페이지** — 업로드, 목록 조회, 처리 상태 확인, 삭제
- **Chat 페이지** — AI Agent와의 대화, 소스 레퍼런스 표시, 과거 채팅 이력
- **Responsive Layout** — 모바일 & 데스크탑 모두 지원

## 1. Requirements & Constraints

- **REQ-001**: 웹 앱은 React + Vite 기반 TypeScript SPA로 구성해야 한다
- **REQ-002**: 빌드 도구는 `vite@latest` stable 버전을 사용해야 한다 (Vite 8 베타 제외)
- **REQ-003**: 스타일링은 Tailwind CSS v3를 사용해야 한다
- **REQ-004**: 언어는 TypeScript를 사용해야 하며, `strict` 모드를 활성화해야 한다
- **REQ-005**: 로컬 개발 API URL은 `http://localhost:7071`, 프로덕션 API URL은 `VITE_API_BASE_URL` 환경변수를 통해 주입해야 한다
- **REQ-006**: PDF 관리 기능: 파일 업로드(드래그 앤 드롭 + 파일 선택), 업로드된 PDF 목록 조회, 처리 상태 확인, PDF 삭제
- **REQ-007**: Chat 기능: AI Agent와의 대화, 소스 문서 레퍼런스 표시, 채팅 세션 이력 조회 및 표시
- **REQ-008**: 레이아웃은 모바일(320px 이상)과 데스크탑(1024px 이상) 모두를 지원하는 Responsive Layout이어야 한다
- **REQ-009**: API 연동 경로: `POST /api/pdf/upload`, `GET /api/pdf/status/{documentId}`, `POST /api/chat/query`, `GET /api/chat/history`, `GET /api/health`
- **REQ-010**: 프로덕션 배포 대상은 Azure Static Web Apps이며, `kaist-ai-infra/infra/modules/staticwebapp.bicep`에 이미 프로비저닝되어 있다
- **REQ-011**: Azure Static Web Apps 배포를 위해 `staticwebapp.config.json`에 SPA fallback 라우팅(`"navigationFallback": {"rewrite": "/index.html"}`)을 설정해야 한다

- **SEC-001**: API 응답의 에러 메시지가 브라우저 콘솔에 그대로 노출되지 않도록 사용자 친화적 메시지로 변환해야 한다
- **SEC-002**: 파일 업로드 시 클라이언트에서도 MIME 타입(`application/pdf`) 및 파일 크기(50MB 이하)를 사전 검증해야 한다
- **SEC-003**: API 기본 키(Function Key)는 `VITE_API_KEY` 환경변수를 통해 주입하며, `.env.local`은 `.gitignore`에 포함해야 한다
- **SEC-004**: XSS 방지를 위해 서버 응답의 텍스트를 React JSX에서 직접 렌더링하고, `dangerouslySetInnerHTML` 사용을 금지해야 한다

- **CON-001**: Azure Functions HTTP 트리거는 기본 `authLevel: function`이므로, API 요청 헤더에 `x-functions-key` 또는 쿼리스트링 `code=` 방식으로 Function Key를 전달해야 한다
- **CON-002**: Azure Static Web Apps 무료 플랜은 커스텀 백엔드 통합(Functions 링크)을 지원하지 않으므로, CORS는 Azure Functions에서 직접 구성해야 한다
- **CON-003**: `kaist-ai-functions`의 chat history API(`GET /api/chat/history`)는 `sessionId` 쿼리 파라미터로 세션을 식별하므로, 프론트엔드에서 세션 ID를 localStorage에 관리해야 한다
- **CON-004**: 이번 계획서의 범위는 뼈대(skeleton) 구현이며, 사용자 인증(로그인/회원가입) 및 멀티테넌트 분리는 후속 계획서에서 다룬다
- **CON-005**: `chat/query` API는 스트리밍 응답을 제공하지 않으므로(현재 백엔드 구현 기준), 전체 응답을 받은 후 렌더링하는 방식을 사용한다

- **GUD-001**: 컴포넌트는 기능 단위로 `src/features/` 하위에 배置하고, 재사용 가능한 공통 컴포넌트는 `src/components/ui/`에 배치한다
- **GUD-002**: API 호출 로직은 `src/api/` 레이어로 분리하고, TanStack Query의 커스텀 훅으로 래핑한다
- **GUD-003**: 전역 상태는 최소화하고, 서버 상태는 TanStack Query, 클라이언트 UI 상태는 컴포넌트 로컬 state로 관리한다
- **GUD-004**: 환경별 설정 값은 `src/config/env.ts`의 단일 모듈을 통해서만 참조한다
- **GUD-005**: 로딩·에러·빈 상태(Empty State)를 모든 비동기 UI에 명시적으로 처리한다
- **GUD-006**: 세련된 현대적 디자인을 위해 Tailwind CSS의 다크 톤 계열 팔레트(`slate`, `zinc`, `neutral`)를 기반으로 하고, 포인트 컬러는 `indigo` 또는 `violet`을 사용한다

- **PAT-001**: 파일 컨벤션 — React 컴포넌트 파일은 PascalCase(`ChatPage.tsx`), 유틸리티/훅은 camelCase(`useDocuments.ts`)
- **PAT-002**: API 클라이언트는 `fetch` 기반 래퍼 함수로 구현하며, 모든 요청에 `x-functions-key` 헤더를 자동 추가한다
- **PAT-003**: 타입 정의는 `src/types/` 하위에 backend `shared/models.py`의 Pydantic 모델과 1:1로 대응하는 TypeScript interface로 관리한다

## 2. Implementation Steps

### Implementation Phase 1 — 프로젝트 초기화 및 환경 구성

- GOAL-001: Vite + React + TypeScript 프로젝트를 생성하고 Tailwind CSS, 라우팅, 서버 상태 관리 라이브러리를 설치 및 설정한다

| Task     | Description                                                                                                                                                                                                               | Completed | Date |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-001 | `kaist-ai-webapp/` 디렉토리에서 `npm create vite@latest . -- --template react-ts` 명령으로 Vite + React + TypeScript 프로젝트를 초기화한다                                                                              |           |      |
| TASK-002 | `npm install tailwindcss @tailwindcss/forms postcss autoprefixer` 후 `npx tailwindcss init -p` 로 `tailwind.config.js` 및 `postcss.config.js` 생성. `tailwind.config.js` content에 `./src/**/*.{ts,tsx}` 경로를 추가한다 |           |      |
| TASK-003 | `src/index.css`에 Tailwind 지시어(`@tailwind base; @tailwind components; @tailwind utilities;`)를 추가하고, 기존 Vite boilerplate CSS를 제거한다                                                                          |           |      |
| TASK-004 | `npm install react-router-dom@latest @tanstack/react-query@latest` 를 설치한다                                                                                                                                            |           |      |
| TASK-005 | `.env.development` 파일에 `VITE_API_BASE_URL=http://localhost:7071` 및 `VITE_API_KEY=` (빈값) 을 설정하고, `.env.production` 파일에 `VITE_API_BASE_URL=` (프로덕션 URL 플레이스홀더) 를 생성한다                        |           |      |
| TASK-006 | `.gitignore`에 `.env.local`, `.env.*.local` 항목이 포함되어 있는지 확인하고 없으면 추가한다                                                                                                                               |           |      |
| TASK-007 | `src/config/env.ts`를 생성하고 `VITE_API_BASE_URL`, `VITE_API_KEY` 환경변수를 읽어 export하는 `apiBaseUrl`과 `apiKey` 상수를 정의한다                                                                                    |           |      |
| TASK-008 | `public/staticwebapp.config.json`을 생성하고 `"navigationFallback": {"rewrite": "/index.html", "exclude": ["/api/*"]}` SPA 라우팅 fallback 설정을 추가한다                                                              |           |      |

### Implementation Phase 2 — 타입 정의 및 API 클라이언트 계층

- GOAL-002: backend `shared/models.py`의 Pydantic 모델과 1:1 대응하는 TypeScript 타입을 정의하고, Azure Functions API를 호출하는 클라이언트 모듈을 구현한다

| Task     | Description                                                                                                                                                                                                                                                                   | Completed | Date |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-009 | `src/types/document.ts`를 생성하고 `DocumentRecord`, `UploadResponse`, `StatusResponse` interface를 정의한다 (`status: 'pending' \| 'processing' \| 'completed' \| 'failed'` 유니온 타입 포함)                                                                               |           |      |
| TASK-010 | `src/types/chat.ts`를 생성하고 `ChatMessage`, `ChatQueryRequest`, `ChatQueryResponse`, `SourceReference`, `ChatHistoryResponse` interface를 정의한다                                                                                                                          |           |      |
| TASK-011 | `src/types/health.ts`를 생성하고 `HealthResponse` interface를 정의한다 (`status: 'healthy' \| 'degraded'`, `checks: { storage: string; cosmos: string; gemini: string }`)                                                                                                    |           |      |
| TASK-012 | `src/api/client.ts`를 생성하고, `apiBaseUrl`과 `apiKey`를 사용해 모든 요청에 `x-functions-key` 헤더를 자동 주입하는 `apiFetch<T>` 제네릭 함수를 구현한다. 4xx/5xx 응답 시 에러 객체를 throw한다                                                                             |           |      |
| TASK-013 | `src/api/documents.ts`를 생성하고 다음 함수를 구현한다: `uploadDocument(file: File): Promise<UploadResponse>` (FormData + POST), `getDocumentStatus(documentId: string): Promise<StatusResponse>` (GET), `processDocument(documentId: string): Promise<void>` (POST)        |           |      |
| TASK-014 | `src/api/chat.ts`를 생성하고 다음 함수를 구현한다: `sendQuery(request: ChatQueryRequest): Promise<ChatQueryResponse>` (POST), `getChatHistory(sessionId: string): Promise<ChatHistoryResponse>` (GET)                                                                        |           |      |
| TASK-015 | `src/hooks/useDocuments.ts`를 생성하고 TanStack Query를 사용하는 커스텀 훅을 구현한다: `useDocumentStatus(documentId)` (폴링 포함, 상태가 `completed` 또는 `failed`가 될 때까지 5초 간격 refetch), `useUploadDocument()` (mutation 훅)                                       |           |      |
| TASK-016 | `src/hooks/useChat.ts`를 생성하고 TanStack Query를 사용하는 커스텀 훅을 구현한다: `useChatHistory(sessionId)`, `useSendQuery()` (mutation 훅). `sessionId`는 `src/hooks/useSession.ts`에서 `localStorage`로 관리한다 (`chatSessionId` 키, 없으면 `crypto.randomUUID()` 생성) |           |      |

### Implementation Phase 3 — 레이아웃 및 공통 UI 컴포넌트

- GOAL-003: 앱 전체 레이아웃 쉘과 재사용 가능한 공통 UI 컴포넌트를 구현한다. RAG & AI Agent에 집중할 수 있는 세련된 다크 톤 디자인을 적용한다

| Task     | Description                                                                                                                                                                                                                                                                                                      | Completed | Date |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-017 | `src/components/layout/AppLayout.tsx`를 생성한다. 좌측 사이드바(네비게이션 링크: PDF 관리, 채팅) + 우측 메인 콘텐츠 영역의 2단 레이아웃. 모바일에서는 사이드바가 하단 탭 바로 전환되는 반응형 구조. 배경색 `bg-zinc-950`, 사이드바 `bg-zinc-900`, 메인 `bg-zinc-900`                                           |           |      |
| TASK-018 | `src/components/layout/Sidebar.tsx`를 생성한다. 앱 로고/이름(`KAIST AI Agent`), PDF 관리 및 채팅 네비게이션 링크, 활성 상태 하이라이트(`bg-indigo-600`). `react-router-dom`의 `NavLink` 사용                                                                                                                    |           |      |
| TASK-019 | `src/components/layout/MobileTabBar.tsx`를 생성한다. 모바일 하단 고정 탭 바. PDF 아이콘과 Chat 아이콘. `md:hidden` Tailwind 클래스로 데스크탑에서는 숨김                                                                                                                                                         |           |      |
| TASK-020 | `src/components/ui/Button.tsx`를 생성한다. `variant: 'primary' \| 'secondary' \| 'ghost' \| 'danger'`, `size: 'sm' \| 'md' \| 'lg'`, `isLoading: boolean` props를 갖는 버튼 컴포넌트. 로딩 시 스피너 아이콘 표시                                                                                               |           |      |
| TASK-021 | `src/components/ui/Badge.tsx`를 생성한다. 문서 처리 상태(`pending` → yellow, `processing` → blue, `completed` → green, `failed` → red)를 시각적으로 표현하는 상태 배지 컴포넌트                                                                                                                                 |           |      |
| TASK-022 | `src/components/ui/Spinner.tsx`와 `src/components/ui/EmptyState.tsx`를 생성한다. Spinner는 SVG 애니메이션 로딩 인디케이터. EmptyState는 아이콘 + 제목 + 설명 텍스트를 갖는 빈 상태 레이아웃 컴포넌트                                                                                                           |           |      |
| TASK-023 | `src/components/ui/ErrorMessage.tsx`를 생성한다. 에러 메시지를 `bg-red-950 border border-red-800 text-red-300` 스타일로 표시하는 컴포넌트. `message: string` prop 수신                                                                                                                                          |           |      |
| TASK-024 | `src/components/ui/ProgressBar.tsx`를 생성한다. `progress: number` (0-100) prop을 받아 PDF 처리 진행률을 시각화하는 컴포넌트. Tailwind `bg-indigo-500` 포인트 컬러 사용                                                                                                                                         |           |      |

### Implementation Phase 4 — PDF 관리 페이지

- GOAL-004: PDF 파일 업로드, 목록 조회, 처리 상태 확인 기능을 갖춘 PDF 관리 페이지를 구현한다

| Task     | Description                                                                                                                                                                                                                                                                                | Completed | Date |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------- | ---- |
| TASK-025 | `src/features/pdf/PdfUploadZone.tsx`를 생성한다. 드래그 앤 드롭과 파일 선택 버튼을 모두 지원하는 파일 업로드 영역. 점선 테두리 + 아이콘 + 안내 문구 디자인. 드래그 오버 시 `border-indigo-400 bg-indigo-950/30` 하이라이트 처리. 파일 선택 시 `application/pdf`와 50MB 제한을 사전 검증한다 |           |      |
| TASK-026 | `src/features/pdf/PdfUploadProgress.tsx`를 생성한다. 업로드 중인 파일명, 업로드 완료 후 처리 상태 및 진행률을 표시. `useDocumentStatus` 훅의 폴링을 사용해 처리 상태를 실시간으로 갱신한다                                                                                                |           |      |
| TASK-027 | `src/features/pdf/PdfListItem.tsx`를 생성한다. 문서 이름, 파일 크기, 업로드 시각, 처리 상태 배지(`Badge` 컴포넌트 활용), 처리 진행률(`ProgressBar` 컴포넌트 활용)을 표시하는 목록 행 컴포넌트. "처리 시작" 버튼(상태가 `pending`일 때만 활성)을 포함한다                                  |           |      |
| TASK-028 | `src/features/pdf/PdfPage.tsx`를 생성한다. `PdfUploadZone` + 업로드된 문서 목록을 조합하는 페이지 컴포넌트. 문서 목록은 Cosmos DB에서 직접 조회하는 대신, 업로드 후 React state로 관리하여 로컬 목록 표시. 빈 상태일 때 `EmptyState` 컴포넌트 표시                                        |           |      |
| TASK-029 | `src/features/pdf/PdfPage.tsx`에서 업로드 처리 플로우를 구현한다: (1) `useUploadDocument` 뮤테이션으로 파일 업로드 → (2) 반환된 `documentId`로 자동 처리 시작(`POST /api/pdf/process`) → (3) `useDocumentStatus` 폴링으로 상태 표시                                                        |           |      |

### Implementation Phase 5 — 채팅 페이지

- GOAL-005: AI Agent와 대화하고, 응답 소스 문서를 확인하고, 과거 채팅 이력을 조회할 수 있는 채팅 페이지를 구현한다

| Task     | Description                                                                                                                                                                                                                                                                              | Completed | Date |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-030 | `src/features/chat/ChatMessage.tsx`를 생성한다. `role: 'user' \| 'assistant'` prop에 따라 좌/우 정렬. 사용자 메시지: `bg-indigo-600` 말풍선, 우측 정렬. AI 응답: `bg-zinc-800` 말풍선, 좌측 정렬. 타임스탬프 표시                                                                       |           |      |
| TASK-031 | `src/features/chat/SourceReferences.tsx`를 생성한다. `ChatQueryResponse.sources` 배열을 받아 소스 문서 레퍼런스를 접이식(accordion) UI로 표시. 각 항목에 문서명, 관련도 점수, 발췌 텍스트를 표시한다                                                                                    |           |      |
| TASK-032 | `src/features/chat/ChatInput.tsx`를 생성한다. 멀티라인 `textarea`(Enter로 전송, Shift+Enter로 개행), 전송 버튼, 로딩 시 비활성 처리를 갖는 채팅 입력 컴포넌트. `onSend(message: string) => void` 콜백 prop 수신                                                                          |           |      |
| TASK-033 | `src/features/chat/ChatHistorySidebar.tsx`를 생성한다. 과거 채팅 메시지 이력을 시간 순으로 표시하는 사이드 패널. `useChatHistory` 훅으로 데이터 로드. 모바일에서는 기본 숨김(`hidden`), 버튼 클릭 시 슬라이드 오버레이로 표시                                                           |           |      |
| TASK-034 | `src/features/chat/ChatPage.tsx`를 생성한다. 메시지 목록 스크롤 영역 + 하단 고정 입력창의 채팅 레이아웃. `useSendQuery` mutation으로 쿼리 전송. 응답 수신 후 `ChatMessage` 및 `SourceReferences` 컴포넌트로 렌더링. 메시지 전송 후 스크롤 최하단 자동 이동(`useEffect` + `scrollIntoView`) |           |      |
| TASK-035 | `src/features/chat/ChatPage.tsx`에 문서 선택 패널을 추가한다. 현재 세션에서 RAG 검색 대상 문서를 선택하는 체크박스 목록. 선택된 `documentIds` 배열을 `ChatQueryRequest.document_ids`에 포함하여 전송한다                                                                                 |           |      |

### Implementation Phase 6 — 라우팅 및 앱 진입점 통합

- GOAL-006: React Router 라우팅, TanStack Query Provider, 환경 설정을 통합하여 완성된 앱 진입점을 구성한다

| Task     | Description                                                                                                                                                                                                          | Completed | Date |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-036 | `src/main.tsx`에 `QueryClientProvider`(TanStack Query)와 `BrowserRouter`(React Router)를 래핑하여 앱 전체에 적용한다                                                                                                 |           |      |
| TASK-037 | `src/App.tsx`에 React Router Routes를 구성한다: `/` → `/pdf`로 리다이렉트, `/pdf` → `PdfPage`, `/chat` → `ChatPage`. `AppLayout`으로 모든 페이지를 래핑한다                                                         |           |      |
| TASK-038 | `vite.config.ts`에 개발 서버 프록시를 설정한다: `/api` 경로를 `http://localhost:7071`로 프록시하여 로컬 CORS 이슈 없이 백엔드를 호출할 수 있도록 한다                                                              |           |      |
| TASK-039 | `src/features/common/HealthIndicator.tsx`를 생성한다. `GET /api/health` API를 30초 주기로 호출하여, 사이드바 하단에 서비스의 전체 상태(`healthy` / `degraded`)를 점등 인디케이터로 표시하는 컴포넌트               |           |      |
| TASK-040 | `package.json`의 `scripts`에 `"dev": "vite"`, `"build": "tsc -b && vite build"`, `"preview": "vite preview"` 명령이 올바르게 설정되어 있는지 확인하고, `README.md`에 로컬 실행 방법을 기술한다                     |           |      |

## 3. Alternatives

- **ALT-001**: **Next.js 대신 Vite + React SPA** — Next.js는 서버 사이드 렌더링(SSR) 기능을 제공하지만, 백엔드가 Azure Functions로 완전히 분리된 구조에서는 불필요한 복잡도를 추가한다. Azure Static Web Apps에 순수 SPA를 배포하는 구조가 더 단순하고 `azd` 파이프라인과 일치한다
- **ALT-002**: **Zustand/Jotai 전역 상태 관리 대신 TanStack Query** — 앱의 대부분의 상태가 서버 데이터(API 응답)이므로 전용 서버 상태 관리 라이브러리인 TanStack Query가 더 적합하다. 클라이언트 UI 상태는 컴포넌트 로컬 state로 충분하다
- **ALT-003**: **Material UI / Chakra UI 대신 Tailwind CSS** — 컴포넌트 라이브러리는 번들 크기를 증가시키고 커스터마이징에 제약이 있다. Tailwind CSS는 필요한 스타일만 빌드에 포함되며 디자인 자유도가 높다
- **ALT-004**: **WebSocket 스트리밍 대신 단순 HTTP POST** — 현재 `chat/query` 백엔드 구현이 스트리밍을 지원하지 않으므로, 복잡도를 낮추기 위해 단순 HTTP POST 방식을 사용한다. 향후 백엔드가 Server-Sent Events를 지원하면 프론트엔드도 업그레이드한다
- **ALT-005**: **Vite 8 베타 제외** — Vite 8은 베타 버전으로 안정성이 검증되지 않았으므로 `vite@latest` stable 채널을 사용한다

## 4. Dependencies

- **DEP-001**: `vite@latest` — 빌드 도구 (stable 버전)
- **DEP-002**: `react@^19.0.0`, `react-dom@^19.0.0` — UI 라이브러리
- **DEP-003**: `typescript@^5.x` — 타입스크립트 컴파일러
- **DEP-004**: `tailwindcss@^3.x`, `@tailwindcss/forms`, `postcss`, `autoprefixer` — CSS 유틸리티 프레임워크
- **DEP-005**: `react-router-dom@latest` — SPA 클라이언트 라우팅
- **DEP-006**: `@tanstack/react-query@^5.x` — 서버 상태 관리 및 API 캐싱/폴링
- **DEP-007**: `@vitejs/plugin-react` (devDependency) — Vite React 플러그인 (HMR 지원)
- **DEP-008**: Azure Functions 백엔드 (`kaist-ai-functions/`): `GET /api/health`, `POST /api/pdf/upload`, `GET /api/pdf/status/{documentId}`, `POST /api/pdf/process`, `POST /api/chat/query`, `GET /api/chat/history` 엔드포인트가 정상 동작해야 한다
- **DEP-009**: Azure Static Web App (`swa-kaist-ai-agent-dev-krc`) — Bicep으로 프로비저닝된 상태. `kaist-ai-infra/infra/modules/staticwebapp.bicep` 정의에 따라 배포 대상이 정해져 있다

## 5. Files

- **FILE-001**: `kaist-ai-webapp/package.json` — 프로젝트 메타데이터 및 dependencies/scripts 정의
- **FILE-002**: `kaist-ai-webapp/vite.config.ts` — Vite 설정, dev 프록시(`/api` → `http://localhost:7071`), build 출력 경로
- **FILE-003**: `kaist-ai-webapp/tsconfig.json`, `tsconfig.app.json` — TypeScript strict 모드 설정
- **FILE-004**: `kaist-ai-webapp/tailwind.config.js`, `kaist-ai-webapp/postcss.config.js` — Tailwind CSS 설정
- **FILE-005**: `kaist-ai-webapp/.env.development` — 로컬 개발 환경변수 (`VITE_API_BASE_URL=http://localhost:7071`)
- **FILE-006**: `kaist-ai-webapp/.env.production` — 프로덕션 환경변수 (빌드 시 주입)
- **FILE-007**: `kaist-ai-webapp/public/staticwebapp.config.json` — Azure Static Web Apps SPA 라우팅 fallback 설정
- **FILE-008**: `kaist-ai-webapp/src/main.tsx` — 앱 진입점, QueryClientProvider + BrowserRouter 래핑
- **FILE-009**: `kaist-ai-webapp/src/App.tsx` — React Router Routes 정의
- **FILE-010**: `kaist-ai-webapp/src/config/env.ts` — 환경변수 중앙화 모듈
- **FILE-011**: `kaist-ai-webapp/src/types/document.ts`, `src/types/chat.ts`, `src/types/health.ts` — TypeScript 타입 정의
- **FILE-012**: `kaist-ai-webapp/src/api/client.ts`, `src/api/documents.ts`, `src/api/chat.ts` — API 클라이언트 레이어
- **FILE-013**: `kaist-ai-webapp/src/hooks/useDocuments.ts`, `src/hooks/useChat.ts`, `src/hooks/useSession.ts` — TanStack Query 커스텀 훅
- **FILE-014**: `kaist-ai-webapp/src/components/layout/AppLayout.tsx`, `Sidebar.tsx`, `MobileTabBar.tsx` — 레이아웃 컴포넌트
- **FILE-015**: `kaist-ai-webapp/src/components/ui/Button.tsx`, `Badge.tsx`, `Spinner.tsx`, `EmptyState.tsx`, `ErrorMessage.tsx`, `ProgressBar.tsx` — 공통 UI 컴포넌트
- **FILE-016**: `kaist-ai-webapp/src/features/pdf/PdfPage.tsx`, `PdfUploadZone.tsx`, `PdfUploadProgress.tsx`, `PdfListItem.tsx` — PDF 관리 기능
- **FILE-017**: `kaist-ai-webapp/src/features/chat/ChatPage.tsx`, `ChatMessage.tsx`, `ChatInput.tsx`, `SourceReferences.tsx`, `ChatHistorySidebar.tsx` — 채팅 기능
- **FILE-018**: `kaist-ai-webapp/src/features/common/HealthIndicator.tsx` — 서비스 헬스 상태 인디케이터
- **FILE-019**: `kaist-ai-webapp/src/index.css` — Tailwind 지시어 및 전역 CSS

## 6. Testing

- **TEST-001**: `src/api/client.ts` — `apiFetch` 함수가 `x-functions-key` 헤더를 자동으로 추가하는지 확인. 4xx 응답 시 에러를 throw하는지 확인
- **TEST-002**: `src/api/documents.ts` — `uploadDocument` 함수가 FormData를 올바르게 구성하고 `POST /api/pdf/upload`를 호출하는지 확인 (mock fetch 사용)
- **TEST-003**: `src/api/chat.ts` — `sendQuery` 함수가 `POST /api/chat/query`를 올바른 body로 호출하는지 확인
- **TEST-004**: `PdfUploadZone` 컴포넌트 — PDF 외 파일 업로드 시 에러 메시지를 표시하는지 확인. 50MB 초과 파일 시 에러 메시지를 표시하는지 확인
- **TEST-005**: `useDocumentStatus` 훅 — 상태가 `completed` 또는 `failed`일 때 폴링이 중단되는지 확인 (`refetchInterval` 조건 검증)
- **TEST-006**: `useSession` 훅 — `localStorage`에 `chatSessionId`가 없을 때 `crypto.randomUUID()`로 세션 ID를 생성하고 저장하는지 확인
- **TEST-007**: E2E 로컬 통합 테스트 — `kaist-ai-functions`를 `func start` 로 로컬 실행 후, 웹앱 개발 서버와 연결하여 PDF 업로드 → 처리 → 채팅 쿼리 전체 플로우가 동작하는지 수동 확인
- **TEST-008**: Responsive 레이아웃 테스트 — Chrome DevTools 모바일 시뮬레이터(375px)에서 하단 탭 바가 표시되고, 사이드바가 숨겨지는지 확인. 데스크탑(1280px)에서 사이드바가 표시되는지 확인
- **TEST-009**: Azure Static Web Apps 배포 테스트 — `npm run build` 후 `dist/` 폴더의 `index.html`이 생성되고, `staticwebapp.config.json`이 `dist/` 또는 `public/`에 존재하는지 확인. 배포 후 직접 URL 접근 시 SPA 라우팅이 동작하는지 확인

## 7. Risks & Assumptions

- **RISK-001**: Azure Functions `authLevel: function`으로 설정된 API 일부는 Function Key 없이 호출 시 401을 반환한다. 로컬 개발 시 `local.settings.json`의 기본 key를 사용하거나 `authLevel: anonymous`로 임시 변경이 필요할 수 있다
- **RISK-002**: Azure Functions의 CORS 설정이 Static Web Apps 도메인을 허용하지 않으면 프로덕션에서 API 호출이 실패한다. `functions.bicep`에 CORS 허용 오리진이 설정되어 있는지 검증이 필요하다
- **RISK-003**: `chat/history` API는 현재 `sessionId` 쿼리 파라미터로 세션을 식별하며, 사용자 인증이 없으므로 다른 사용자의 세션 ID를 알면 이력을 조회할 수 있다. 이는 현재 skeleton 단계에서 허용된 제약이며 후속 인증 계획서에서 해결해야 한다
- **RISK-004**: Cosmos DB에 문서 목록 조회 API(`GET /api/pdf/documents`)가 현재 `kaist-ai-functions`에 구현되어 있지 않다. TASK-028에서 로컬 state로 관리하는 방식을 사용하나, 페이지 새로고침 시 목록이 초기화된다. 필요 시 백엔드 추가 구현이 required이다
- **RISK-005**: `vite@latest`의 빌드 동작이 Azure Static Web Apps의 빌드 파이프라인과 호환되지 않을 수 있다. 빌드 아티팩트 경로(`dist/`)와 `staticwebapp.config.json` 위치를 정확히 설정해야 한다
- **ASSUMPTION-001**: 백엔드 API(`/api/health`, `/api/pdf/upload`, `/api/pdf/status/{id}`, `/api/pdf/process`, `/api/chat/query`, `/api/chat/history`)가 모두 정상 동작하고 있음을 가정한다 (이전 계획서 `feature-api-backend-1.md` 구현 완료 전제)
- **ASSUMPTION-002**: Azure Static Web Apps에 배포 시 `swa-kaist-ai-agent-dev-krc` 리소스가 `kaist-ai-infra` Bicep으로 이미 프로비저닝되어 있음을 가정한다
- **ASSUMPTION-003**: 이번 skeleton 구현에서는 사용자 인증(로그인)이 없으므로, 모든 사용자가 동일한 PDF 목록과 채팅 기능을 공유한다

## 8. Related Specifications / Further Reading

- [spec-architecture-pdf-chatbot-agent.md](../spec/spec-architecture-pdf-chatbot-agent.md) — 전체 시스템 아키텍처 명세 (REQ-015~REQ-021 Client Application Requirements)
- [feature-api-backend-1.md](./feature-api-backend-1.md) — Azure Functions API 백엔드 구현 계획서 (이 계획서의 전제 조건)
- [infrastructure-azure-bicep-1.md](./infrastructure-azure-bicep-1.md) — Azure 인프라 Bicep 구성 계획서 (Static Web Apps 프로비저닝 정의 포함)
- [Vite 공식 문서](https://vitejs.dev/guide/) — Vite 빌드 도구 가이드
- [TanStack Query v5 문서](https://tanstack.com/query/latest/docs/framework/react/overview) — 서버 상태 관리
- [Azure Static Web Apps 배포 가이드](https://learn.microsoft.com/azure/static-web-apps/deploy-react) — React SPA 배포 방법
- [Azure Static Web Apps 라우팅 구성](https://learn.microsoft.com/azure/static-web-apps/configuration) — `staticwebapp.config.json` 설정 레퍼런스
