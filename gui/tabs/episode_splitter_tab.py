"""
에피소드 분리 탭
MD 파일을 ACT/에피소드별로 분리하는 GUI
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import TYPE_CHECKING

from gui.tabs.base_tab import BaseTab
from services.episode_splitter_service import EpisodeSplitterService

if TYPE_CHECKING:
    from models.project_data import ProjectData
    from services.file_service import FileService
    from services.content_generator import ContentGenerator


class EpisodeSplitterTab(BaseTab):
    """에피소드 분리 탭"""

    def __init__(self, parent, project_data, file_service, content_generator):
        self.splitter_service = EpisodeSplitterService()
        self.selected_file = None
        self.episodes = []
        super().__init__(parent, project_data, file_service, content_generator)

    def get_tab_name(self) -> str:
        return "에피소드 분리"

    def create_ui(self):
        """UI 생성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 상단: 파일 선택
        file_frame = ttk.LabelFrame(main_frame, text="MD 파일 선택", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))

        # 파일 경로 입력
        path_frame = ttk.Frame(file_frame)
        path_frame.pack(fill=tk.X)

        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(path_frame, textvariable=self.file_path_var, width=80)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        browse_btn = ttk.Button(path_frame, text="찾아보기...", command=self._browse_file)
        browse_btn.pack(side=tk.LEFT, padx=(0, 5))

        analyze_btn = ttk.Button(path_frame, text="분석", command=self._analyze_file)
        analyze_btn.pack(side=tk.LEFT)

        # 중단: 에피소드 미리보기
        preview_frame = ttk.LabelFrame(main_frame, text="에피소드 미리보기", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 트리뷰
        columns = ("번호", "제목", "ACT", "글자수")
        self.tree = ttk.Treeview(preview_frame, columns=columns, show="headings", height=15)

        self.tree.heading("번호", text="번호")
        self.tree.heading("제목", text="제목")
        self.tree.heading("ACT", text="ACT")
        self.tree.heading("글자수", text="글자수")

        self.tree.column("번호", width=60, anchor=tk.CENTER)
        self.tree.column("제목", width=300)
        self.tree.column("ACT", width=200)
        self.tree.column("글자수", width=80, anchor=tk.CENTER)

        # 스크롤바
        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 하단: 출력 설정 및 실행
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X)

        # 출력 디렉토리
        output_frame = ttk.LabelFrame(bottom_frame, text="출력 설정", padding="10")
        output_frame.pack(fill=tk.X, pady=(0, 10))

        output_path_frame = ttk.Frame(output_frame)
        output_path_frame.pack(fill=tk.X)

        ttk.Label(output_path_frame, text="출력 폴더:").pack(side=tk.LEFT, padx=(0, 5))

        self.output_path_var = tk.StringVar()
        output_entry = ttk.Entry(output_path_frame, textvariable=self.output_path_var, width=70)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        output_browse_btn = ttk.Button(output_path_frame, text="변경...", command=self._browse_output)
        output_browse_btn.pack(side=tk.LEFT)

        # 실행 버튼
        button_frame = ttk.Frame(bottom_frame)
        button_frame.pack(fill=tk.X)

        self.split_btn = ttk.Button(
            button_frame,
            text="에피소드 분리 실행",
            command=self._execute_split,
            state=tk.DISABLED
        )
        self.split_btn.pack(side=tk.RIGHT, padx=5)

        self.open_folder_btn = ttk.Button(
            button_frame,
            text="출력 폴더 열기",
            command=self._open_output_folder,
            state=tk.DISABLED
        )
        self.open_folder_btn.pack(side=tk.RIGHT, padx=5)

        # 상태 표시
        self.status_var = tk.StringVar(value="MD 파일을 선택하세요.")
        status_label = ttk.Label(button_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT, padx=5)

    def _browse_file(self):
        """MD 파일 선택"""
        # 프로젝트 폴더에서 시작
        initial_dir = self.project_data.project_path if self.project_data.project_path else Path.cwd()

        file_path = filedialog.askopenfilename(
            title="대본 MD 파일 선택",
            initialdir=initial_dir,
            filetypes=[("Markdown 파일", "*.md"), ("모든 파일", "*.*")]
        )

        if file_path:
            self.file_path_var.set(file_path)
            self._analyze_file()

    def _browse_output(self):
        """출력 폴더 선택"""
        folder = filedialog.askdirectory(
            title="출력 폴더 선택",
            initialdir=self.output_path_var.get() or Path.cwd()
        )

        if folder:
            self.output_path_var.set(folder)

    def _analyze_file(self):
        """파일 분석"""
        file_path = self.file_path_var.get()

        if not file_path:
            messagebox.showwarning("경고", "파일을 선택하세요.")
            return

        if not Path(file_path).exists():
            messagebox.showerror("에러", f"파일을 찾을 수 없습니다:\n{file_path}")
            return

        try:
            # 에피소드 목록 가져오기
            self.episodes = self.splitter_service.get_episode_list(file_path)

            # 트리뷰 초기화
            for item in self.tree.get_children():
                self.tree.delete(item)

            # 에피소드 추가
            for ep in self.episodes:
                self.tree.insert("", tk.END, values=(
                    f"EP{ep['number']:02d}",
                    ep['title'],
                    ep['act'],
                    f"{ep['content_length']:,}자"
                ))

            # 기본 출력 경로 설정
            md_path = Path(file_path)
            default_output = md_path.parent / f"{md_path.stem}_episodes"
            self.output_path_var.set(str(default_output))

            # 상태 업데이트
            self.status_var.set(f"{len(self.episodes)}개 에피소드 발견")
            self.split_btn.config(state=tk.NORMAL)
            self.selected_file = file_path

        except Exception as e:
            messagebox.showerror("에러", f"파일 분석 실패:\n{str(e)}")
            self.status_var.set("분석 실패")
            self.split_btn.config(state=tk.DISABLED)

    def _execute_split(self):
        """에피소드 분리 실행"""
        if not self.selected_file:
            messagebox.showwarning("경고", "먼저 파일을 분석하세요.")
            return

        output_dir = self.output_path_var.get()

        try:
            # 분리 실행
            result = self.splitter_service.split_to_files(self.selected_file, output_dir)

            # 결과 메시지
            msg = f"에피소드 분리 완료!\n\n"
            msg += f"출력 폴더: {result['output_dir']}\n"
            msg += f"총 에피소드: {result['episodes_count']}개\n\n"

            for act, files in result['files'].items():
                msg += f"{act}: {len(files)}개 파일\n"

            messagebox.showinfo("완료", msg)

            # 출력 폴더 열기 버튼 활성화
            self.output_path_var.set(result['output_dir'])
            self.open_folder_btn.config(state=tk.NORMAL)
            self.status_var.set(f"분리 완료: {result['episodes_count']}개 파일 생성")

        except Exception as e:
            messagebox.showerror("에러", f"분리 실패:\n{str(e)}")

    def _open_output_folder(self):
        """출력 폴더 열기"""
        output_dir = self.output_path_var.get()

        if output_dir and Path(output_dir).exists():
            import os
            os.startfile(output_dir)
        else:
            messagebox.showwarning("경고", "출력 폴더가 존재하지 않습니다.")

    def update_display(self):
        """화면 업데이트"""
        pass
