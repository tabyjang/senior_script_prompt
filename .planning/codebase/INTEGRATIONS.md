# 외부 통합

**분석일:** 2026-01-19

## API 및 외부 서비스

**AI/LLM 서비스:**
- Google Gemini - 대본 콘텐츠 생성, 캐릭터 설명, 장면 분석
  - SDK/클라이언트: google-generativeai 패키지
  - 인증: config의 API 키 (GOOGLE_API_KEY 환경 변수)
  - 사용 모델: gemini-1.5-flash, gemini-2.0-flash-exp
  - 통합: `services/llm_service.py`

- OpenAI - 대체 LLM 제공자 (선택사항)
  - SDK/클라이언트: openai 패키지
  - 인증: config의 API 키
  - 사용 모델: 설정에서 구성 가능
  - 통합: `services/llm_service.py`

- Anthropic Claude - 대체 LLM 제공자 (선택사항)
  - SDK/클라이언트: anthropic 패키지
  - 인증: config의 API 키
  - 사용 모델: 설정에서 구성 가능
  - 통합: `services/llm_service.py`

**이미지 생성:**
- ComfyUI - API를 통한 캐릭터 이미지 생성
  - 통합 방법: Flask 서버를 통한 REST API (`comfyui_api_server.py`)
  - 엔드포인트: 캐릭터 생성 워크플로우
  - 통합: `services/comfyui_service.py`, `gui/tabs/comfyui_tab.py`
  - 워크플로우: `prompts/workflows/`의 JSON 워크플로우 파일

## 데이터 저장

**데이터베이스:**
- 없음 - 파일 기반 저장만 사용

**파일 저장:**
- 로컬 파일시스템 - 모든 프로젝트 데이터는 `prompts/` 폴더 구조에 저장
  - 캐릭터: `prompts/{project}/characters/*.json`
  - 장면: `prompts/{project}/scenes/**/*.json`
  - 대본: `prompts/{project}/*_episodes/**/*.md`
  - 매핑: `prompts/{project}/mappings/*.json`

**캐싱:**
- 없음

## 인증 및 신원 확인

**인증 제공자:**
- 없음 - 로컬 애플리케이션, 사용자 인증 없음

**API 키:**
- LLM 제공자: `config/config_manager.py`를 통해 config에 저장
- OAuth 통합 없음

## 모니터링 및 가시성

**오류 추적:**
- 없음 - 콘솔 출력만

**분석:**
- 없음

**로그:**
- 표준 출력 (stdout/stderr)
- 환경 변수를 통해 TensorFlow 경고 억제

## CI/CD 및 배포

**호스팅:**
- 로컬 데스크톱 애플리케이션
- 배포 파이프라인 없음

**CI 파이프라인:**
- 감지되지 않음

## 환경 설정

**개발:**
- 필수 설정: LLM 제공자 API 키
- 설정 위치: `config/config_manager.py`로 관리
- 프로젝트 경로: 커맨드라인 인자로 지정

**프로덕션:**
- 개발과 동일 (로컬 데스크톱 앱)

## 웹훅 및 콜백

**수신:**
- 없음

**발신:**
- 없음

---

*통합 감사: 2026-01-19*
*외부 서비스 추가/제거 시 업데이트*
