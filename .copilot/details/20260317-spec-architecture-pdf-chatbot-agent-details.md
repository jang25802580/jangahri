<!-- markdownlint-disable-file -->

# Task Details: PDF Knowledge Base Chatbot Agent Spec Review

## Research Reference

**Source Research**: .copilot/research/20260317-spec-architecture-pdf-chatbot-agent-research.md

## Phase 1: 인증·데이터 보존

### Task 1.1: 인증·권한 세부화

- 상세 요구:
  - 인증 프로토콜: Azure AD (OIDC/OAuth2) 기본 채택
  - 역할: `uploader`, `reader`, `admin` 정의 및 각 엔드포인트 매핑
  - 토큰: 만료·갱신 정책(예: access token 1h, refresh token 30d) 및 검증 흐름
- Files:
  - docs/spec/spec-architecture-pdf-chatbot-agent.md - 기존 명세
  - .copilot/research/20260317-spec-architecture-pdf-chatbot-agent-research.md - 근거
- Success:
  - 엔드포인트별 권한표가 추가됨

### Task 1.2: 데이터 보존·삭제 API

- 상세 요구:
  - `DELETE /api/document/{id}` 스펙 추가
  - 보존정책 자동화: Timer-triggered Azure Function으로 만료 문서 정리
  - 감사 로그: 삭제 요청·완료 기록 보관
- Files:
  - docs/spec/spec-architecture-pdf-chatbot-agent.md
- Success:
  - 삭제 API와 자동 정리 프로세스 명세 포함

## Phase 2: 신뢰성·운영

### Task 2.1: 맬웨어 검사·업로드 재개

- 상세 요구:
  - 맬웨어 검사 옵션: (A) 클라우드 AV 연동, (B) 스테이징 샌드박스 검사
  - 처리 모델: 업로드 → 임시 저장 → 검사 통과 시 정식 저장·처리
  - 업로드 재개: 범용 청크 업로드(예: 5MB 청크) 지원
- Success:
  - 검사 실패 및 재시도 정책 추가

### Task 2.2: 오류 코드 및 재처리

- 상세 요구:
  - 공통 에러 포맷(JSON) 정의
  - 재시도 정책, idempotency 키 정의
  - 실패시 재처리 큐(예: Azure Queue Storage/Durable Functions)
- Success:
  - 에러 표준과 재처리 흐름이 명세에 포함됨

## Phase 3: 성능·모니터링

### Task 3.1: RU 소비·모니터링

- 상세 요구:
  - RU 소비 추정 가이드(예: 평균 embedding 질의당 RU, batch 크기별 소비)
  - Application Insights에 수집할 주요 메트릭 정의
  - 경보 임계값(예: 95th latency > 5s, error rate > 1%)
- Success:
  - 모니터링·경보 문구가 명세에 포함됨

## Dependencies

- Azure AD 문서, Cosmos DB 벡터 검색 문서, Azure Functions(Timer/Durable)

## Success Criteria

- 각 Phase별 Success 항목이 명세에 반영되어 구현팀에 전달 가능
