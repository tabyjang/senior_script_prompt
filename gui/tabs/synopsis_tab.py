"""
시놉시스 탭
시놉시스 뷰어 및 에디터를 제공합니다.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from .base_tab import BaseTab
from utils.json_utils import format_json, safe_json_loads


class SynopsisTab(BaseTab):
    """시놉시스 탭 클래스"""

    def get_tab_name(self) -> str:
        return "시놉시스"

    def create_ui(self):
        """UI 생성"""
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

        # PanedWindow로 크기 조절 가능하게 (상하 분할)
        paned_vertical = ttk.PanedWindow(self.frame, orient=tk.VERTICAL)
        paned_vertical.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # 상단: 좌우 분할 영역
        top_container = ttk.Frame(paned_vertical)
        paned_vertical.add(top_container, weight=2)
        top_container.columnconfigure(0, weight=1)
        top_container.rowconfigure(0, weight=1)

        # 좌우 분할 PanedWindow
        paned_horizontal = ttk.PanedWindow(top_container, orient=tk.HORIZONTAL)
        paned_horizontal.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 왼쪽: 뷰어 영역
        viewer_frame = ttk.LabelFrame(paned_horizontal, text="뷰어", padding=10)
        paned_horizontal.add(viewer_frame, weight=2)
        viewer_frame.columnconfigure(0, weight=1)
        viewer_frame.rowconfigure(0, weight=1)

        self.viewer = scrolledtext.ScrolledText(
            viewer_frame,
            width=120,
            height=30,
            wrap=tk.WORD,
            font=("맑은 고딕", 11),
            state=tk.DISABLED
        )
        self.viewer.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 오른쪽: 시스템 프롬프트 편집 영역
        system_prompt_frame = ttk.LabelFrame(paned_horizontal, text="시놉시스 시스템 프롬프트", padding=10)
        paned_horizontal.add(system_prompt_frame, weight=1)
        system_prompt_frame.columnconfigure(0, weight=1)
        system_prompt_frame.rowconfigure(0, weight=1)

        self.synopsis_system_prompt_editor = scrolledtext.ScrolledText(
            system_prompt_frame,
            width=60,
            height=40,
            wrap=tk.WORD,
            font=("맑은 고딕", 10)
        )
        self.synopsis_system_prompt_editor.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.synopsis_system_prompt_editor.bind('<KeyRelease>', lambda e: self._on_system_prompt_edit())

        # 기본 시스템 프롬프트 로드
        self._load_synopsis_system_prompt()

        # 하단: 원본 JSON 에디터
        editor_frame = ttk.LabelFrame(paned_vertical, text="원본 JSON 에디터", padding=10)
        paned_vertical.add(editor_frame, weight=1)
        editor_frame.columnconfigure(0, weight=1)
        editor_frame.rowconfigure(0, weight=1)

        self.editor = scrolledtext.ScrolledText(
            editor_frame,
            width=120,
            height=30,
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        self.editor.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.editor.bind('<KeyRelease>', lambda e: self.mark_unsaved())

    def update_display(self):
        """화면 업데이트"""
        synopsis = self.project_data.get_synopsis()

        # 뷰어 업데이트
        self.viewer.config(state=tk.NORMAL)
        self.viewer.delete(1.0, tk.END)

        if synopsis:
            formatted_text = self._format_synopsis_for_viewer(synopsis)
            self.viewer.insert(1.0, formatted_text)
        else:
            self.viewer.insert(1.0, "시놉시스 데이터가 없습니다.")

        self.viewer.config(state=tk.DISABLED)

        # 에디터 업데이트
        self.editor.delete(1.0, tk.END)
        json_str = format_json(synopsis)
        self.editor.insert(1.0, json_str)

    def _format_synopsis_for_viewer(self, synopsis: dict) -> str:
        """시놉시스 데이터를 읽기 쉽게 포맷팅"""
        lines = []

        # 프로젝트 정보
        if 'project_id' in synopsis:
            lines.append(f"프로젝트 ID: {synopsis['project_id']}")
        if 'keyword' in synopsis:
            lines.append(f"키워드: {synopsis['keyword']}")
        if 'status' in synopsis:
            lines.append(f"상태: {synopsis['status']}")
        if 'created_at' in synopsis:
            lines.append(f"생성일: {synopsis['created_at']}")
        if any(key in synopsis for key in ['project_id', 'keyword', 'status', 'created_at']):
            lines.append("")

        # 제목
        if 'title' in synopsis:
            lines.append(f"제목: {synopsis['title']}")
            lines.append("")

        # 시놉시스
        if 'synopsis' in synopsis:
            lines.append("시놉시스:")
            lines.append(synopsis['synopsis'])
            lines.append("")
        elif 'summary' in synopsis:
            lines.append("요약:")
            lines.append(synopsis['summary'])
            lines.append("")

        # 전체 스토리
        if 'full_story' in synopsis:
            lines.append("전체 스토리:")
            lines.append(synopsis['full_story'])
            lines.append("")

        # 장르
        if 'genre' in synopsis:
            lines.append(f"장르: {synopsis['genre']}")
            lines.append("")

        # 테마
        if 'theme' in synopsis:
            lines.append(f"테마: {synopsis['theme']}")
            lines.append("")

        # 주요 인물
        if 'characters' in synopsis and synopsis['characters']:
            lines.append("주요 인물:")
            for char in synopsis['characters']:
                name = char.get('name', '알 수 없음')
                role = char.get('role', '')
                age = char.get('age', '')
                occupation = char.get('occupation', '')
                char_line = f"  - {name}"
                if role:
                    char_line += f" ({role})"
                if age:
                    char_line += f", {age}세"
                if occupation:
                    char_line += f", {occupation}"
                lines.append(char_line)
            lines.append("")

        return "\n".join(lines)

    def _load_synopsis_system_prompt(self):
        """
        시놉시스 시스템 프롬프트 로드 (기본값)
        """
        default_prompt = """당신은 소설/드라마 시놉시스 작성 전문가입니다.
주어진 키워드와 요구사항을 바탕으로 상세하고 매력적인 시놉시스를 작성해주세요.

**중요 원칙**:
1. 50-70대 시니어 남성 독자를 위한 콘텐츠이므로 품격 있고 세련된 표현을 사용하세요
2. 로맨스와 성취감, 의리와 도덕 중심의 스토리를 구성하세요
3. 인물 관계와 갈등을 명확하게 설정하세요
4. 전체 스토리의 흐름이 자연스럽고 매력적이어야 합니다
5. 반드시 JSON 형식으로만 응답해주세요

**시놉시스 구성 요소**:
- 제목: 매력적이고 기억에 남는 제목
- 시놉시스: 전체 스토리의 핵심을 담은 간결한 요약 (200-300자)
- 전체 스토리: 상세한 스토리 설명 (1000-2000자)
- 주요 인물: 등장인물의 이름, 나이, 역할, 직업, 외모, 성격 등
- 장르: 로맨스, 드라마 등
- 테마: 사랑, 성취, 의리 등"""

        self.synopsis_system_prompt_editor.delete(1.0, tk.END)
        self.synopsis_system_prompt_editor.insert(1.0, default_prompt)

    def _on_system_prompt_edit(self):
        """시놉시스 시스템 프롬프트 편집 시 호출"""
        # TODO: 설정 파일에 저장하도록 구현
        pass

    def save(self) -> bool:
        """데이터 저장"""
        json_str = self.editor.get(1.0, tk.END).strip()
        if json_str:
            synopsis = safe_json_loads(json_str)
            if synopsis is not None:
                self.project_data.set_synopsis(synopsis)
                return self.file_service.save_synopsis(synopsis)
        return False
