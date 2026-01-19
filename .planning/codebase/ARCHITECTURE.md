# 아키텍처

**분석일:** 2026-01-19

## 패턴 개요

**전체:** 서비스 레이어를 갖춘 모듈화된 데스크톱 GUI 애플리케이션

**주요 특징:**
- tkinter GUI를 사용하는 데스크톱 애플리케이션
- 서비스 지향 아키텍처 (config, models, services, GUI)
- 파일 기반 데이터 영속성
- 이벤트 기반 GUI 상호작용
- 선택적 의존성에 대한 지연 로딩

## 레이어

**GUI 레이어:**
- 목적: 사용자 인터페이스 및 상호작용 처리
- 포함: 메인 윈도우, 탭 (시놉시스, 캐릭터, 대본, 장면 등), 다이얼로그
- 위치: `gui/main_window.py`, `gui/tabs/*.py`, `gui/dialogs/*.py`
- 의존: Services 레이어, models 레이어, utils
- 사용처: 사용자 상호작용

**Services 레이어:**
- 목적: 비즈니스 로직 및 외부 서비스 통합
- 포함: LLM 통합, 파일 I/O, 콘텐츠 생성, ComfyUI 통합
- 위치: `services/llm_service.py`, `services/file_service.py`, `services/content_generator.py`, `services/comfyui_service.py`
- 의존: Config 레이어, 외부 API
- 사용처: GUI 레이어

**Models 레이어:**
- 목적: 데이터 구조 및 도메인 모델
- 포함: ProjectData 모델
- 위치: `models/project_data.py`
- 의존: 없음 (순수 데이터 구조)
- 사용처: Services 레이어, GUI 레이어

**Config 레이어:**
- 목적: 애플리케이션 설정 및 세팅 관리
- 포함: API 키, 제공자 선택을 위한 ConfigManager
- 위치: `config/config_manager.py`
- 의존: 파일 시스템
- 사용처: Services 레이어

**Utils 레이어:**
- 목적: 공유 유틸리티 및 헬퍼 함수
- 포함: JSON 유틸리티, UI 헬퍼, 파일 변환기
- 위치: `utils/json_utils.py`, `utils/ui_helpers.py`, `utils/word_converter.py`
- 의존: 없음 (순수 함수)
- 사용처: 모든 레이어

## 데이터 흐름

**애플리케이션 시작:**

1. 사용자 실행: `python main.py [--prompts path]`
2. `main.py`가 모든 서비스 초기화 (ConfigManager, ProjectData, FileService, LLMService, ContentGenerator)
3. tkinter 루트 윈도우 생성
4. 서비스와 함께 MainWindow 초기화
5. MainWindow가 prompts 폴더에서 프로젝트 목록 로드
6. 사용자가 드롭다운에서 프로젝트 선택
7. 탭이 프로젝트 데이터 로드 및 표시

**콘텐츠 생성 흐름:**

1. 사용자가 탭에서 "생성" 버튼 클릭
2. 탭이 `content_generator.generate_*()` 메서드 호출
3. ContentGenerator가 시스템 지시사항과 함께 프롬프트 준비
4. LLMService가 적절한 제공자로 라우팅 (Gemini/OpenAI/Anthropic)
5. 프롬프트로 API 호출
6. 응답 파싱 및 반환
7. 탭이 생성된 콘텐츠로 UI 업데이트
8. FileService가 JSON/Markdown 파일에 데이터 저장

**상태 관리:**
- 파일 기반: 모든 상태가 `prompts/` 폴더에 영속화
- ProjectData 모델이 현재 프로젝트 상태를 메모리에 보관
- 각 탭이 자체 UI 상태 관리
- 서비스 싱글톤 스타일 인스턴스를 넘어서는 전역 상태 없음

## 주요 추상화

**BaseTab:**
- 목적: 모든 GUI 탭을 위한 추상 베이스 클래스
- 위치: `gui/tabs/base_tab.py`
- 패턴: 템플릿 메서드 패턴
- 제공: `get_tab_name()`, `create_ui()`, `update_display()`, `save()` 메서드

**Service 클래스:**
- 목적: 비즈니스 로직 도메인 캡슐화
- 예시: `services/llm_service.py`, `services/file_service.py`, `services/content_generator.py`
- 패턴: 서비스 레이어 패턴
- 각 서비스가 하나의 도메인 관리 (LLM 호출, 파일, 콘텐츠 생성)

**ConfigManager:**
- 목적: 중앙 집중식 설정 관리
- 위치: `config/config_manager.py`
- 패턴: 싱글톤 스타일 (하나의 인스턴스가 전달됨)

## 진입점

**CLI 진입점:**
- 위치: `main.py`
- 트리거: 사용자가 `python main.py` 실행
- 책임: 서비스 초기화, GUI 생성, 이벤트 루프 시작

**GUI 이벤트 루프:**
- 위치: `gui/main_window.py` → `root.mainloop()`
- 트리거: 애플리케이션 초기화 후
- 책임: 사용자 상호작용, 버튼 클릭, 탭 전환 처리

## 오류 처리

**전략:** 사용자 대면 오류 메시지와 함께 서비스 경계에서 Try/catch

**패턴:**
- try/except 블록으로 래핑된 LLM 호출
- `tkinter.messagebox`를 통해 표시되는 오류
- 선택적 의존성에 대한 지연 임포트 (google-generativeai, openai, anthropic)
- 사용자 친화적인 설치 지침과 함께 발생하는 ImportError

## 횡단 관심사

**로깅:**
- `print()` 문을 통한 콘솔 출력
- 환경 변수를 통해 억제되는 TensorFlow 경고

**유효성 검사:**
- LLMService의 API 키 유효성 검사
- FileService의 파일 경로 유효성 검사
- JSON 스키마 유효성 검사 (암시적)

**오류 메시지:**
- tkinter messagebox를 통한 사용자 친화적인 오류 다이얼로그
- 한국어 UI 메시지

---

*아키텍처 분석: 2026-01-19*
*주요 패턴 변경 시 업데이트*
