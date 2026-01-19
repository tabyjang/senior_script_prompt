# 기술 스택

**분석일:** 2026-01-19

## 언어

**주 언어:**
- Python 3.x - 모든 애플리케이션 코드

**보조 언어:**
- JSON - 캐릭터, 장면, 매핑 데이터 저장 형식
- Markdown - 에피소드 대본 및 문서

## 런타임

**환경:**
- Python 3.x (3.8+ 추정)
- Windows/Linux/macOS (크로스플랫폼 데스크톱 애플리케이션)

**패키지 관리자:**
- pip
- Lockfile: 감지되지 않음 (requirements.txt만 있음)

## 프레임워크

**핵심:**
- tkinter - GUI 프레임워크 (Python 내장)
- tkinterdnd2 - 드래그 앤 드롭 지원 (선택사항)

**API 서버:**
- Flask 2.3.0+ - ComfyUI API 서버 (`comfyui_api_server.py`)
- flask-cors 4.0.0+ - CORS 지원

**빌드/개발:**
- 해당 없음 (인터프리터 언어인 Python)

## 주요 의존성

**필수:**
- google-generativeai - Gemini AI 통합 (`services/llm_service.py`)
- openai - OpenAI API 통합 (선택사항)
- anthropic - Anthropic API 통합 (선택사항)
- flask - ComfyUI 통합을 위한 REST API 서버

**인프라:**
- pathlib - 경로 처리 (Python 내장)
- argparse - 커맨드라인 인자 파싱 (Python 내장)
- json - JSON 데이터 처리 (Python 내장)
- tkinter - GUI 컴포넌트 (Python 내장)

## 설정

**환경:**
- `config/config_manager.py`를 통한 설정
- API 키는 config에 저장 (provider, api_key, model)
- 프로젝트 경로는 커맨드라인으로 지정: `--prompts`, `--project`

**빌드:**
- 빌드 설정 없음 (인터프리터 언어)
- TensorFlow 환경 변수 설정으로 경고 억제

## 플랫폼 요구사항

**개발:**
- Python 3.x 설치
- 선택사항: 드래그 앤 드롭을 위한 tkinterdnd2
- 선택사항: LLM 제공자 패키지 (google-generativeai, openai, anthropic)

**프로덕션:**
- 데스크톱 애플리케이션 (웹 기반 아님)
- 사용자 머신에서 로컬 실행
- LLM 제공자를 위한 API 키 필요

---

*스택 분석: 2026-01-19*
*주요 의존성 변경 시 업데이트*
