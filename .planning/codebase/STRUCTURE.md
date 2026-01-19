# 코드베이스 구조

**분석일:** 2026-01-19

## 디렉토리 레이아웃

```
script_editors_app/
├── main.py                     # 애플리케이션 진입점
├── requirements.txt            # Python 의존성
├── config/                     # 설정 관리
│   ├── __init__.py
│   └── config_manager.py
├── models/                     # 데이터 모델
│   ├── __init__.py
│   ├── project_data.py
│   └── piper/                  # TTS 모델 파일 (선택사항)
├── services/                   # 비즈니스 로직 서비스
│   ├── __init__.py
│   ├── llm_service.py
│   ├── file_service.py
│   ├── content_generator.py
│   ├── comfyui_service.py
│   └── google_sheets_service.py
├── gui/                        # 사용자 인터페이스
│   ├── __init__.py
│   ├── main_window.py
│   ├── tabs/                   # 기능 탭
│   │   ├── base_tab.py
│   │   ├── synopsis_input_tab.py
│   │   ├── characters_tab.py
│   │   ├── chapters_tab.py
│   │   ├── scripts_tab.py
│   │   ├── scenes_tab.py
│   │   ├── image_prompts_input_tab.py
│   │   ├── image_generation_tab.py
│   │   ├── comfyui_tab.py
│   │   ├── word_converter_tab.py
│   │   ├── tts_tab.py
│   │   └── episode_splitter_tab.py
│   └── dialogs/
│       ├── __init__.py
│       └── settings_dialog.py
├── utils/                      # 유틸리티 함수
│   ├── __init__.py
│   ├── json_utils.py
│   ├── ui_helpers.py
│   ├── file_utils.py
│   └── word_converter.py
├── prompts/                    # 프로젝트 데이터 저장
│   └── {project_name}/
│       ├── characters/
│       ├── scenes/
│       ├── mappings/
│       └── *_episodes/
├── output/                     # 생성된 출력
│   └── tts/                    # TTS 오디오 파일
├── comfyui_api_server.py      # ComfyUI API 서버
└── comfyui_character_generator.py  # 캐릭터 이미지 생성
```

## 디렉토리 목적

**config/**
- 목적: 애플리케이션 설정 관리
- 포함: API 키, LLM 제공자 설정을 위한 ConfigManager 클래스
- 주요 파일: `config_manager.py`
- 하위 디렉토리: 없음

**models/**
- 목적: 데이터 모델 및 도메인 객체
- 포함: ProjectData 모델, TTS 모델 (선택사항)
- 주요 파일: `project_data.py`
- 하위 디렉토리: `piper/` (TTS 모델 파일)

**services/**
- 목적: 비즈니스 로직 및 외부 서비스 통합
- 포함: LLM 서비스, 파일 서비스, 콘텐츠 생성기, ComfyUI 서비스
- 주요 파일: `llm_service.py` (LLM 통합), `content_generator.py` (콘텐츠 생성), `comfyui_service.py` (이미지 생성)
- 하위 디렉토리: 없음

**gui/**
- 목적: 사용자 인터페이스 컴포넌트
- 포함: 메인 윈도우, 탭, 다이얼로그
- 주요 파일: `main_window.py` (메인 애플리케이션 윈도우)
- 하위 디렉토리: `tabs/` (기능 탭), `dialogs/` (설정 다이얼로그)

**gui/tabs/**
- 목적: 개별 기능 탭
- 포함: BaseTab 추상 클래스 및 구체적인 탭 구현
- 주요 파일: `base_tab.py` (추상 베이스), `synopsis_input_tab.py`, `scripts_tab.py`, `scenes_tab.py` 등
- 하위 디렉토리: 없음

**utils/**
- 목적: 공유 유틸리티 함수
- 포함: JSON 유틸리티, UI 헬퍼, 파일 유틸리티, Word 변환기
- 주요 파일: `json_utils.py`, `ui_helpers.py`, `word_converter.py`
- 하위 디렉토리: 없음

**prompts/**
- 목적: 프로젝트 데이터 저장 (파일 기반 데이터베이스)
- 포함: 캐릭터, 장면, 대본, 매핑이 있는 프로젝트 폴더
- 구조: `{project_name}/characters/*.json`, `{project_name}/scenes/**/*.json`, `{project_name}/*_episodes/**/*.md`
- 하위 디렉토리: 프로젝트당 하나

**output/**
- 목적: 생성된 파일 (TTS 오디오, 이미지)
- 포함: TTS 오디오 파일
- 하위 디렉토리: `tts/`

## 주요 파일 위치

**진입점:**
- `main.py` - 애플리케이션 진입점, 서비스 초기화
- `comfyui_api_server.py` - ComfyUI 통합을 위한 Flask API 서버

**설정:**
- `config/config_manager.py` - 설정 관리
- `requirements.txt` - Python 의존성

**핵심 로직:**
- `services/llm_service.py` - LLM API 통합 (Gemini, OpenAI, Anthropic)
- `services/content_generator.py` - 콘텐츠 생성 오케스트레이션
- `services/file_service.py` - 파일 I/O 작업
- `gui/main_window.py` - 메인 윈도우 및 탭 관리

**테스팅:**
- `test_comfyui.py` - ComfyUI 통합 테스트
- 전용 테스트 디렉토리 없음

**문서:**
- `README.md` - 프로젝트 개요 및 설치 지침
- `*_TAB_IMPLEMENTATION.md` - 탭 구현 문서
- `STORAGE_FORMAT.md` - 데이터 저장 형식 문서

## 네이밍 규칙

**파일:**
- 모든 Python 모듈에 snake_case.py
- GUI 탭에 {feature}_tab.py
- 서비스 클래스에 {feature}_service.py
- 파일 내부의 클래스 이름은 PascalCase

**디렉토리:**
- 모든 디렉토리에 snake_case
- 컬렉션에 복수형: tabs/, dialogs/, services/, utils/

**특수 패턴:**
- Python 패키지 마커를 위한 __init__.py
- 컴파일된 Python 바이트코드를 위한 __pycache__/ (gitignore됨)

## 새 코드 추가 위치

**새 기능 탭:**
- 주 코드: `gui/tabs/{feature}_tab.py`
- 베이스 클래스: `gui/tabs/base_tab.py` 확장
- 등록: `gui/main_window.py`의 `_initialize_tabs()`에 추가

**새 서비스:**
- 구현: `services/{service_name}_service.py`
- 초기화: `main.py` 서비스 초기화에 추가
- 사용: 필요에 따라 MainWindow 또는 탭에 주입

**새 유틸리티:**
- 구현: `utils/{utility_name}.py`
- 모든 레이어에서 임포트

**새 다이얼로그:**
- 구현: `gui/dialogs/{dialog_name}_dialog.py`
- 사용: main_window.py 또는 탭에서 호출

## 특수 디렉토리

**prompts/**
- 목적: 사용자 프로젝트 데이터 (git에 커밋되지 않음, 사용자 생성)
- 출처: 애플리케이션에 의해 생성 및 관리
- 커밋됨: 구조는 문서화됨, 실제 데이터는 커밋되지 않음

**output/**
- 목적: 생성된 파일 (TTS 오디오, 이미지)
- 출처: 애플리케이션에 의해 생성
- 커밋됨: 아니오 (출력 파일은 커밋되지 않음)

**models/piper/**
- 목적: TTS 모델 파일
- 출처: 별도로 다운로드
- 커밋됨: 아니오 (큰 바이너리 파일)

**__pycache__/**
- 목적: Python 컴파일 바이트코드
- 출처: Python 인터프리터에 의해 자동 생성
- 커밋됨: 아니오 (.gitignore됨)

---

*구조 분석: 2026-01-19*
*디렉토리 구조 변경 시 업데이트*
