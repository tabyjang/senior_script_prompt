# 프로젝트 뷰어/에디터 (모듈화 버전)

안전하고 튼튼한 모듈화 구조로 재작성된 프로젝트 뷰어/에디터입니다.

## 폴더 구조

```
editors_app/
├── main.py                          # 진입점
├── config/
│   ├── __init__.py
│   └── config_manager.py            # 설정 관리
├── models/
│   ├── __init__.py
│   └── project_data.py              # 데이터 모델
├── services/
│   ├── __init__.py
│   ├── llm_service.py               # LLM API 통합
│   ├── file_service.py              # 파일 I/O
│   └── content_generator.py         # 콘텐츠 생성
├── gui/
│   ├── __init__.py
│   ├── main_window.py               # 메인 윈도우
│   ├── tabs/
│   │   ├── __init__.py
│   │   ├── base_tab.py              # 탭 베이스 클래스
│   │   ├── synopsis_tab.py          # 시놉시스 탭
│   │   ├── characters_tab.py        # 캐릭터 탭
│   │   ├── chapters_tab.py          # 챕터 탭
│   │   ├── scripts_tab.py           # 대본 탭
│   │   ├── scenes_tab.py            # 장면 탭
│   │   └── image_prompts_tab.py     # 이미지 프롬프트 탭
│   └── dialogs/
│       ├── __init__.py
│       └── settings_dialog.py       # 설정 대화상자
└── utils/
    ├── __init__.py
    ├── json_utils.py                # JSON 유틸리티
    └── ui_helpers.py                # UI 헬퍼 함수
```

## 설치

```bash
# 필수 패키지 설치
pip install tkinter

# LLM 제공자별 패키지 설치 (선택적)
pip install google-generativeai  # Gemini용
pip install openai               # OpenAI용
pip install anthropic            # Anthropic용
```

## 실행 방법

### 기본 실행

```bash
cd senior_project_manager/01_man/editors_app
python main.py
```

### 프로젝트 경로 지정

```bash
python main.py --project ../001_gym_romance
```

## 주요 기능

### 1. 모듈화된 구조
- **config/**: 설정 관리 (API 키, 모델 선택 등)
- **models/**: 데이터 모델 (시놉시스, 캐릭터, 챕터 등)
- **services/**: 비즈니스 로직 (LLM 호출, 파일 I/O, 콘텐츠 생성)
- **gui/**: 사용자 인터페이스 (탭, 다이얼로그 등)
- **utils/**: 유틸리티 함수 (JSON 처리, UI 헬퍼 등)

### 2. 안전한 파일 관리
- 모든 파일 I/O는 `FileService` 클래스를 통해 관리
- 오류 처리 및 검증 강화
- 자동 백업 및 복구 기능 (예정)

### 3. 확장 가능한 LLM 통합
- Gemini, OpenAI, Anthropic API 통합
- 제공자별 최적화된 파라미터 설정
- 오류 처리 및 재시도 로직

### 4. 사용자 친화적 GUI
- 탭 기반 인터페이스
- 뷰어/에디터 분리
- 자동 저장 및 변경사항 추적

## 개발 가이드

### 새 탭 추가하기

1. `gui/tabs/` 폴더에 새 파일 생성 (예: `new_tab.py`)
2. `BaseTab` 클래스를 상속받아 구현

```python
from gui.tabs.base_tab import BaseTab

class NewTab(BaseTab):
    def get_tab_name(self) -> str:
        return "새 탭"

    def create_ui(self):
        # UI 생성 로직
        pass

    def update_display(self):
        # 화면 업데이트 로직
        pass

    def save(self) -> bool:
        # 저장 로직
        return True
```

3. `gui/main_window.py`의 `_initialize_tabs()` 메서드에 탭 추가

### 새 서비스 추가하기

1. `services/` 폴더에 새 파일 생성
2. 서비스 클래스 구현
3. `main.py`에서 인스턴스 생성 및 전달

## 현재 상태

### 구현 완료
- ✅ 폴더 구조 생성
- ✅ 설정 관리 모듈
- ✅ 데이터 모델
- ✅ 서비스 레이어 (LLM, 파일, 콘텐츠 생성)
- ✅ 유틸리티 함수
- ✅ 메인 윈도우
- ✅ 시놉시스 탭 (완전 구현)
- ✅ 캐릭터 탭 (간소화 버전)
- ✅ **챕터 탭 (완전 구현)** - 원본 로직 100% 이식
  - 스크롤 가능한 챕터 카드 뷰어
  - JSON 에디터
  - 마우스 휠 스크롤 지원
  - 챕터 정보 표시 (번호, 제목, 요약, 분위기)
- ✅ **이미지 프롬프트 탭 (완전 구현)** - 원본 로직 100% 이식
  - 5가지 서브탭 (전신샷, 초상화, 옆모습, 액션, 자연스러운 배경)
  - 스크롤 가능한 캐릭터별 프롬프트 뷰어
  - 시스템 프롬프트 에디터 (LLM 지시사항)
  - JSON 에디터
  - LLM 기반 자동 생성 (5종류 일괄 생성)
  - 마우스 휠 스크롤 지원
  - 프롬프트별 개별 저장
- ✅ **대본 탭 (완전 구현)** - 원본 로직 100% 이식
  - 챕터별 대본 관리 (콤보박스 선택)
  - 읽기 전용 뷰어 (TTS 복사용)
  - 편집 가능 에디터
  - LLM 기반 자동 생성 (개별/일괄)
  - 이전 챕터 참고를 통한 연속성 유지
  - TTS 최적화 (5000자 내외)
  - 실시간 글자 수 표시
  - 자동 저장
- ✅ **장면 탭 (완전 구현)** - 원본 로직 100% 이식
  - 좌우 분할 UI (대본 | 장면 목록)
  - 챕터당 10개 장면 자동 생성
  - LLM 기반 장면 분석 및 생성
  - Stable Diffusion 최적화 이미지 프롬프트
  - 클립보드 복사 기능 (📋 복사)
  - 일괄 생성 (백그라운드 스레드, 3초 딜레이)
  - 마우스 휠 스크롤 지원
  - 자동 저장

### 구현 예정
- ⏳ 자동 백업 기능
- ⏳ 버전 관리 기능

## 라이선스

MIT License

## 문의

이슈나 문의사항은 GitHub Issues를 통해 남겨주세요.
