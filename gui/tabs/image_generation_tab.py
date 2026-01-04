"""
인물 탭
인물별 정보를 탭 형식으로 표시합니다.
"""

import tkinter as tk
from tkinter import ttk
from .base_tab import BaseTab
import json


class ImageGenerationTab(BaseTab):
    """인물 탭 클래스"""

    def __init__(self, parent, project_data, file_service, content_generator):
        """초기화"""
        self.character_notebook = None
        self.character_tabs = {}

        # 부모 클래스 초기화
        super().__init__(parent, project_data, file_service, content_generator)

    def get_tab_name(self) -> str:
        return "인물"

    def create_ui(self):
        """UI 생성"""
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

        # 메인 컨테이너
        main_container = ttk.Frame(self.frame)
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)

        # 상단: 인물 선택 탭 (Notebook)
        self.character_notebook = ttk.Notebook(main_container)
        self.character_notebook.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

    def update_display(self):
        """화면 업데이트 - 인물별 탭 생성"""
        if not self.character_notebook:
            return

        # 기존 탭 모두 제거
        for tab_id in self.character_notebook.tabs():
            self.character_notebook.forget(tab_id)
        self.character_tabs.clear()

        characters = self.project_data.get_characters()

        if not characters:
            # 인물이 없을 때
            empty_frame = ttk.Frame(self.character_notebook, padding=20)
            self.character_notebook.add(empty_frame, text="인물 없음")
            ttk.Label(
                empty_frame,
                text="등록된 인물이 없습니다.\n\ncharacters 폴더에 인물 JSON 파일을 추가하세요.",
                font=("맑은 고딕", 11),
                justify=tk.CENTER
            ).pack(expand=True)
            return

        # 각 인물별 탭 생성
        for idx, character in enumerate(characters):
            char_name = character.get('name', '') or f'인물{idx+1}'

            # 탭 프레임 생성
            tab_frame = ttk.Frame(self.character_notebook, padding=5)
            tab_frame.columnconfigure(0, weight=1)
            tab_frame.rowconfigure(0, weight=1)

            # 탭 추가 (인물 이름으로)
            self.character_notebook.add(tab_frame, text=f" {char_name} ")
            self.character_tabs[str(id(tab_frame))] = idx

            # 인물 정보 표시 영역
            self._create_character_view(tab_frame, character)

    def _create_character_view(self, parent_frame, character: dict):
        """인물 정보 뷰 생성 - 2열 레이아웃"""
        # 스크롤 가능한 캔버스
        canvas = tk.Canvas(parent_frame, highlightthickness=0, bg="white")
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)

        # 내용을 담을 프레임
        content_frame = ttk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)

        # 그리드 배치
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 캔버스에 프레임 추가
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")

        # 프레임 크기 변경 시 스크롤 영역 업데이트
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)

        content_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        # 마우스 휠 스크롤
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<MouseWheel>", on_mousewheel)
        content_frame.bind("<MouseWheel>", on_mousewheel)

        # 2열 레이아웃 설정
        content_frame.columnconfigure(0, weight=0, minsize=100)  # 키 열
        content_frame.columnconfigure(1, weight=1)  # 값 열

        # 인물 정보 표시
        row = 0
        priority_keys = ['name', 'age', 'gender', 'role', 'occupation', 'personality', 'appearance', 'background']

        # 우선 키 먼저 표시
        for key in priority_keys:
            if key in character:
                row = self._add_info_row(content_frame, row, key, character[key], canvas)

        # 나머지 키 표시
        for key, value in character.items():
            if key not in priority_keys:
                row = self._add_info_row(content_frame, row, key, value, canvas)

    def _add_info_row(self, parent, row: int, key: str, value, canvas) -> int:
        """정보 행 추가"""
        display_key = self._get_display_key(key)
        formatted_value = self._format_value(value)

        # 키 레이블 (왼쪽)
        key_label = ttk.Label(
            parent,
            text=display_key,
            font=("맑은 고딕", 10, "bold"),
            foreground="#0066cc",
            anchor="e",
            width=12
        )
        key_label.grid(row=row, column=0, sticky=(tk.E, tk.N), padx=(10, 10), pady=8)

        # 값 표시 (오른쪽)
        if '\n' in formatted_value or len(formatted_value) > 80:
            # 여러 줄 텍스트
            line_count = min(formatted_value.count('\n') + 1, 8)
            value_text = tk.Text(
                parent,
                wrap=tk.WORD,
                font=("맑은 고딕", 10),
                height=line_count,
                relief=tk.FLAT,
                bg="#f5f5f5",
                padx=8,
                pady=5
            )
            value_text.insert(1.0, formatted_value)
            value_text.config(state=tk.DISABLED)
            value_text.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=5)

            # 마우스 휠 이벤트 전파
            def on_text_mousewheel(event, c=canvas):
                c.yview_scroll(int(-1 * (event.delta / 120)), "units")
                return "break"
            value_text.bind("<MouseWheel>", on_text_mousewheel)
        else:
            # 한 줄 텍스트
            value_label = ttk.Label(
                parent,
                text=formatted_value,
                font=("맑은 고딕", 10),
                wraplength=500,
                justify=tk.LEFT,
                anchor="w"
            )
            value_label.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=8)

        # 구분선
        separator = ttk.Separator(parent, orient=tk.HORIZONTAL)
        separator.grid(row=row + 1, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=2)

        return row + 2

    def _get_display_key(self, key: str) -> str:
        """키를 한글 표시명으로 변환"""
        key_map = {
            'name': '이름',
            'age': '나이',
            'gender': '성별',
            'role': '역할',
            'occupation': '직업',
            'personality': '성격',
            'appearance': '외모',
            'background': '배경',
            'relationship': '관계',
            'characteristics': '특징',
            'description': '설명',
            'image_generation_prompt': '이미지 프롬프트',
            'image_generation_prompts': '프롬프트 목록',
            'character_info': '인물 정보',
            'versions': '버전 정보'
        }
        return key_map.get(key, key)

    def _format_value(self, value) -> str:
        """값을 읽기 쉽게 포맷팅"""
        if isinstance(value, dict):
            lines = []
            for k, v in value.items():
                if isinstance(v, (dict, list)):
                    lines.append(f"{k}:")
                    lines.append(f"  {json.dumps(v, ensure_ascii=False, indent=2)}")
                else:
                    lines.append(f"{k}: {v}")
            return '\n'.join(lines)
        elif isinstance(value, list):
            if all(isinstance(item, str) for item in value):
                return '\n'.join([f"• {item}" for item in value])
            else:
                lines = []
                for item in value:
                    if isinstance(item, dict):
                        lines.append(json.dumps(item, ensure_ascii=False))
                    else:
                        lines.append(f"• {item}")
                return '\n'.join(lines)
        else:
            return str(value) if value else ""

    def save(self) -> bool:
        """데이터 저장"""
        return True
