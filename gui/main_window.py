"""
메인 윈도우
프로젝트 뷰어/에디터의 메인 GUI 윈도우입니다.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

# 탭들 import
from gui.tabs.synopsis_tab import SynopsisTab
from gui.tabs.characters_tab import CharactersTab
from gui.tabs.chapters_tab import ChaptersTab
from gui.tabs.scripts_tab import ScriptsTab
from gui.tabs.scenes_tab import ScenesTab
from gui.tabs.image_prompts_tab import ImagePromptsTab
from gui.tabs.copy_paste_tab import CopyPasteTab

# 다이얼로그 import
from gui.dialogs.settings_dialog import SettingsDialog


class MainWindow:
    """메인 윈도우 클래스"""

    def __init__(self, root, project_path, config_manager, project_data, file_service, content_generator):
        """
        Args:
            root: Tkinter root
            project_path: 프로젝트 경로
            config_manager: ConfigManager 인스턴스
            project_data: ProjectData 인스턴스
            file_service: FileService 인스턴스
            content_generator: ContentGenerator 인스턴스
        """
        self.root = root
        self.project_path = project_path
        self.config = config_manager
        self.project_data = project_data
        self.file_service = file_service
        self.content_generator = content_generator

        # 윈도우 설정
        self.root.title("프로젝트 뷰어/에디터")
        self._setup_window()

        # 메뉴바 생성
        self._create_menu()

        # 메인 프레임 생성
        self._create_main_frame()

        # 상태바 생성
        self._create_statusbar()

        # 데이터 로드
        self._load_project_data()

        # 탭들 초기화
        self._initialize_tabs()

    def _setup_window(self):
        """윈도우 설정"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.85)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def _create_menu(self):
        """메뉴바 생성"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 파일 메뉴
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="파일", menu=file_menu)
        file_menu.add_command(label="프로젝트 열기...", command=self._open_project)
        file_menu.add_separator()
        file_menu.add_command(label="저장", command=self._save_all, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.root.quit)

        # 설정 메뉴
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="설정", menu=settings_menu)
        settings_menu.add_command(label="LLM 설정...", command=self._open_settings)

        # 단축키
        self.root.bind('<Control-s>', lambda e: self._save_all())

    def _create_main_frame(self):
        """메인 프레임 생성"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # 상단 툴바
        toolbar = ttk.Frame(main_frame)
        toolbar.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        toolbar.columnconfigure(0, weight=1)

        settings_btn = ttk.Button(toolbar, text="⚙ 설정", command=self._open_settings, width=12)
        settings_btn.grid(row=0, column=1, sticky=tk.E)

        # 왼쪽 사이드바 (탭 목록)
        self._create_sidebar(main_frame)

        # 오른쪽 콘텐츠 영역 (노트북)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

    def _create_sidebar(self, parent):
        """왼쪽 사이드바 생성"""
        sidebar = ttk.Frame(parent)
        sidebar.grid(row=1, column=0, sticky=(tk.W, tk.N, tk.S), padx=(0, 10))

        ttk.Label(sidebar, text="탭", font=("맑은 고딕", 12, "bold")).pack(pady=10)

        self.tab_buttons = {}
        self.current_tab = "synopsis"

        # 탭 버튼들
        tab_names = [
            ("synopsis", "시놉시스"),
            ("characters", "인물"),
            ("image_prompts", "이미지 프롬프트"),
            ("chapters", "챕터"),
            ("scripts", "대본"),
            ("scenes", "장면 생성"),
            ("copy_paste", "복사/붙여넣기")
        ]

        for tab_id, tab_label in tab_names:
            btn = ttk.Button(
                sidebar,
                text=tab_label,
                width=18,
                command=lambda tid=tab_id: self._switch_tab(tid)
            )
            btn.pack(pady=5, fill=tk.X, padx=5)
            self.tab_buttons[tab_id] = btn

        # 초기 탭 표시
        self.tab_buttons[self.current_tab].state(['pressed'])

        # 저장 버튼
        ttk.Separator(sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15, padx=5)
        save_btn = ttk.Button(
            sidebar,
            text="저장 (Ctrl+S)",
            width=18,
            command=self._save_all
        )
        save_btn.pack(pady=5, fill=tk.X, padx=5)

    def _create_statusbar(self):
        """상태바 생성"""
        self.status_var = tk.StringVar(value="준비")
        statusbar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        statusbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

    def _initialize_tabs(self):
        """탭들 초기화"""
        # 탭 인스턴스 생성
        self.tabs = {
            'synopsis': SynopsisTab(self.notebook, self.project_data, self.file_service, self.content_generator),
            'characters': CharactersTab(self.notebook, self.project_data, self.file_service, self.content_generator),
            'chapters': ChaptersTab(self.notebook, self.project_data, self.file_service, self.content_generator),
            'scripts': ScriptsTab(self.notebook, self.project_data, self.file_service, self.content_generator),
            'scenes': ScenesTab(self.notebook, self.project_data, self.file_service, self.content_generator),
            'image_prompts': ImagePromptsTab(self.notebook, self.project_data, self.file_service, self.content_generator),
            'copy_paste': CopyPasteTab(self.notebook, self.project_data, self.file_service, self.content_generator)
        }

        # 모든 탭 업데이트
        for tab in self.tabs.values():
            tab.update_display()

    def _switch_tab(self, tab_id):
        """탭 전환"""
        # 이전 탭 버튼 상태 해제
        if self.current_tab in self.tab_buttons:
            self.tab_buttons[self.current_tab].state(['!pressed'])

        self.current_tab = tab_id
        self.tab_buttons[tab_id].state(['pressed'])

        # 노트북 탭 전환
        tab_index = list(self.tabs.keys()).index(tab_id)
        self.notebook.select(tab_index)

        # 탭 업데이트
        self.tabs[tab_id].update_display()

    def _load_project_data(self):
        """프로젝트 데이터 로드"""
        try:
            data = self.file_service.load_all_data()
            self.project_data.data = data
            self.status_var.set(
                f"데이터 로드 완료: {len(data.get('characters', []))}명, {len(data.get('chapters', []))}개 챕터"
            )
        except Exception as e:
            messagebox.showerror("오류", f"데이터 로드 실패: {e}")
            self.status_var.set(f"오류: {e}")

    def _save_all(self):
        """모든 변경사항 저장"""
        try:
            success_count = 0
            fail_count = 0

            # 각 탭의 저장 메서드 호출
            for tab_id, tab in self.tabs.items():
                try:
                    if tab.save():
                        success_count += 1
                except Exception as e:
                    print(f"{tab_id} 탭 저장 오류: {e}")
                    fail_count += 1

            self.project_data.clear_unsaved()
            self.status_var.set(f"저장 완료! (성공: {success_count}, 실패: {fail_count})")
            messagebox.showinfo("저장", "모든 변경사항이 저장되었습니다.")
        except Exception as e:
            messagebox.showerror("저장 오류", f"저장 중 오류가 발생했습니다: {e}")
            self.status_var.set(f"저장 오류: {e}")

    def _open_project(self):
        """프로젝트 열기"""
        project_dir = filedialog.askdirectory(title="프로젝트 폴더 선택")
        if project_dir:
            self.project_path = Path(project_dir)
            self.file_service.project_path = self.project_path
            self.project_data.project_path = self.project_path
            self._load_project_data()

            # 모든 탭 업데이트
            for tab in self.tabs.values():
                tab.update_display()

    def _open_settings(self):
        """설정 창 열기"""
        SettingsDialog(self.root, self.config, self.project_data, self.file_service)
