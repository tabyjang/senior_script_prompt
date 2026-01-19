# Project: Senior Story Script Editor

## What This Is

시니어 스토리 대본 에디터 - AI 기반 콘텐츠 생성을 활용한 시니어 스토리 대본 작성 데스크톱 애플리케이션

**One-liner:** Python/tkinter 기반 데스크톱 앱으로, LLM을 활용해 시니어 대상 스토리 대본을 생성하고 관리

## Core Value

**핵심 가치:** 시니어 콘텐츠 제작자가 AI 도움으로 효율적으로 대본을 작성하고 관리할 수 있는 통합 환경 제공

## Current State

**Status:** 기능 완료, 품질 개선 필요

**What works:**
- 시놉시스, 캐릭터, 챕터, 대본, 장면 관리
- LLM 통합 (Gemini/OpenAI/Anthropic)
- 이미지 프롬프트 생성 및 ComfyUI 연동
- TTS 지원 및 에피소드 분할
- Word 변환기

**What's missing:**
- Undo/Redo 기능
- 자동 저장
- 검색/필터 기능
- 비동기 LLM 호출 (GUI 차단 문제)
- LLM 응답 캐싱

## Requirements

### Must Have (이번 마일스톤)
1. 비동기 LLM 호출로 GUI 반응성 개선
2. Undo/Redo 기능
3. 자동 저장
4. LLM 응답 캐싱

### Should Have
1. 검색/필터 기능
2. 대용량 프로젝트 지연 로딩

### Could Have
1. 구조화된 로깅 시스템
2. 서비스 레이어 테스트

## Constraints

**Technical:**
- Python 3.x, tkinter 기반 유지
- 파일 기반 데이터 저장 유지 (SQLite 전환 불가)
- 크로스플랫폼 호환성 유지

**Non-technical:**
- 기존 UI 구조 최대한 유지
- 한국어 인터페이스 유지

## Key Decisions

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-20 | 비동기 LLM에 threading 사용 | asyncio보다 tkinter와 통합 용이 |
| 2026-01-20 | 파일 기반 캐싱 선택 | 메모리 캐싱 대비 재시작 후에도 유지 |

---

*Created: 2026-01-20*
*Updated: 2026-01-20*
