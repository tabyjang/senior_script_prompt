# Roadmap: Senior Story Script Editor v1.1

## Overview

성능 최적화와 누락된 핵심 기능을 추가하여 사용자 경험을 개선. GUI 반응성 문제 해결을 최우선으로 하고, 이후 Undo/Redo, 자동 저장, 캐싱 순으로 진행.

## Domain Expertise

None (Python/tkinter 표준 패턴 사용)

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [ ] **Phase 1: Async LLM** - 비동기 LLM 호출로 GUI 반응성 개선
- [ ] **Phase 2: Undo/Redo** - 편집 실행 취소 및 재실행 기능
- [ ] **Phase 3: Auto-save** - 자동 저장 시스템
- [ ] **Phase 4: LLM Caching** - LLM 응답 캐싱으로 API 비용 절감
- [ ] **Phase 5: Search/Filter** - 프로젝트 전체 검색 및 필터 기능

## Phase Details

### Phase 1: Async LLM
**Goal**: LLM API 호출을 비동기로 전환하여 생성 중 GUI 멈춤 해결
**Depends on**: Nothing (first phase)
**Research**: Unlikely (표준 threading 패턴)
**Plans**: TBD

핵심 작업:
- threading.Thread를 사용한 LLM 호출 래핑
- 진행 표시기 UI 추가
- 콜백 기반 결과 처리

### Phase 2: Undo/Redo
**Goal**: 편집 작업에 대한 실행 취소/재실행 기능 제공
**Depends on**: Phase 1
**Research**: Unlikely (Command 패턴)
**Plans**: TBD

핵심 작업:
- Command 패턴 기반 액션 히스토리
- 탭별 Undo/Redo 스택
- Ctrl+Z, Ctrl+Y 단축키

### Phase 3: Auto-save
**Goal**: 주기적 자동 저장으로 데이터 손실 방지
**Depends on**: Phase 2
**Research**: Unlikely (타이머 + dirty flag)
**Plans**: TBD

핵심 작업:
- 변경 감지 (dirty flag)
- 주기적 저장 타이머
- 자동 저장 상태 표시

### Phase 4: LLM Caching
**Goal**: 동일 프롬프트에 대한 LLM 응답 캐싱
**Depends on**: Phase 1
**Research**: Unlikely (파일 기반 캐시)
**Plans**: TBD

핵심 작업:
- 프롬프트 해시 기반 캐시 키
- 파일 기반 캐시 저장소
- 캐시 만료 정책

### Phase 5: Search/Filter
**Goal**: 프로젝트, 캐릭터, 장면 전체에서 검색 및 필터
**Depends on**: Phase 3
**Research**: Unlikely (인메모리 검색)
**Plans**: TBD

핵심 작업:
- 검색 UI (검색바 + 결과 목록)
- 콘텐츠 인덱싱
- 필터 옵션

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Async LLM | 0/? | Not started | - |
| 2. Undo/Redo | 0/? | Not started | - |
| 3. Auto-save | 0/? | Not started | - |
| 4. LLM Caching | 0/? | Not started | - |
| 5. Search/Filter | 0/? | Not started | - |
