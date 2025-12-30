"""
메인 윈도우
프로젝트 뷰어/에디터의 메인 GUI 윈도우입니다.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

# 탭들 import
from gui.tabs.synopsis_tab import SynopsisTab
from gui.tabs.synopsis_input_tab import SynopsisInputTab
from gui.tabs.characters_tab import CharactersTab
from gui.tabs.character_details_input_tab import CharacterDetailsInputTab
from gui.tabs.chapters_tab import ChaptersTab
from gui.tabs.chapter_details_input_tab import ChapterDetailsInputTab
from gui.tabs.scripts_tab import ScriptsTab
from gui.tabs.scenes_tab import ScenesTab
from gui.tabs.image_prompts_tab import ImagePromptsTab
from gui.tabs.image_prompts_input_tab import ImagePromptsInputTab
from gui.tabs.image_generation_tab import ImageGenerationTab
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

        # 프로젝트 표시(왼쪽) - 현재 작업 폴더명/경로를 항상 보여줌
        self.project_title_var = tk.StringVar(value="")
        project_title = ttk.Label(
            toolbar,
            textvariable=self.project_title_var,
            font=("맑은 고딕", 11, "bold")
        )
        project_title.grid(row=0, column=0, sticky=tk.W, padx=(5, 10))

        # 버튼 프레임 (오른쪽 정렬)
        button_frame = ttk.Frame(toolbar)
        button_frame.grid(row=0, column=1, sticky=tk.E)

        # 프로젝트 열기 버튼
        open_project_btn = ttk.Button(
            button_frame,
            text="📁 프로젝트 열기",
            command=self._open_project,
            width=18
        )
        open_project_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 설정 버튼
        settings_btn = ttk.Button(button_frame, text="⚙ 설정", command=self._open_settings, width=12)
        settings_btn.pack(side=tk.LEFT)

        # 왼쪽 사이드바 (탭 목록)
        self._create_sidebar(main_frame)

        # 오른쪽 콘텐츠 영역 (노트북)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Notebook 탭 헤더 숨기기 (왼쪽 사이드바로 탭 전환)
        style = ttk.Style()
        style.layout("TNotebook.Tab", [])  # 탭 헤더 제거

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
            ("synopsis_input", "시놉시스 입력"),
            ("characters", "인물"),
            ("character_details_input", "인물 세부정보 입력"),
            ("image_prompts", "이미지 프롬프트"),
            ("image_prompts_input", "이미지 프롬프트 입력"),
            ("chapters", "챕터"),
            ("chapter_details_input", "챕터 세부정보 입력"),
            ("scripts", "대본"),
            ("scenes", "장면 생성"),
            ("image_generation", "이미지 생성"),
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
            'synopsis_input': SynopsisInputTab(self.notebook, self.project_data, self.file_service, self.content_generator),
            'characters': CharactersTab(self.notebook, self.project_data, self.file_service, self.content_generator),
            'character_details_input': CharacterDetailsInputTab(self.notebook, self.project_data, self.file_service, self.content_generator),
            'chapters': ChaptersTab(self.notebook, self.project_data, self.file_service, self.content_generator),
            'chapter_details_input': ChapterDetailsInputTab(self.notebook, self.project_data, self.file_service, self.content_generator),
            'scripts': ScriptsTab(self.notebook, self.project_data, self.file_service, self.content_generator),
            'scenes': ScenesTab(self.notebook, self.project_data, self.file_service, self.content_generator),
            'image_prompts': ImagePromptsTab(self.notebook, self.project_data, self.file_service, self.content_generator),
            'image_prompts_input': ImagePromptsInputTab(self.notebook, self.project_data, self.file_service, self.content_generator),
            'image_generation': ImageGenerationTab(self.notebook, self.project_data, self.file_service, self.content_generator),
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
            # 프로젝트 폴더 존재 확인
            if not self.project_path.exists():
                self.status_var.set(f"프로젝트 폴더가 존재하지 않습니다: {self.project_path}")
                return

            # 모든 데이터 로드
            data = self.file_service.load_all_data()
            self.project_data.data = data
            
            # 프로젝트 경로 업데이트
            self.project_data.project_path = self.project_path
            
            # 상태바에 프로젝트 정보 표시
            char_count = len(data.get('characters', []))
            chapter_count = len(data.get('chapters', []))
            synopsis_title = data.get('synopsis', {}).get('title', '제목 없음')
            self.status_var.set(
                f"프로젝트: {synopsis_title} | 캐릭터: {char_count}명, 챕터: {chapter_count}개 | 경로: {self.project_path}"
            )

            # 상단 툴바에 현재 작업 폴더 표시 (폴더명 + 전체 경로)
            folder_name = self.project_path.name
            self.project_title_var.set(f"📁 {folder_name}   ({self.project_path})")
        except Exception as e:
            error_msg = f"데이터 로드 실패: {e}"
            messagebox.showerror("오류", error_msg)
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

    def _open_project(self):
        """프로젝트 열기"""
        # 초기 디렉토리 설정 (마지막 프로젝트 경로 또는 현재 프로젝트 경로)
        initial_dir = None
        last_path = self.config.get_last_project_path()
        if last_path and Path(last_path).exists():
            initial_dir = str(Path(last_path).parent)
        elif self.project_path.exists():
            initial_dir = str(self.project_path.parent)
        
        project_dir = filedialog.askdirectory(
            title="프로젝트 폴더 선택",
            initialdir=initial_dir
        )
        
        if project_dir:
            project_path = Path(project_dir).resolve()
            
            # 프로젝트 폴더 유효성 확인 (synopsis.json이 있는지 확인)
            synopsis_file = project_path / "synopsis.json"
            if not synopsis_file.exists():
                # synopsis.json이 없어도 경고만 표시하고 계속 진행
                response = messagebox.askyesno(
                    "경고",
                    f"선택한 폴더에 synopsis.json 파일이 없습니다.\n"
                    f"계속 진행하시겠습니까?\n\n"
                    f"경로: {project_path}"
                )
                if not response:
                    return
            
            # 프로젝트 경로 업데이트
            self.project_path = project_path
            self.file_service.project_path = project_path
            self.project_data.project_path = project_path
            
            # 마지막 프로젝트 경로를 설정 파일에 저장
            self.config.set_last_project_path(str(project_path))
            
            # 데이터 로드
            self._load_project_data()

            # 모든 탭 업데이트
            for tab in self.tabs.values():
                tab.update_display()
            
            # 윈도우 제목 업데이트
            synopsis = self.project_data.get_synopsis()
            title = synopsis.get('title', '제목 없음') if synopsis else '제목 없음'
            self.root.title(f"프로젝트 뷰어/에디터 - {title}")

            # 상단 툴바 표시도 갱신
            try:
                folder_name = self.project_path.name
                self.project_title_var.set(f"📁 {folder_name}   ({self.project_path})")
            except Exception:
                pass
            
            messagebox.showinfo("프로젝트 열기", f"프로젝트를 성공적으로 불러왔습니다.\n\n{project_path}")

    def _open_settings(self):
        """설정 창 열기"""
        SettingsDialog(self.root, self.config, self.project_data, self.file_service)
