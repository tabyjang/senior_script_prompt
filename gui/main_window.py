"""
메인 윈도우
프로젝트 뷰어/에디터의 메인 GUI 윈도우입니다.
prompts 폴더 기반 프로젝트 선택 시스템
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

# 탭들 import
from gui.tabs.synopsis_input_tab import SynopsisInputTab
from gui.tabs.image_generation_tab import ImageGenerationTab
from gui.tabs.chapter_details_input_tab import ChapterDetailsInputTab
from gui.tabs.scripts_tab import ScriptsTab
from gui.tabs.image_prompts_input_tab import ImagePromptsInputTab
from gui.tabs.comfyui_tab import ComfyUITab
from gui.tabs.word_converter_tab import WordConverterTab
from gui.tabs.tts_tab import TTSTab
from gui.tabs.episode_splitter_tab import EpisodeSplitterTab

# 다이얼로그 import
from gui.dialogs.settings_dialog import SettingsDialog

# 유틸리티 import
from utils.word_converter import convert_word_to_markdown


class MainWindow:
    """메인 윈도우 클래스"""

    def __init__(self, root, project_path, config_manager, project_data, file_service, content_generator):
        """
        Args:
            root: Tkinter root
            project_path: 프로젝트 경로 (prompts 폴더)
            config_manager: ConfigManager 인스턴스
            project_data: ProjectData 인스턴스
            file_service: FileService 인스턴스
            content_generator: ContentGenerator 인스턴스
        """
        self.root = root
        self.prompts_path = self._find_prompts_folder(project_path)
        self.project_path = None  # 선택된 프로젝트 경로
        self.config = config_manager
        self.project_data = project_data
        self.file_service = file_service
        self.content_generator = content_generator

        # 프로젝트 목록
        self.project_list = []
        self.project_var = None
        self.project_combo = None

        # 윈도우 설정
        self.root.title("시니어 콘텐츠 에디터")
        self._setup_window()

        # 메뉴바 생성
        self._create_menu()

        # 메인 프레임 생성
        self._create_main_frame()

        # 상태바 생성
        self._create_statusbar()

        # 프로젝트 목록 로드
        self._load_project_list()

        # 탭들 초기화
        self._initialize_tabs()

        # 마지막 프로젝트 자동 선택
        self._select_last_project()

    def _find_prompts_folder(self, project_path: Path) -> Path:
        """prompts 폴더 찾기"""
        if project_path is None:
            # 기본 경로 시도
            default_paths = [
                Path(__file__).parent.parent / "prompts",
                Path.cwd() / "prompts",
            ]
            for p in default_paths:
                if p.exists():
                    return p
            return Path(__file__).parent.parent / "prompts"

        # project_path가 prompts 폴더인 경우
        if project_path.name == "prompts" and project_path.exists():
            return project_path

        # project_path 내에 prompts 폴더가 있는 경우
        prompts_in_path = project_path / "prompts"
        if prompts_in_path.exists():
            return prompts_in_path

        # project_path의 상위 폴더에서 prompts 찾기
        parent = project_path.parent
        for _ in range(3):  # 최대 3단계 상위까지
            prompts_in_parent = parent / "prompts"
            if prompts_in_parent.exists():
                return prompts_in_parent
            parent = parent.parent

        # 찾지 못하면 기본값
        return Path(__file__).parent.parent / "prompts"

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
        file_menu.add_command(label="새로고침", command=self._refresh_project_list, accelerator="F5")
        file_menu.add_separator()
        file_menu.add_command(label="저장", command=self._save_all, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.root.quit)

        # 도구 메뉴
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="도구", menu=tools_menu)
        tools_menu.add_command(label="Word → MD 변환...", command=self._convert_word_to_md)

        # 설정 메뉴
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="설정", menu=settings_menu)
        settings_menu.add_command(label="LLM 설정...", command=self._open_settings)

        # 단축키
        self.root.bind('<Control-s>', lambda e: self._save_all())
        self.root.bind('<F5>', lambda e: self._refresh_project_list())

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
        toolbar.columnconfigure(1, weight=1)

        # 프로젝트 선택 영역
        project_frame = ttk.Frame(toolbar)
        project_frame.grid(row=0, column=0, sticky=tk.W)

        ttk.Label(
            project_frame,
            text="프로젝트:",
            font=("맑은 고딕", 11, "bold")
        ).pack(side=tk.LEFT, padx=(5, 10))

        # 프로젝트 드롭다운
        self.project_var = tk.StringVar()
        self.project_combo = ttk.Combobox(
            project_frame,
            textvariable=self.project_var,
            width=50,
            state='readonly',
            font=("맑은 고딕", 10)
        )
        self.project_combo.pack(side=tk.LEFT, padx=5)
        self.project_combo.bind('<<ComboboxSelected>>', lambda e: self._on_project_selected())

        # 새로고침 버튼
        refresh_btn = ttk.Button(
            project_frame,
            text="🔄",
            command=self._refresh_project_list,
            width=3
        )
        refresh_btn.pack(side=tk.LEFT, padx=2)

        # 버튼 프레임 (오른쪽 정렬)
        button_frame = ttk.Frame(toolbar)
        button_frame.grid(row=0, column=1, sticky=tk.E)

        # 설정 버튼
        settings_btn = ttk.Button(button_frame, text="⚙ 설정", command=self._open_settings, width=12)
        settings_btn.pack(side=tk.LEFT)

        # 왼쪽 사이드바 (탭 목록)
        self._create_sidebar(main_frame)

        # 오른쪽 콘텐츠 영역 (노트북)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 메인 Notebook 탭 헤더만 숨기기 (왼쪽 사이드바로 탭 전환)
        style = ttk.Style()
        # 메인 탭용 커스텀 스타일 (헤더 숨김)
        style.layout("Hidden.TNotebook.Tab", [])
        self.notebook.configure(style="Hidden.TNotebook")

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
            ("chapters", "챕터"),
            ("scripts", "대본"),
            ("scene_prompts", "장면 프롬프트"),
            ("comfyui", "ComfyUI 생성"),
            ("tts", "TTS 음성"),
            ("episode_splitter", "에피소드 분리"),
            ("word_converter", "Word 변환")
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

    def _create_statusbar(self):
        """상태바 생성"""
        self.status_var = tk.StringVar(value="프로젝트를 선택해주세요")
        statusbar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        statusbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

    def _load_project_list(self):
        """프로젝트 목록 로드 (prompts 폴더의 하위 폴더들)"""
        self.project_list = []

        if not self.prompts_path.exists():
            print(f"[경고] prompts 폴더를 찾을 수 없습니다: {self.prompts_path}")
            return

        try:
            # prompts 폴더 내의 하위 폴더들을 프로젝트로 인식
            for item in sorted(self.prompts_path.iterdir()):
                if item.is_dir() and not item.name.startswith('.') and not item.name.startswith('_'):
                    # workflows 같은 특수 폴더 제외
                    if item.name.lower() not in ['workflows', 'templates', 'temp', 'output']:
                        self.project_list.append(item.name)

            # 콤보박스 업데이트
            if self.project_combo:
                self.project_combo['values'] = self.project_list

        except Exception as e:
            print(f"프로젝트 목록 로드 오류: {e}")

    def _refresh_project_list(self):
        """프로젝트 목록 새로고침"""
        current_selection = self.project_var.get() if self.project_var else None
        self._load_project_list()

        if current_selection and current_selection in self.project_list:
            self.project_var.set(current_selection)

        self.status_var.set(f"프로젝트 목록 새로고침 완료 ({len(self.project_list)}개)")

    def _select_last_project(self):
        """마지막으로 사용한 프로젝트 자동 선택"""
        last_path = self.config.get_last_project_path()

        if last_path:
            last_project_name = Path(last_path).name
            if last_project_name in self.project_list:
                self.project_var.set(last_project_name)
                self._on_project_selected()
                return

        # 마지막 프로젝트가 없으면 첫 번째 프로젝트 선택
        if self.project_list:
            self.project_var.set(self.project_list[0])
            self._on_project_selected()

    def _on_project_selected(self):
        """프로젝트 선택 시 호출"""
        selected_project = self.project_var.get()
        if not selected_project:
            return

        # 프로젝트 경로 설정
        self.project_path = self.prompts_path / selected_project

        # 파일 서비스 경로 업데이트
        self.file_service.project_path = self.project_path
        self.project_data.project_path = self.project_path

        # 설정에 저장
        self.config.set_last_project_path(str(self.project_path))

        # 프로젝트 데이터 로드
        self._load_project_data()

        # 모든 탭에 dirty 플래그 설정 (다음 탭 전환 시 업데이트 필요)
        if hasattr(self, 'tabs'):
            for tab in self.tabs.values():
                tab._needs_update = True

            # 현재 탭만 즉시 업데이트
            if self.current_tab in self.tabs:
                try:
                    self.tabs[self.current_tab].update_display()
                    self.tabs[self.current_tab]._needs_update = False
                except Exception as e:
                    print(f"탭 업데이트 오류: {e}")

        # 상태바 업데이트
        self.status_var.set(f"프로젝트: {selected_project} | 경로: {self.project_path}")

        # 윈도우 제목 업데이트
        self.root.title(f"시니어 콘텐츠 에디터 - {selected_project}")

    def _initialize_tabs(self):
        """탭들 초기화"""
        # 탭 인스턴스 생성
        self.tabs = {
            'synopsis': SynopsisInputTab(self.notebook, self.project_data, self.file_service, self.content_generator),
            'characters': ImageGenerationTab(self.notebook, self.project_data, self.file_service, self.content_generator),
            'chapters': ChapterDetailsInputTab(self.notebook, self.project_data, self.file_service, self.content_generator),
            'scripts': ScriptsTab(self.notebook, self.project_data, self.file_service, self.content_generator),
            'scene_prompts': ImagePromptsInputTab(self.notebook, self.project_data, self.file_service, self.content_generator),
            'comfyui': ComfyUITab(self.notebook, self.project_data, self.file_service, self.content_generator),
            'tts': TTSTab(self.notebook, self.project_data, self.file_service, self.content_generator),
            'episode_splitter': EpisodeSplitterTab(self.notebook, self.project_data, self.file_service, self.content_generator),
            'word_converter': WordConverterTab(self.notebook, self.project_data, self.file_service, self.content_generator)
        }

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

        # 탭 업데이트 (dirty 플래그가 있을 때만)
        tab = self.tabs[tab_id]
        if getattr(tab, '_needs_update', True):
            tab.update_display()
            tab._needs_update = False

    def _load_project_data(self):
        """프로젝트 데이터 로드"""
        try:
            if self.project_path is None or not self.project_path.exists():
                self.status_var.set("프로젝트를 선택해주세요")
                return

            # 모든 데이터 로드
            data = self.file_service.load_all_data()
            self.project_data.data = data

            # 프로젝트 경로 업데이트
            self.project_data.project_path = self.project_path

            # 상태바에 프로젝트 정보 표시
            char_count = len(data.get('characters', []))
            self.status_var.set(
                f"프로젝트: {self.project_path.name} | 캐릭터: {char_count}명 | 경로: {self.project_path}"
            )

        except Exception as e:
            error_msg = f"데이터 로드 실패: {e}"
            self.status_var.set(f"오류: {e}")
            print(f"[프로젝트 로드 오류] {error_msg}")
            import traceback
            traceback.print_exc()

    def _save_all(self):
        """모든 변경사항 저장"""
        try:
            success_count = 0
            fail_count = 0
            failed_tabs = []

            # 각 탭의 저장 메서드 호출
            for tab_id, tab in self.tabs.items():
                try:
                    ok = tab.save()
                    if ok:
                        success_count += 1
                    else:
                        fail_count += 1
                        failed_tabs.append(tab_id)
                except Exception as e:
                    print(f"{tab_id} 탭 저장 오류: {e}")
                    fail_count += 1
                    failed_tabs.append(tab_id)

            self.project_data.clear_unsaved()
            self.status_var.set(f"저장 완료! (성공: {success_count}, 실패: {fail_count})")

            if fail_count > 0:
                messagebox.showwarning(
                    "저장 결과",
                    "일부 탭 저장에 실패했습니다.\n\n"
                    f"- 성공: {success_count}\n"
                    f"- 실패: {fail_count}\n\n"
                    "실패 탭:\n"
                    + "\n".join(f"- {t}" for t in failed_tabs)
                )
            else:
                messagebox.showinfo("저장", "모든 변경사항이 저장되었습니다.")
        except Exception as e:
            messagebox.showerror("저장 오류", f"저장 중 오류가 발생했습니다: {e}")
            self.status_var.set(f"저장 오류: {e}")

    def _open_settings(self):
        """설정 창 열기"""
        SettingsDialog(self.root, self.config, self.project_data, self.file_service)

    def _convert_word_to_md(self):
        """Word 파일을 Markdown으로 변환"""
        # 파일 선택 대화상자
        initial_dir = str(self.project_path) if self.project_path and self.project_path.exists() else None

        word_file = filedialog.askopenfilename(
            title="Word 파일 선택",
            filetypes=[
                ("Word 문서", "*.docx"),
                ("모든 파일", "*.*")
            ],
            initialdir=initial_dir
        )

        if not word_file:
            return

        # 저장 위치 선택
        default_name = Path(word_file).stem + ".md"
        default_dir = Path(word_file).parent

        save_path = filedialog.asksaveasfilename(
            title="Markdown 파일 저장",
            defaultextension=".md",
            filetypes=[("Markdown 파일", "*.md")],
            initialfile=default_name,
            initialdir=str(default_dir)
        )

        if not save_path:
            return

        # 변환 실행
        self.status_var.set("Word → MD 변환 중...")
        self.root.update()

        success, message, output_path = convert_word_to_markdown(word_file, save_path)

        if success:
            self.status_var.set(f"변환 완료: {Path(output_path).name}")
            messagebox.showinfo("변환 완료", message)
        else:
            self.status_var.set("변환 실패")
            messagebox.showerror("변환 오류", message)
