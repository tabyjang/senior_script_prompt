"""
시놉시스 탭
프로젝트의 전체 대본 또는 시놉시스 MD 파일을 마크다운 형식으로 보여줍니다.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from pathlib import Path
import re
from typing import Optional
from .base_tab import BaseTab


class SynopsisInputTab(BaseTab):
    """시놉시스 탭 클래스 - MD 파일 뷰어"""

    def get_tab_name(self) -> str:
        return "시놉시스"

    def create_ui(self):
        """UI 생성"""
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)

        # 상단 버튼 영역
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=0, column=0, pady=(0, 5), sticky=(tk.W, tk.E))

        # MD 파일 열기 버튼
        open_btn = ttk.Button(
            button_frame,
            text="MD 파일 열기",
            command=self._open_md_file,
            width=15
        )
        open_btn.pack(side=tk.LEFT, padx=5)

        # 새로고침 버튼
        refresh_btn = ttk.Button(
            button_frame,
            text="새로고침",
            command=self.update_display,
            width=10
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)

        # 현재 파일 경로 표시
        self.file_path_var = tk.StringVar(value="")
        file_path_label = ttk.Label(
            button_frame,
            textvariable=self.file_path_var,
            font=("맑은 고딕", 9),
            foreground="gray"
        )
        file_path_label.pack(side=tk.LEFT, padx=20)

        # 메인 뷰어 영역
        viewer_frame = ttk.LabelFrame(self.frame, text="시놉시스 / 전체 대본", padding=5)
        viewer_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        viewer_frame.columnconfigure(0, weight=1)
        viewer_frame.rowconfigure(0, weight=1)

        # 마크다운 뷰어 (스크롤 가능한 텍스트)
        self.viewer = scrolledtext.ScrolledText(
            viewer_frame,
            width=120,
            height=40,
            wrap=tk.WORD,
            font=("맑은 고딕", 10),
            padx=10,
            pady=10
        )
        self.viewer.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 마크다운 스타일 태그 설정
        self._setup_markdown_tags()

        # 현재 로드된 파일 경로 저장
        self.current_md_path = None

    def _setup_markdown_tags(self):
        """마크다운 스타일 태그 설정"""
        # 헤더 스타일
        self.viewer.tag_configure("h1", font=("맑은 고딕", 12), foreground="#0066cc")
        self.viewer.tag_configure("h2", font=("맑은 고딕", 11), foreground="#336699")
        self.viewer.tag_configure("h3", font=("맑은 고딕", 10), foreground="#555555")
        self.viewer.tag_configure("h4", font=("맑은 고딕", 10), foreground="#666666")

        # 볼드 스타일
        self.viewer.tag_configure("bold", font=("맑은 고딕", 10, "bold"))

        # 인용문 스타일
        self.viewer.tag_configure("quote", foreground="#555555", lmargin1=20, lmargin2=20)

        # 리스트 스타일
        self.viewer.tag_configure("list_item", lmargin1=15, lmargin2=25)

        # 구분선 스타일
        self.viewer.tag_configure("hr", foreground="#cccccc", justify="center")

        # 대화문 스타일
        self.viewer.tag_configure("dialogue", foreground="#0066cc")

        # 일반 텍스트 스타일
        self.viewer.tag_configure("normal", font=("맑은 고딕", 10))

        # 테이블 스타일
        self.viewer.tag_configure("table_header", font=("맑은 고딕", 10, "bold"), background="#f0f0f0")
        self.viewer.tag_configure("table_cell", font=("맑은 고딕", 10))
        self.viewer.tag_configure("table_border", foreground="#cccccc")

        # 에피소드 제목 스타일
        self.viewer.tag_configure("episode_title", font=("맑은 고딕", 11), foreground="#0055aa")

    def update_display(self):
        """화면 업데이트 - 프로젝트 폴더에서 MD 파일 자동 로드"""
        self.viewer.config(state=tk.NORMAL)
        self.viewer.delete(1.0, tk.END)

        md_content = None
        md_path = None

        try:
            md_path = self.file_service.find_project_md_file()

            if md_path and md_path.exists():
                with open(md_path, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                self.current_md_path = md_path
                self.file_path_var.set(f"{md_path.name}")

        except Exception as e:
            print(f"[시놉시스 탭] MD 파일 로드 오류: {e}")

        if md_content:
            self._render_markdown(md_content)
        else:
            self.viewer.insert(tk.END, "MD 파일을 찾을 수 없습니다.\n\n", "normal")
            self.viewer.insert(tk.END, "'MD 파일 열기' 버튼으로 파일을 선택하세요.", "normal")
            self.file_path_var.set("")

        self.viewer.config(state=tk.DISABLED)

    def _open_md_file(self):
        """MD 파일 직접 열기"""
        initial_dir = None
        try:
            project_path = Path(self.file_service.project_path)
            if project_path.exists():
                initial_dir = str(project_path)
        except:
            pass

        file_path = filedialog.askopenfilename(
            title="MD 파일 선택",
            filetypes=[
                ("Markdown 파일", "*.md"),
                ("모든 파일", "*.*")
            ],
            initialdir=initial_dir
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    md_content = f.read()

                self.current_md_path = Path(file_path)
                self.file_path_var.set(f"{self.current_md_path.name}")

                self.viewer.config(state=tk.NORMAL)
                self.viewer.delete(1.0, tk.END)
                self._render_markdown(md_content)
                self.viewer.config(state=tk.DISABLED)

            except Exception as e:
                messagebox.showerror("오류", f"파일을 열 수 없습니다:\n{e}")

    def _render_markdown(self, content: str):
        """마크다운 콘텐츠를 스타일 적용하여 렌더링"""
        # 이스케이프 문자 정리
        content = content.replace(r'\.', '.')
        content = content.replace(r'\(', '(')
        content = content.replace(r'\)', ')')
        content = content.replace(r'\-', '-')
        content = content.replace(r'\[', '[')
        content = content.replace(r'\]', ']')
        content = content.replace(r'\!', '!')

        lines = content.split('\n')
        i = 0
        last_was_blank = False  # 연속 빈 줄 방지

        while i < len(lines):
            line = lines[i]

            # 빈 줄 처리 (연속 빈 줄 방지)
            if not line.strip():
                if not last_was_blank:
                    self.viewer.insert(tk.END, "\n")
                    last_was_blank = True
                i += 1
                continue

            last_was_blank = False

            # 마크다운 테이블 처리 (| 로 시작하는 줄)
            if line.strip().startswith('|'):
                table_lines = []
                while i < len(lines) and lines[i].strip().startswith('|'):
                    table_lines.append(lines[i])
                    i += 1
                self._render_table(table_lines)
                continue

            # __text__ 형식이 여러 개 있으면 테이블 헤더로 처리
            bold_items = re.findall(r'__([^_]+)__', line)
            if len(bold_items) >= 3:
                # 테이블 헤더로 처리
                header_text = "  |  ".join(bold_items)
                self.viewer.insert(tk.END, header_text + "\n", "table_header")
                i += 1
                continue

            # # 헤더 처리
            header_match = re.match(r'^(#{1,4})\s+(.+)$', line)
            if header_match:
                level = len(header_match.group(1))
                header_text = self._clean_text(header_match.group(2))
                self.viewer.insert(tk.END, header_text + "\n", f"h{level}")
                i += 1
                continue

            # __제목__ 형식 (한 줄에 하나만 있을 때)
            single_bold = re.match(r'^__([^_]+)__\s*$', line.strip())
            if single_bold:
                title = single_bold.group(1)
                self.viewer.insert(tk.END, title + "\n", "episode_title")
                i += 1
                continue

            # 구분선 처리
            if re.match(r'^[-_*]{3,}\s*$', line.strip()):
                self.viewer.insert(tk.END, "─" * 50 + "\n", "hr")
                i += 1
                continue

            # 인용문 처리
            if line.strip().startswith('>'):
                quote_text = self._clean_text(line.strip()[1:].strip())
                self.viewer.insert(tk.END, f"  {quote_text}\n", "quote")
                i += 1
                continue

            # 리스트 항목 처리
            list_match = re.match(r'^(\s*)([-*•]|\d+\.)\s+(.+)$', line)
            if list_match:
                bullet = list_match.group(2)
                text = self._clean_text(list_match.group(3))
                if bullet in ['-', '*', '•']:
                    self.viewer.insert(tk.END, f"  • {text}\n", "list_item")
                else:
                    self.viewer.insert(tk.END, f"  {bullet} {text}\n", "list_item")
                i += 1
                continue

            # 대화문 처리
            if line.strip().startswith('"') or line.strip().startswith('"'):
                text = self._clean_text(line)
                self.viewer.insert(tk.END, f"{text}\n", "dialogue")
                i += 1
                continue

            # 일반 텍스트 처리
            text = self._clean_text(line)
            self.viewer.insert(tk.END, text + "\n", "normal")
            i += 1

    def _render_table(self, table_lines: list):
        """마크다운 테이블 렌더링"""
        if not table_lines:
            return

        for idx, line in enumerate(table_lines):
            # | 구분자 제거하고 셀 추출
            cells = [c.strip() for c in line.split('|') if c.strip()]

            # 구분선 (---) 스킵
            if cells and all(re.match(r'^[-:]+$', c) for c in cells):
                continue

            # 셀 내용 정리
            cleaned_cells = [self._clean_text(c) for c in cells]
            row_text = "  |  ".join(cleaned_cells)

            if idx == 0:
                # 첫 줄은 헤더
                self.viewer.insert(tk.END, row_text + "\n", "table_header")
            else:
                self.viewer.insert(tk.END, row_text + "\n", "table_cell")

    def _clean_text(self, text: str) -> str:
        """마크다운 서식 제거"""
        # 이스케이프 문자 정리
        text = text.replace(r'\.', '.')
        text = text.replace(r'\(', '(')
        text = text.replace(r'\)', ')')
        text = text.replace(r'\-', '-')

        # __text__ → text
        text = re.sub(r'__([^_]+)__', r'\1', text)
        # **text** → text
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        # *text* → text
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        # _text_ → text
        text = re.sub(r'_([^_]+)_', r'\1', text)

        return text.strip()

    def save(self) -> bool:
        """데이터 저장 (뷰어 전용이므로 항상 True 반환)"""
        return True
