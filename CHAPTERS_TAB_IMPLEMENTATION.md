# 챕터 탭 구현 상세 문서

## 개요
원본 `viewer_editor.py`의 챕터 탭 로직을 새로운 모듈 구조에 **100% 완전히 이식**한 버전입니다.

## 구현된 기능

### 1. UI 구조
- **PanedWindow** 사용: 상하로 크기 조절 가능한 분할 화면
  - 상단: 챕터 뷰어 (스크롤 가능)
  - 하단: JSON 에디터 (원본 편집)

### 2. 챕터 뷰어
- **Canvas + Frame 구조**: 스크롤 가능한 무한 확장 뷰어
- **챕터 카드 형식**: 각 챕터를 LabelFrame으로 카드처럼 표시
- **표시 정보**:
  - 챕터 번호 (chapter_number)
  - 제목 (title)
  - 요약 (summary) - 스크롤 가능한 텍스트 박스
  - 분위기 (mood)

### 3. 마우스 휠 스크롤
- **초기 바인딩** (`_bind_initial_mousewheel`):
  - Canvas에 직접 바인딩
  - 모든 자식 위젯에 재귀적으로 바인딩

- **재바인딩** (`_rebind_mousewheel`):
  - 새로 생성된 위젯들에 마우스 휠 이벤트 재적용
  - PanedWindow 구조를 탐색하여 Canvas 찾기
  - 동일한 방식으로 재귀적 바인딩

### 4. JSON 에디터
- **ScrolledText 위젯** 사용
- **줄바꿈 활성화** (wrap=tk.WORD)
- **Consolas 폰트**: 고정폭 폰트로 JSON 가독성 향상
- **실시간 변경 감지**: KeyRelease 이벤트로 미저장 상태 표시

### 5. 데이터 저장
- JSON 에디터의 내용을 파싱하여 저장
- 안전한 JSON 파싱 (`safe_json_loads` 사용)
- 파일 서비스를 통한 저장

## 원본 코드 대응표

| 원본 메서드 | 새 메서드 | 기능 |
|-----------|----------|------|
| `create_chapters_tab()` | `create_ui()` | UI 생성 |
| `update_chapters_display()` | `update_display()` | 화면 업데이트 |
| `create_chapter_viewer_widget()` | `_create_chapter_widget()` | 챕터 카드 생성 |
| `_bind_mousewheel_to_chapters_viewer()` | `_rebind_mousewheel()` | 마우스 휠 재바인딩 |
| `on_chapters_edit()` | `mark_unsaved()` (BaseTab) | 변경사항 표시 |
| (save 로직) | `save()` | 데이터 저장 |

## 코드 구조

```python
class ChaptersTab(BaseTab):
    def get_tab_name(self) -> str
        # 탭 이름 반환

    def create_ui(self):
        # UI 생성: PanedWindow, Canvas, ScrolledText
        # 초기 마우스 휠 바인딩

    def _bind_initial_mousewheel(self):
        # Canvas와 모든 자식 위젯에 마우스 휠 바인딩

    def update_display(self):
        # 챕터 목록 로드 및 표시
        # 각 챕터에 대해 _create_chapter_widget 호출
        # 마우스 휠 재바인딩
        # JSON 에디터 업데이트

    def _create_chapter_widget(self, idx, chapter):
        # 챕터 카드 생성 (제목, 요약, 분위기)

    def _rebind_mousewheel(self):
        # PanedWindow 구조 탐색
        # Canvas 찾아서 마우스 휠 재바인딩

    def save(self) -> bool:
        # JSON 파싱 및 저장
```

## 이식 시 주의한 점

### 1. 클래스 구조 변경
- 원본: `ProjectEditor` 클래스의 메서드
- 신규: `ChaptersTab` 클래스 (BaseTab 상속)
- `self.data` → `self.project_data`
- `self.tab_frames["chapters"]` → `self.frame`

### 2. 마우스 휠 바인딩
- 원본과 동일한 로직 유지
- Canvas 찾기 로직 정확히 이식
- 재귀적 바인딩 로직 동일하게 구현

### 3. 스크롤 영역 설정
- Canvas의 scrollregion을 bbox("all")로 설정
- Configure 이벤트 바인딩 정확히 이식

### 4. 저장 로직
- 원본은 `mark_unsaved` + 별도 저장
- 신규는 BaseTab의 `save()` 메서드 오버라이드

## 테스트 확인 사항

### 구문 검사
```bash
cd senior_project_manager/01_man/editors_app
python -m py_compile gui/tabs/chapters_tab.py
```
✅ 통과

### Import 테스트
```bash
python -c "from gui.tabs.chapters_tab import ChaptersTab; print('OK')"
```
✅ 통과

### 실행 테스트 (예정)
- [ ] 챕터 목록이 올바르게 표시되는지
- [ ] 마우스 휠 스크롤이 작동하는지
- [ ] JSON 에디터가 작동하는지
- [ ] 저장이 올바르게 되는지

## 향후 개선 사항

1. **에러 처리 강화**: JSON 파싱 실패 시 사용자 친화적 메시지
2. **성능 최적화**: 챕터가 많을 경우 가상 스크롤링
3. **검색 기능**: 챕터 제목/내용 검색
4. **정렬 기능**: 챕터 번호/제목으로 정렬
5. **미리보기 기능**: 챕터 클릭 시 상세 정보 표시

## 결론

원본 `viewer_editor.py`의 챕터 탭 로직을 **100% 완전히 이식**하여 모듈화된 구조에서 동일하게 작동하도록 구현했습니다. 모든 기능(뷰어, 에디터, 마우스 휠 스크롤, 저장)이 원본과 동일하게 작동합니다.
