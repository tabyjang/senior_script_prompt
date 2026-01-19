# 코딩 규칙

**분석일:** 2026-01-19

## 네이밍 패턴

**파일:**
- 모든 Python 파일에 snake_case (main.py, config_manager.py, llm_service.py)
- 카테고리 접미사가 있는 설명적 이름: *_service.py, *_tab.py, *_dialog.py
- 테스트 파일: test_*.py (예: test_comfyui.py)

**함수:**
- 모든 함수에 snake_case
- Private 메서드: _leading_underscore (예: `_call_gemini`, `_setup_window`)
- 설명적 이름: get_*, set_*, create_*, load_*, save_*
- 도메인 특정 용어를 위한 프롬프트/주석에 한국어 이름

**변수:**
- 변수에 snake_case
- 설명적 이름: project_path, config_manager, file_service
- 루프 카운터를 제외하고 단일 문자 변수 없음
- UI 레이블에 한국어 변수 이름

**클래스:**
- 클래스 이름에 PascalCase (ConfigManager, LLMService, BaseTab)
- 설명적 접미사: *Service, *Tab, *Dialog, *Manager
- 접두사 규칙 없음 (인터페이스에 I 없음)

**타입:**
- Python 타입 힌트 사용: Optional[str], Path, bool
- 코드베이스 전체에 광범위하게 사용되지 않음

## 코드 스타일

**포매팅:**
- 4칸 들여쓰기 (Python 표준)
- 포맷터 설정 감지 안됨 (.prettierrc, .black 등)
- 혼합된 줄 길이 (엄격한 제한 없음)

**린팅:**
- 린터 설정 감지 안됨 (.pylintrc, .flake8 등)

**Docstring:**
- 모듈 및 클래스에 삼중 따옴표 docstring
- 함수 docstring은 있지만 일관성 없음
- 주석 및 docstring에 한국어 사용
- 일부 docstring에서 Args/Returns 형식 사용

## Import 구성

**순서:**
1. 표준 라이브러리 import (os, sys, pathlib, argparse)
2. 서드파티 패키지 (tkinter, flask)
3. 로컬 애플리케이션 import (config, models, services, gui, utils)

**그룹핑:**
- import 그룹 간 빈 줄
- 로컬 패키지에서 상대 import: `from config.config_manager import ConfigManager`
- 표준 라이브러리에 절대 import

**경로 처리:**
- os.path보다 pathlib.Path 선호
- Path 객체를 일관되게 사용

## 오류 처리

**패턴:**
- 서비스 경계에서 Try/except 블록
- 한국어로 된 사용자 친화적 오류 메시지
- GUI 오류 표시를 위한 messagebox
- 설치 지침과 함께 누락된 선택적 의존성에 대한 ImportError

**오류 타입:**
- 잘못된 설정에 대한 ValueError
- 누락된 패키지에 대한 ImportError
- GUI 이벤트 핸들러에서 일반 Exception 캐칭

**지연 Import:**
- `services/llm_service.py`에서 지연 임포트된 선택적 의존성
- 지연 초기화 패턴을 사용한 전역 모듈 참조

## 로깅

**프레임워크:**
- 콘솔 출력을 위한 print() 문
- 구조화된 로깅 프레임워크 없음

**패턴:**
- 한국어 메시지: `print(f"[시작] prompts 폴더: {prompts_path}")`
- 주요 작업에 대한 상태 메시지
- 로그 레벨 없음 (debug, info, warn, error)

## 주석

**주석 시기:**
- 목적을 설명하는 모듈 수준 docstring
- 비즈니스 로직에 한국어 주석
- 기술적 세부사항에 영어 주석
- 명확하지 않은 코드에 대한 "왜"를 설명하는 주석

**Docstring:**
- 파일 상단의 모듈 docstring
- 목적을 설명하는 클래스 docstring
- Args/Returns 형식을 사용하는 메서드 docstring (일관성 없음)
- 도메인 특정 설명에 한국어 사용

**TODO 주석:**
- 코드베이스에서 관찰되지 않음
- README.md에서 추적되는 구현 상태

## 함수 디자인

**크기:**
- 함수 범위 10-100+ 줄
- 큰 함수 존재 (엄격하게 제한되지 않음)
- _ 접두사로 추출된 헬퍼 메서드

**매개변수:**
- 여러 매개변수가 일반적 (5-8개 매개변수)
- 의존성 주입 사용 (config_manager, file_service 전달됨)
- 타입 힌트가 일관성 없이 사용됨

**반환 값:**
- 실패할 수 있는 함수에 Optional[str]
- save/유효성 검사 메서드에 bool
- 명시적 return 문

## 모듈 디자인

**Export:**
- 직접 임포트되는 클래스: `from gui.main_window import MainWindow`
- __all__ 선언 없음
- 공식적으로 정의된 공개 API 없음

**패키지 구조:**
- __init__.py 파일이 있지만 비어 있음
- 배럴 파일 패턴 없음

---

*규칙 분석: 2026-01-19*
*패턴 변경 시 업데이트*
