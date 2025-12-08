"""
캐릭터 탭
캐릭터 뷰어 및 에디터를 제공합니다.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from .base_tab import BaseTab
from utils.json_utils import format_json, safe_json_loads
from utils.ui_helpers import create_scrollable_frame


class CharactersTab(BaseTab):
    """캐릭터 탭 클래스"""

    def get_tab_name(self) -> str:
        return "인물"

    def create_ui(self):
        """UI 생성"""
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)

        # 상단: 툴바
        toolbar = ttk.Frame(self.frame)
        toolbar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Label(toolbar, text="캐릭터 관리:", font=("맑은 고딕", 10, "bold")).pack(side=tk.LEFT, padx=5)

        # PanedWindow로 크기 조절 가능하게
        paned = ttk.PanedWindow(self.frame, orient=tk.VERTICAL)
        paned.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # 상단: 뷰어 영역
        viewer_frame = ttk.LabelFrame(paned, text="뷰어", padding=10)
        paned.add(viewer_frame, weight=1)
        viewer_frame.columnconfigure(0, weight=1)
        viewer_frame.rowconfigure(0, weight=1)

        # 스크롤 가능한 뷰어
        canvas, self.viewer_frame, scrollbar = create_scrollable_frame(viewer_frame)
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 하단: 원본 JSON 에디터
        editor_frame = ttk.LabelFrame(paned, text="원본 JSON 에디터", padding=10)
        paned.add(editor_frame, weight=1)
        editor_frame.columnconfigure(0, weight=1)
        editor_frame.rowconfigure(0, weight=1)

        self.editor = scrolledtext.ScrolledText(
            editor_frame,
            width=120,
            height=25,
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        self.editor.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.editor.bind('<KeyRelease>', lambda e: self.mark_unsaved())

    def update_display(self):
        """화면 업데이트"""
        # 기존 위젯 제거
        for widget in self.viewer_frame.winfo_children():
            widget.destroy()

        characters = self.project_data.get_characters()

        if not characters:
            ttk.Label(
                self.viewer_frame,
                text="인물 정보가 없습니다.",
                font=("맑은 고딕", 11)
            ).pack(pady=20)
            self.editor.delete(1.0, tk.END)
            self.editor.insert(1.0, "[]")
            return

        # 뷰어에 인물 정보 표시
        for idx, char in enumerate(characters):
            self._create_character_widget(idx, char)

        # 에디터에 JSON 표시
        self.editor.delete(1.0, tk.END)
        json_str = format_json(characters)
        self.editor.insert(1.0, json_str)

    def _create_character_widget(self, idx: int, char: dict):
        """캐릭터 위젯 생성 (간소화)"""
        frame = ttk.LabelFrame(
            self.viewer_frame,
            text=char.get('name', '알 수 없음'),
            padding=15
        )
        frame.pack(fill=tk.X, padx=15, pady=10)

        # 이름
        ttk.Label(
            frame,
            text=f"이름: {char.get('name', '')}",
            font=("맑은 고딕", 10)
        ).pack(fill=tk.X, pady=2)

        # 역할
        ttk.Label(
            frame,
            text=f"역할: {char.get('role', '')}",
            font=("맑은 고딕", 10)
        ).pack(fill=tk.X, pady=2)

    def save(self) -> bool:
        """데이터 저장"""
        json_str = self.editor.get(1.0, tk.END).strip()
        if json_str:
            characters = safe_json_loads(json_str)
            if characters is not None:
                self.project_data.set_characters(characters)
                return self.file_service.save_characters(characters)
        return False
