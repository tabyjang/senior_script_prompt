"""
Word 변환 탭
Word 파일을 드래그 앤 드롭으로 Markdown 파일로 변환합니다.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from .base_tab import BaseTab

try:
    from tkinterdnd2 import DND_FILES
    HAS_DND = True
except ImportError:
    HAS_DND = False

from utils.word_converter import convert_word_to_markdown


class WordConverterTab(BaseTab):
    """Word 변환 탭 클래스"""

    def __init__(self, parent, project_data, file_service, content_generator):
        """초기화"""
        self.drop_area = None
        self.status_label = None
        self.history_text = None
        super().__init__(parent, project_data, file_service, content_generator)

    def get_tab_name(self) -> str:
        return "Word 변환"

    def create_ui(self):
        """UI 생성"""
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)

        # 상단 안내
        info_frame = ttk.Frame(self.frame, padding="10")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=10)

        ttk.Label(
            info_frame,
            text="Word → Markdown 변환",
            font=("맑은 고딕", 14, "bold")
        ).pack(anchor=tk.W)

        ttk.Label(
            info_frame,
            text="Word 파일(.docx)을 아래 영역에 드래그 앤 드롭하면 Markdown으로 변환됩니다.",
            font=("맑은 고딕", 10)
        ).pack(anchor=tk.W, pady=(5, 0))

        ttk.Label(
            info_frame,
            text="저장 위치: prompts/파일명/파일명.md",
            font=("맑은 고딕", 9),
            foreground="gray"
        ).pack(anchor=tk.W, pady=(2, 0))

        # 드롭 영역
        drop_frame = ttk.LabelFrame(self.frame, text="파일 드롭 영역", padding=20)
        drop_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        drop_frame.columnconfigure(0, weight=1)
        drop_frame.rowconfigure(0, weight=1)

        # 드롭 영역 (Canvas로 만들어 시각적 효과)
        self.drop_area = tk.Canvas(
            drop_frame,
            bg="#f0f0f0",
            highlightthickness=2,
            highlightbackground="#cccccc",
            height=200
        )
        self.drop_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 드롭 영역 텍스트
        self._draw_drop_text()

        # 드래그 앤 드롭 설정
        if HAS_DND:
            self._setup_dnd()
        else:
            self.drop_area.create_text(
                self.drop_area.winfo_reqwidth() // 2,
                self.drop_area.winfo_reqheight() // 2 + 40,
                text="(드래그 앤 드롭이 지원되지 않습니다. 아래 버튼을 사용하세요)",
                fill="red",
                font=("맑은 고딕", 9)
            )

        # 파일 선택 버튼
        btn_frame = ttk.Frame(drop_frame)
        btn_frame.grid(row=1, column=0, pady=(10, 0))

        select_btn = ttk.Button(
            btn_frame,
            text="파일 선택...",
            command=self._select_file,
            width=15
        )
        select_btn.pack(side=tk.LEFT, padx=5)

        # 상태 레이블
        self.status_label = ttk.Label(
            drop_frame,
            text="",
            font=("맑은 고딕", 10)
        )
        self.status_label.grid(row=2, column=0, pady=(10, 0))

        # 변환 기록
        history_frame = ttk.LabelFrame(self.frame, text="변환 기록", padding=10)
        history_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=10, pady=(0, 10))
        history_frame.columnconfigure(0, weight=1)

        self.history_text = tk.Text(
            history_frame,
            height=8,
            wrap=tk.WORD,
            font=("Consolas", 9),
            state=tk.DISABLED
        )
        self.history_text.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # 스크롤바
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.history_text.configure(yscrollcommand=scrollbar.set)

    def _draw_drop_text(self):
        """드롭 영역 텍스트 그리기"""
        self.drop_area.delete("all")

        # 캔버스 크기 가져오기
        self.drop_area.update_idletasks()
        width = self.drop_area.winfo_width()
        height = self.drop_area.winfo_height()

        if width < 10:
            width = 400
        if height < 10:
            height = 200

        # 아이콘 텍스트
        self.drop_area.create_text(
            width // 2,
            height // 2 - 20,
            text="📄",
            font=("Segoe UI Emoji", 40)
        )

        # 안내 텍스트
        self.drop_area.create_text(
            width // 2,
            height // 2 + 40,
            text="Word 파일(.docx)을 여기에 드래그 앤 드롭",
            font=("맑은 고딕", 12),
            fill="#666666"
        )

    def _setup_dnd(self):
        """드래그 앤 드롭 설정"""
        try:
            self.drop_area.drop_target_register(DND_FILES)
            self.drop_area.dnd_bind('<<Drop>>', self._on_drop)
            self.drop_area.dnd_bind('<<DragEnter>>', self._on_drag_enter)
            self.drop_area.dnd_bind('<<DragLeave>>', self._on_drag_leave)
        except Exception as e:
            print(f"[Word 변환] DnD 설정 오류: {e}")

    def _on_drag_enter(self, event):
        """드래그 진입 시"""
        self.drop_area.configure(highlightbackground="#4CAF50", bg="#e8f5e9")

    def _on_drag_leave(self, event):
        """드래그 이탈 시"""
        self.drop_area.configure(highlightbackground="#cccccc", bg="#f0f0f0")

    def _on_drop(self, event):
        """파일 드롭 시"""
        self.drop_area.configure(highlightbackground="#cccccc", bg="#f0f0f0")

        # 파일 경로 파싱
        files = self._parse_drop_data(event.data)

        for file_path in files:
            if file_path.lower().endswith('.docx'):
                self._convert_file(file_path)
            else:
                self._add_history(f"지원하지 않는 파일 형식: {Path(file_path).name}")

    def _parse_drop_data(self, data: str) -> list:
        """드롭 데이터에서 파일 경로 추출"""
        files = []

        # Windows에서는 중괄호로 감싸진 경로가 올 수 있음
        if data.startswith('{') and data.endswith('}'):
            data = data[1:-1]

        # 공백이 포함된 경로 처리
        if '{' in data:
            import re
            # {path with spaces} 형식 처리
            pattern = r'\{([^}]+)\}|(\S+)'
            matches = re.findall(pattern, data)
            for match in matches:
                path = match[0] if match[0] else match[1]
                if path:
                    files.append(path)
        else:
            # 단순 공백 분리
            files = data.split()

        return files

    def _select_file(self):
        """파일 선택 대화상자"""
        file_path = filedialog.askopenfilename(
            title="Word 파일 선택",
            filetypes=[
                ("Word 문서", "*.docx"),
                ("모든 파일", "*.*")
            ]
        )

        if file_path:
            self._convert_file(file_path)

    def _convert_file(self, file_path: str):
        """파일 변환 실행"""
        word_file = Path(file_path)
        file_name = word_file.stem  # 확장자 제외한 이름

        # 출력 경로 결정: editors_app/prompts/파일명/파일명.md
        # editors_app 폴더 기준으로 저장
        editors_app_path = Path(__file__).resolve().parent.parent.parent

        # prompts 폴더 경로
        prompts_folder = editors_app_path / "prompts"
        output_folder = prompts_folder / file_name
        output_file = output_folder / f"{file_name}.md"

        # 폴더 생성
        try:
            output_folder.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self._set_status(f"폴더 생성 실패: {e}", error=True)
            return

        # 변환 실행
        self._set_status(f"변환 중: {word_file.name}...")

        success, message, output_path = convert_word_to_markdown(
            str(word_file),
            str(output_file)
        )

        if success:
            self._set_status(f"변환 완료: {file_name}.md")
            self._add_history(f"[성공] {word_file.name}")
            self._add_history(f"  → {output_file}")
        else:
            self._set_status(f"변환 실패", error=True)
            self._add_history(f"[실패] {word_file.name}: {message}")

    def _set_status(self, text: str, error: bool = False):
        """상태 레이블 업데이트"""
        self.status_label.configure(
            text=text,
            foreground="red" if error else "green"
        )

    def _add_history(self, text: str):
        """변환 기록 추가"""
        self.history_text.configure(state=tk.NORMAL)
        self.history_text.insert(tk.END, text + "\n")
        self.history_text.see(tk.END)
        self.history_text.configure(state=tk.DISABLED)

    def update_display(self):
        """화면 업데이트"""
        # 캔버스 크기에 맞게 텍스트 다시 그리기
        self.frame.after(100, self._draw_drop_text)

    def save(self) -> bool:
        """저장 (이 탭은 저장 불필요)"""
        return True
