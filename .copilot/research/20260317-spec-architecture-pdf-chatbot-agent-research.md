<!-- markdownlint-disable-file -->

# Task Research Notes: PDF Knowledge Base Chatbot Agent Spec Review

## Research Executed

### File Analysis

- docs/spec/spec-architecture-pdf-chatbot-agent.md
  - 전체 아키텍처·요구사항·인터페이스·예제·테스트 전략이 상세히 기술되어 있음. 인프라(Bicep), API 계약, 데이터 스키마, 보안 요구사항 등이 포함됨.

### Code Search Results

- 검색 대상: `Cosmos DB vector search`, `Azure Functions Python 3.11`, `Azure Static Web Apps Vite Tailwind`
  - 일치 항목: 명세에서 참조한 Microsoft 문서들이 설계 근거로 적절함.

### External Research

- #fetch:https://learn.microsoft.com/azure/cosmos-db/nosql/vector-search
  - Cosmos DB의 vector search(하이브리드 검색) 기능과 제약사항 확인.
- #fetch:https://learn.microsoft.com/azure/azure-functions/functions-reference-python
  - Azure Functions Python 3.11 런타임과 제한(타임아웃 등) 관련 문서 확인.
- #fetch:https://learn.microsoft.com/azure/static-web-apps/
  - Static Web Apps와 빌드/배포 속성 관련 참조.
- #fetch:https://learn.microsoft.com/azure/storage/blobs/
  - Blob Storage 권장 설정(계층·보안·네이밍) 검토.

### Project Conventions

- 참조: 레포지토리 루트의 `kaist-ai-infra/infra/main.bicep`와 `docs/plan/infrastructure-azure-bicep-1.md`에서 사용되는 리소스명·지역·리소스 그룹 네이밍 규칙과 일치함.

## Key Discoveries

### 누락되었거나 보완 권고 항목

1. **인증 흐름 상세화**: 인증 방식(예: Azure AD/OIDC)과 토큰 발급/검증, 권한 범위(scope)·역할(role) 설계가 명세에 요약되어 있으나, 토큰 만료·갱신, 역할맵(예: uploader, reader, admin)과 엔드포인트별 권한 정책이 구체화되어 있지 않음.

2. **맬웨어 검사 구현 세부사항**: "PDF 파일을 스캔"(SEC-002) 항목이 있지만, 사용될 스캐너(예: 클라우드 AV, 서드파티 서비스, 또는 서버사이드 샌드박스)와 처리 지연·재시도 정책, 실패 시 사용자 알림/버전관리 절차가 빠짐.

3. **데이터 보존·삭제 API**: 보존정책(DAT-004)은 언급되어 있으나, 사용자 요청으로 데이터 삭제(권리 행사지원) 및 자동 만료(cleanup) 작업을 수행하는 API·스케줄러(예: Azure Functions Timer 또는 Azure Logic Apps) 명세가 없음.

4. **비용·RU 소비 예측 지침**: Cosmos DB serverless의 RU 소비 추정, 임계치 초과 시 대처(경보·스케일 전략) 및 비용 모니터링 지표가 부재.

5. **업로드 중단·재개 지원**: 대용량 PDF(최대 50MB) 업로드에서 네트워크 실패 시 업로드 재개 또는 청크 업로드 전략에 대한 명시가 없음.

6. **오류 코드 및 예외 사양**: API 응답 표준(에러 코드, 구조체, 문제 원인별 HTTP 상태 코드 및 메시지 포맷)이 상세하게 정의되어 있지 않음(예: validation error vs processing error vs third-party failure).

7. **스케일/성능 테스트 절차**: 성능 목표(PER-001~PER-004)는 제시되어 있으나, 테스트 데이터셋 구성, 시나리오(동시 사용자 패턴), 측정 방법(어떤 엔드포인트를 어떤 툴로 몇 분간), RU 측정 방식 등이 누락됨.

8. **모니터링·알림 세부 설정**: Application Insights에 수집할 주요 텔레메트리(예: 검색 쿼리 레이턴시, embedding 배치 시간, 실패율), 경보 임계값, 로그 샘플링 정책 미기재.

9. **멀티언어·인코딩 처리 정책**: 다국어 문서 처리와 embedding 모델 선택 정책(언어 감지, 모델 라우팅 등)과 문자 인코딩·토큰화 규칙이 구체화되어 있지 않음.

10. **접근 제어(셀프호스팅 키·시크릿) 운영 절차**: Key Vault 정책(접근자 목록, 비밀 로테이션 주기), Managed Identity에 대한 구체적 역할 바인딩 대상이 빠짐.

11. **테스트용 더미 PDF 및 샘플 데이터**: 테스트·CI 파이프라인에서 사용할 대표 PDF 샘플(작은/큰/다국어/이미지 기반 OCR 필요) 목록이 없음.

12. **비정상 상황의 롤백/재처리 정책**: 처리 실패 시 재시도 횟수, 재처리 큐 설계(idempotency), 중복 삽입 방지 전략이 미정의.

13. **데이터 마이그레이션/백업 전략**: Cosmos DB · Blob Storage 내 백업·복구 절차 및 정기 백업 정책이 없음.

14. **데이터 모델의 인덱싱 전략**: Cosmos DB 컨테이너의 파티션 키 설계(현재 `_partitionKey`로 `userId` 제시됨)와 벡터 인덱스 구성·저장소 비용 고려가 더 구체화될 필요.

15. **API 버전 관리 방침**: `GUD-006`에서 버전관리 권고가 있으나, URL 버전 표기(`/v1/`)·하위호환 정책·데프리케이션 주기가 명세에 없음.

### 권장 보완 사항(우선순위)

- 우선 보완(보안·컴플라이언스): 인증·권한(1), Key Vault·Managed Identity 운영(10), 데이터 삭제/보존 API(3)
- 다음으로 보완(신뢰성·운영): 맬웨어 검사 세부(2), 오류 코드 표준(6), 재처리·롤백 정책(12), 업로드 재개(5)
- 이후 보완(성능·비용): RU 소비 예측·모니터링(4,8), 스케일 테스트 절차(7), 인덱싱·파티셔닝 전략(14)

## Recommended Approach

- 명세는 포괄적이며 좋은 출발점이지만, "운영·보안·테스트" 관점의 실행 세부사항을 더 보강해야 실제 구현·검증이 가능함.
- 사용자 데이터 삭제(법적 요구)를 만족하려면 `DELETE /api/document/{id}` 및 백그라운드 정리 작업을 명세로 추가할 것을 권장.
- 인증은 Azure AD(Entra ID) 기반 OAuth2/OIDC + RBAC 역할맵을 기본으로 채택하고, 최소 권한 원칙을 문서화할 것.

## Implementation Guidance

- **즉시 추가할 항목(작업화 권장)**:
  - 상세한 API 오류 사양서(공통 에러 스키마)
  - 인증·권한 정책 문서(역할 목록과 엔드포인트 매핑)
  - 데이터 삭제/보존 API 및 스케줄러 설계
  - 맬웨어 검사 연동 시나리오(동기 vs 비동기 처리)
  - 업로드 재개(청크 업로드) 설계

- **참고 자료**:
  - #fetch:https://learn.microsoft.com/azure/active-directory/develop/v2-overview
  - #fetch:https://learn.microsoft.com/azure/functions/durable/durable-functions-overview (Durable Functions 권장 시나리오)
  - #fetch:https://learn.microsoft.com/azure/cosmos-db/nosql/partitioning-overview


## 결론

명세는 아키텍처·요구사항·인터페이스·테스트 전략을 잘 포함하고 있습니다. 단, 프로덕션 배포를 위해서는 위에 열거한 운영·보안·테스트 관련 세부사항을 보강하면 완성도가 높아집니다.
