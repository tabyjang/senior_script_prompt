"""
장면 탭
챕터별 10개 장면 생성 및 관리를 제공합니다.
원본 viewer_editor.py의 로직을 완전히 이식한 버전
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
from typing import Optional, Dict, List
from .base_tab import BaseTab
from utils.json_utils import extract_json_from_text
import threading
import time


class ScenesTab(BaseTab):
    """장면 탭 클래스 - 원본 로직 완전 이식"""

    def __init__(self, parent, project_data, file_service, content_generator):
        """초기화"""
        # 챕터 선택 변수 초기화
        self.scenes_chapter_var = None
        self.scenes_chapter_combo = None
        self.scenes_script_viewer = None
        self.scenes_tab_viewer_frame = None
        self.scenes_tab_canvas = None
        self.scenes_tab_right_frame = None
        self.scenes_tab_paned = None

        # 부모 클래스 초기화
        super().__init__(parent, project_data, file_service, content_generator)

    def get_tab_name(self) -> str:
        return "장면 생성"

    def create_ui(self):
        """
        UI 생성
        원본 create_scenes_tab() 메서드의 로직을 완전히 이식
        - 좌우 분할: 왼쪽(챕터 선택 + 대본) | 오른쪽(10개 장면 목록)
        """
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(0, weight=1)

        # 좌우 분할 (PanedWindow)
        paned_horizontal = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        paned_horizontal.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # 왼쪽: 챕터 선택 + 대본
        left_frame = ttk.LabelFrame(paned_horizontal, text="대본", padding=10)
        paned_horizontal.add(left_frame, weight=1)
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)

        # 챕터 선택 영역
        chapter_select_frame = ttk.Frame(left_frame)
        chapter_select_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(chapter_select_frame, text="챕터 선택:", font=("맑은 고딕", 10)).pack(side=tk.LEFT, padx=5)

        self.scenes_chapter_var = tk.StringVar()
        self.scenes_chapter_combo = ttk.Combobox(
            chapter_select_frame,
            textvariable=self.scenes_chapter_var,
            width=30,
            state='readonly'
        )
        self.scenes_chapter_combo.pack(side=tk.LEFT, padx=5)
        self.scenes_chapter_combo.bind('<<ComboboxSelected>>', lambda e: self._on_chapter_selected())

        # 장면 생성 버튼
        scene_gen_btn = ttk.Button(
            chapter_select_frame,
            text="🎬 장면 생성 (10개)",
            command=self._generate_current_chapter
        )
        scene_gen_btn.pack(side=tk.LEFT, padx=5)

        # 모든 챕터 장면 생성 버튼
        all_scenes_gen_btn = ttk.Button(
            chapter_select_frame,
            text="🔄 모든 챕터 장면 생성",
            command=self._generate_all_chapters
        )
        all_scenes_gen_btn.pack(side=tk.LEFT, padx=5)

        # 대본 표시 영역 (세로로 길게)
        script_display_frame = ttk.Frame(left_frame)
        script_display_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        script_display_frame.columnconfigure(0, weight=1)
        script_display_frame.rowconfigure(0, weight=1)

        self.scenes_script_viewer = scrolledtext.ScrolledText(
            script_display_frame,
            width=60,
            height=40,
            wrap=tk.WORD,
            font=("맑은 고딕", 11),
            state=tk.DISABLED
        )
        self.scenes_script_viewer.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 오른쪽: 10개 장면 정보 (세로로 길게)
        right_frame = ttk.LabelFrame(paned_horizontal, text="장면 목록 (10개)", padding=10)
        paned_horizontal.add(right_frame, weight=1)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)

        # 스크롤 가능한 장면 목록
        canvas_scenes = tk.Canvas(right_frame)
        scrollbar_scenes = ttk.Scrollbar(right_frame, orient="vertical", command=canvas_scenes.yview)
        self.scenes_tab_viewer_frame = ttk.Frame(canvas_scenes)

        # Canvas에 스크롤 영역 설정
        self.scenes_tab_viewer_frame.bind(
            "<Configure>",
            lambda e: canvas_scenes.configure(scrollregion=canvas_scenes.bbox("all"))
        )

        canvas_scenes.create_window((0, 0), window=self.scenes_tab_viewer_frame, anchor="nw")
        canvas_scenes.configure(yscrollcommand=scrollbar_scenes.set)

        canvas_scenes.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_scenes.grid(row=0, column=1, sticky=(tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)

        # Canvas 참조 저장 (나중에 마우스 휠 재바인딩용)
        self.scenes_tab_canvas = canvas_scenes
        self.scenes_tab_right_frame = right_frame
        self.scenes_tab_paned = paned_horizontal

        # 마우스 휠 이벤트 바인딩 (변수 할당 후에 호출)
        self._bind_initial_mousewheel(canvas_scenes)

    def _bind_initial_mousewheel(self, canvas_scenes):
        """
        초기 마우스 휠 이벤트 바인딩
        원본의 복잡한 마우스 휠 바인딩 로직 이식
        """
        def on_mousewheel_scenes(event):
            """마우스 휠 스크롤 처리 (Windows와 Linux 모두 지원)"""
            try:
                if hasattr(event, 'num'):
                    # Linux
                    if event.num == 4:
                        canvas_scenes.yview_scroll(-3, "units")
                    elif event.num == 5:
                        canvas_scenes.yview_scroll(3, "units")
                elif hasattr(event, 'delta'):
                    # Windows
                    if event.delta > 0:
                        canvas_scenes.yview_scroll(-3, "units")
                    else:
                        canvas_scenes.yview_scroll(3, "units")
            except:
                pass
            return "break"

        def bind_mousewheel_to_widget(widget):
            """위젯과 모든 자식 위젯에 마우스 휠 바인딩 (재귀적)"""
            if widget is None:
                return
            try:
                widget.bind("<MouseWheel>", on_mousewheel_scenes, add='+')
                widget.bind("<Button-4>", on_mousewheel_scenes, add='+')
                widget.bind("<Button-5>", on_mousewheel_scenes, add='+')
                for child in widget.winfo_children():
                    bind_mousewheel_to_widget(child)
            except:
                pass

        # Canvas에 직접 바인딩
        canvas_scenes.bind("<MouseWheel>", on_mousewheel_scenes, add='+')
        canvas_scenes.bind("<Button-4>", on_mousewheel_scenes, add='+')
        canvas_scenes.bind("<Button-5>", on_mousewheel_scenes, add='+')
        canvas_scenes.bind("<Enter>", lambda e: canvas_scenes.focus_set())

        # Frame과 모든 자식 위젯에 바인딩
        bind_mousewheel_to_widget(self.scenes_tab_viewer_frame)
        bind_mousewheel_to_widget(canvas_scenes)

        # right_frame 전체 영역에서도 작동하도록
        if hasattr(self, 'scenes_tab_right_frame') and self.scenes_tab_right_frame is not None:
            self.scenes_tab_right_frame.bind("<MouseWheel>", on_mousewheel_scenes, add='+')
            self.scenes_tab_right_frame.bind("<Button-4>", on_mousewheel_scenes, add='+')
            self.scenes_tab_right_frame.bind("<Button-5>", on_mousewheel_scenes, add='+')

        # paned_horizontal에도 바인딩
        if hasattr(self, 'scenes_tab_paned') and self.scenes_tab_paned is not None:
            self.scenes_tab_paned.bind("<MouseWheel>", on_mousewheel_scenes, add='+')
            self.scenes_tab_paned.bind("<Button-4>", on_mousewheel_scenes, add='+')
            self.scenes_tab_paned.bind("<Button-5>", on_mousewheel_scenes, add='+')

        # Canvas 포커스 설정
        canvas_scenes.focus_set()

    def update_display(self):
        """
        화면 업데이트
        챕터 목록을 콤보박스에 로드
        """
        chapters = self.project_data.get_chapters()

        # 챕터 목록을 콤보박스에 로드
        chapter_list = [f"챕터 {ch.get('chapter_number', i+1)}: {ch.get('title', '제목 없음')}"
                       for i, ch in enumerate(chapters)]

        if self.scenes_chapter_combo:
            self.scenes_chapter_combo['values'] = chapter_list
            if chapter_list and not self.scenes_chapter_var.get():
                self.scenes_chapter_combo.current(0)
                self._on_chapter_selected()

    def _on_chapter_selected(self):
        """
        챕터 선택 시 대본과 장면 로드
        원본 on_scenes_chapter_selected() 메서드의 로직을 완전히 이식
        """
        if not hasattr(self, 'scenes_chapter_var'):
            return

        selected = self.scenes_chapter_var.get()
        if not selected:
            return

        # 선택된 챕터 번호 추출
        try:
            chapter_num = int(selected.split(':')[0].replace('챕터', '').strip())
        except Exception as e:
            print(f"챕터 번호 추출 오류: {e}")
            return

        # 해당 챕터 찾기
        chapters = self.project_data.get_chapters()
        chapter = None
        for ch in chapters:
            if ch.get('chapter_number') == chapter_num:
                chapter = ch
                break

        if not chapter:
            print(f"챕터 {chapter_num}을 찾을 수 없습니다.")
            return

        # 대본 표시
        script = chapter.get('script', '')
        if hasattr(self, 'scenes_script_viewer'):
            self.scenes_script_viewer.config(state=tk.NORMAL)
            self.scenes_script_viewer.delete(1.0, tk.END)
            if script:
                self.scenes_script_viewer.insert(1.0, script)
            else:
                self.scenes_script_viewer.insert(1.0, "대본이 아직 생성되지 않았습니다.\n\n'대본' 탭에서 먼저 대본을 생성해주세요.")
            self.scenes_script_viewer.config(state=tk.DISABLED)

        # 장면 표시 업데이트
        self._update_scenes_display(chapter)

    def _update_scenes_display(self, chapter):
        """
        장면 목록 표시 업데이트
        원본 update_scenes_tab_display() 메서드의 로직을 완전히 이식
        """
        if not hasattr(self, 'scenes_tab_viewer_frame'):
            return

        # 기존 위젯 제거
        for widget in self.scenes_tab_viewer_frame.winfo_children():
            widget.destroy()

        scenes = chapter.get('scenes', [])
        if not scenes:
            ttk.Label(
                self.scenes_tab_viewer_frame,
                text="장면이 아직 생성되지 않았습니다.\n\n위의 '🎬 장면 생성 (10개)' 버튼을 클릭하세요.",
                font=("맑은 고딕", 11)
            ).pack(pady=20)
            return

        # 각 장면 표시
        for idx, scene in enumerate(scenes):
            self._create_scene_widget(idx, scene)

        # 새로 생성된 위젯들에 마우스 휠 바인딩 재적용
        self._rebind_mousewheel()

    def _create_scene_widget(self, idx: int, scene: dict):
        """
        장면 위젯 생성
        원본 create_scene_tab_widget() 메서드의 로직을 완전히 이식
        """
        scene_num = scene.get('scene_number', idx + 1)
        scene_title = scene.get('title', f'장면 {scene_num}')
        scene_prompt = scene.get('image_prompt', '')

        frame = ttk.LabelFrame(
            self.scenes_tab_viewer_frame,
            text=f"장면 {scene_num}: {scene_title}",
            padding=15
        )
        frame.pack(fill=tk.X, padx=15, pady=10)

        # 제목
        title_frame = ttk.Frame(frame)
        title_frame.pack(fill=tk.X, pady=5)
        ttk.Label(title_frame, text="제목:", font=("맑은 고딕", 10, "bold"), width=12).pack(side=tk.LEFT)
        ttk.Label(title_frame, text=scene_title, font=("맑은 고딕", 10)).pack(side=tk.LEFT)

        # 이미지 프롬프트
        prompt_label_frame = ttk.Frame(frame)
        prompt_label_frame.pack(fill=tk.X, pady=5)
        ttk.Label(prompt_label_frame, text="이미지 프롬프트:", font=("맑은 고딕", 10, "bold"), width=12).pack(side=tk.LEFT, anchor=tk.N)

        # 프롬프트와 복사 버튼을 담을 프레임
        prompt_content_frame = ttk.Frame(prompt_label_frame)
        prompt_content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 프롬프트 텍스트 영역
        prompt_text = scrolledtext.ScrolledText(
            prompt_content_frame,
            width=80,
            height=8,
            wrap=tk.WORD,
            font=("맑은 고딕", 10),
            state=tk.DISABLED
        )
        prompt_text.pack(fill=tk.BOTH, expand=True)
        prompt_text.config(state=tk.NORMAL)
        prompt_text.insert(1.0, scene_prompt)
        prompt_text.config(state=tk.DISABLED)

        # 복사 버튼 (프롬프트 아래)
        copy_btn_frame = ttk.Frame(prompt_content_frame)
        copy_btn_frame.pack(fill=tk.X, pady=(5, 0))

        def copy_prompt():
            """이미지 프롬프트를 클립보드에 복사"""
            try:
                # tkinter의 클립보드 기능 사용
                self.frame.clipboard_clear()
                self.frame.clipboard_append(scene_prompt)
                self.frame.update()  # 클립보드 업데이트 확실히 하기
                messagebox.showinfo("복사 완료", "이미지 프롬프트가 클립보드에 복사되었습니다.")
            except Exception as e:
                messagebox.showerror("오류", f"클립보드 복사 중 오류 발생:\n{e}")

        copy_btn = ttk.Button(
            copy_btn_frame,
            text="📋 복사",
            command=copy_prompt,
            width=15
        )
        copy_btn.pack(side=tk.LEFT)

    def _rebind_mousewheel(self):
        """
        마우스 휠 이벤트 재바인딩
        원본 _rebind_mousewheel_to_scenes_tab() 메서드의 로직을 완전히 이식
        """
        if not hasattr(self, 'scenes_tab_canvas') or not hasattr(self, 'scenes_tab_viewer_frame'):
            return

        canvas_scenes = self.scenes_tab_canvas

        def on_mousewheel_scenes(event):
            try:
                if hasattr(event, 'delta'):
                    # Windows
                    delta = event.delta
                    if delta > 0:
                        canvas_scenes.yview_scroll(-3, "units")
                    else:
                        canvas_scenes.yview_scroll(3, "units")
                elif hasattr(event, 'num'):
                    # Linux
                    if event.num == 4:
                        canvas_scenes.yview_scroll(-3, "units")
                    elif event.num == 5:
                        canvas_scenes.yview_scroll(3, "units")
            except Exception as e:
                print(f"마우스 휠 오류: {e}")
            return "break"

        def bind_mousewheel_to_widget(widget):
            if widget is None:
                return
            try:
                widget.bind("<MouseWheel>", on_mousewheel_scenes, add='+')
                widget.bind("<Button-4>", on_mousewheel_scenes, add='+')
                widget.bind("<Button-5>", on_mousewheel_scenes, add='+')
                for child in widget.winfo_children():
                    bind_mousewheel_to_widget(child)
            except:
                pass

        # Canvas에 직접 바인딩
        canvas_scenes.bind("<MouseWheel>", on_mousewheel_scenes, add='+')
        canvas_scenes.bind("<Button-4>", on_mousewheel_scenes, add='+')
        canvas_scenes.bind("<Button-5>", on_mousewheel_scenes, add='+')
        canvas_scenes.bind("<Enter>", lambda e: canvas_scenes.focus_set())

        # 새로 생성된 모든 위젯에 마우스 휠 바인딩
        bind_mousewheel_to_widget(self.scenes_tab_viewer_frame)

        # right_frame에도 바인딩
        if hasattr(self, 'scenes_tab_right_frame') and self.scenes_tab_right_frame is not None:
            right_frame = self.scenes_tab_right_frame
            right_frame.bind("<MouseWheel>", on_mousewheel_scenes, add='+')
            right_frame.bind("<Button-4>", on_mousewheel_scenes, add='+')
            right_frame.bind("<Button-5>", on_mousewheel_scenes, add='+')

        # paned_horizontal에도 바인딩
        if hasattr(self, 'scenes_tab_paned') and self.scenes_tab_paned is not None:
            paned = self.scenes_tab_paned
            paned.bind("<MouseWheel>", on_mousewheel_scenes, add='+')
            paned.bind("<Button-4>", on_mousewheel_scenes, add='+')
            paned.bind("<Button-5>", on_mousewheel_scenes, add='+')

    def _generate_current_chapter(self):
        """
        현재 선택된 챕터의 장면 생성
        원본 generate_scenes_for_chapter_from_scenes_tab() 메서드의 로직을 완전히 이식
        """
        selected = self.scenes_chapter_var.get()
        if not selected:
            messagebox.showwarning("경고", "챕터를 선택해주세요.")
            return

        # 선택된 챕터 번호 추출
        try:
            chapter_num = int(selected.split(':')[0].replace('챕터', '').strip())
        except:
            messagebox.showerror("오류", "챕터 번호를 추출할 수 없습니다.")
            return

        # 챕터 찾기
        chapters = self.project_data.get_chapters()
        chapter = None
        chapter_index = -1
        for i, ch in enumerate(chapters):
            if ch.get('chapter_number') == chapter_num:
                chapter = ch
                chapter_index = i
                break

        if not chapter:
            messagebox.showerror("오류", f"챕터 {chapter_num}을 찾을 수 없습니다.")
            return

        # 대본 확인
        script = chapter.get('script', '')
        if not script:
            messagebox.showwarning("경고", "대본이 없습니다.\n먼저 대본을 생성해주세요.")
            return

        # 확인 대화상자
        result = messagebox.askyesno(
            "장면 생성",
            f"챕터 {chapter_num}의 대본을 분석하여 10개의 장면을 생성하시겠습니까?\n\n"
            f"각 장면에는 한글 제목과 Stable Diffusion 이미지 프롬프트가 생성됩니다.\n\n"
            f"이 작업은 시간이 걸릴 수 있습니다."
        )
        if not result:
            return

        # 장면 생성 실행
        success = self._generate_scenes(chapter_num, chapter, chapter_index)

        # 생성 성공 시 화면 업데이트
        if success:
            self._on_chapter_selected()

    def _generate_all_chapters(self):
        """
        모든 챕터에 대해 장면 생성
        원본 generate_scenes_for_all_chapters() 메서드의 로직을 완전히 이식
        """
        chapters = self.project_data.get_chapters()

        if not chapters:
            messagebox.showwarning("경고", "챕터가 없습니다.")
            return

        # 대본이 있는 챕터만 필터링
        chapters_with_script = []
        for ch in chapters:
            if ch.get('script', ''):
                chapters_with_script.append(ch)

        if not chapters_with_script:
            messagebox.showwarning("경고", "대본이 있는 챕터가 없습니다.\n먼저 대본을 생성해주세요.")
            return

        # 확인 대화상자
        result = messagebox.askyesno(
            "모든 챕터 장면 생성",
            f"총 {len(chapters_with_script)}개 챕터의 대본을 분석하여 각각 10개의 장면을 생성하시겠습니까?\n\n"
            f"각 챕터마다 3초씩 딜레이가 있으며, 전체 작업은 시간이 오래 걸릴 수 있습니다.\n\n"
            f"진행 중에는 창을 닫지 마세요."
        )
        if not result:
            return

        # 백그라운드 스레드에서 순차적으로 처리
        thread = threading.Thread(
            target=self._generate_all_scenes_sequential,
            args=(chapters_with_script,),
            daemon=True
        )
        thread.start()

    def _generate_all_scenes_sequential(self, chapters):
        """
        모든 챕터에 대해 순차적으로 장면 생성
        원본 _generate_all_scenes_sequential() 메서드의 로직을 완전히 이식
        """
        total = len(chapters)
        success_count = 0
        fail_count = 0

        for idx, chapter in enumerate(chapters, 1):
            chapter_num = chapter.get('chapter_number', idx)
            chapter_title = chapter.get('title', '제목 없음')

            # 챕터 인덱스 찾기
            chapter_index = -1
            all_chapters = self.project_data.get_chapters()
            for i, ch in enumerate(all_chapters):
                if ch.get('chapter_number') == chapter_num:
                    chapter_index = i
                    break

            # 장면 생성
            try:
                success = self._generate_scenes(chapter_num, chapter, chapter_index, show_message=False)
                if success:
                    success_count += 1
                else:
                    fail_count += 1
            except Exception as e:
                fail_count += 1
                print(f"챕터 {chapter_num} 장면 생성 오류: {e}")

            # 마지막 챕터가 아니면 3초 딜레이
            if idx < total:
                time.sleep(3)

        # 완료 메시지
        def show_completion():
            messagebox.showinfo(
                "완료",
                f"모든 챕터의 장면 생성이 완료되었습니다.\n\n"
                f"성공: {success_count}개 챕터\n"
                f"실패: {fail_count}개 챕터"
            )
            # 화면 업데이트
            if hasattr(self, 'scenes_chapter_var') and self.scenes_chapter_var.get():
                self._on_chapter_selected()

        # GUI 업데이트는 메인 스레드에서
        self.frame.after(0, show_completion)

    def _generate_scenes(self, chapter_num: int, chapter: dict, chapter_index: int, show_message: bool = True) -> bool:
        """
        챕터 장면 생성 (내부 함수)
        원본 _generate_scenes() 메서드의 로직을 완전히 이식
        """
        # 시놉시스 정보
        synopsis = self.project_data.get_synopsis()

        # 인물 정보
        characters = self.project_data.get_characters()
        characters_info = self._format_characters_for_prompt(characters)

        # 챕터 정보
        chapter_title = chapter.get('title', '')
        chapter_summary = chapter.get('summary', '')
        script = chapter.get('script', '')

        # 인물별 이미지 프롬프트 정보 수집
        character_prompts_info = ""
        for char in characters:
            char_name = char.get('name', '')
            prompts = char.get('image_generation_prompts', {})
            if prompts:
                # 첫 번째 프롬프트를 참고용으로 사용
                first_prompt = prompts.get('prompt_1', char.get('image_generation_prompt', ''))
                if first_prompt:
                    character_prompts_info += f"\n- {char_name}: {first_prompt[:200]}...\n"

        # LLM 호출
        try:
            scenes = self.content_generator.generate_scenes(
                chapter,
                synopsis,
                characters_info,
                character_prompts_info
            )

            if not scenes:
                if show_message:
                    messagebox.showerror("오류", "장면 생성에 실패했습니다.")
                return False

            if len(scenes) != 10:
                if show_message:
                    messagebox.showwarning(
                        "경고",
                        f"10개의 장면이 생성되지 않았습니다. (생성된 장면: {len(scenes)}개)"
                    )

            # 챕터 데이터에 장면 저장 (참조용)
            chapter['scenes'] = scenes
            chapter['scenes_generated_at'] = datetime.now().isoformat()

            # 데이터 업데이트
            chapters = self.project_data.get_chapters()
            chapters[chapter_index] = chapter
            self.project_data.set_chapters(chapters)

            # 대본 파일에 장면 정보 저장 (04_scripts/ 폴더)
            try:
                self.file_service.save_scenes_to_script(
                    chapter_number=chapter_num,
                    scenes=scenes
                )
            except Exception as save_error:
                print(f"경고: 대본 파일에 장면 저장 중 오류 발생: {save_error}")
            
            # 챕터 파일도 저장 (참조용)
            try:
                single_chapter_list = [chapter]
                self.file_service.save_chapters(single_chapter_list)
            except Exception as save_error:
                print(f"경고: 챕터 파일 저장 중 오류 발생: {save_error}")

            if show_message:
                messagebox.showinfo("완료", f"챕터 {chapter_num}의 장면이 생성되고 자동 저장되었습니다.\n생성된 장면: {len(scenes)}개")

            return True

        except Exception as e:
            if show_message:
                messagebox.showerror("오류", f"장면 생성 중 오류 발생:\n{e}")
            return False

    def _format_characters_for_prompt(self, characters: list) -> str:
        """인물 정보를 프롬프트용 텍스트로 포맷팅"""
        if not characters:
            return "등장인물 정보 없음"

        result = []
        for char in characters:
            name = char.get('name', '알 수 없음')
            age_raw = char.get('age', '불명')
            
            # 나이를 정수로 변환
            if isinstance(age_raw, str):
                try:
                    age = int(age_raw)
                except:
                    age = 35
            else:
                age = int(age_raw) if age_raw else 35
            
            # Youth age 계산 (나이대별 차감 규칙, 최소 25세)
            # 60세 이상: 20세 차감, 50세 이상: 15세 차감, 40세 이상: 10세 차감, 30세 이상: 7세 차감
            if age >= 60:
                age_deduction = 20
            elif age >= 50:
                age_deduction = 15
            elif age >= 40:
                age_deduction = 10
            elif age >= 30:
                age_deduction = 7
            else:
                # 30세 미만은 최소값 적용
                age_deduction = 0
            youth_age = max(25, age - age_deduction)
            
            gender = char.get('gender', '불명')
            personality = char.get('personality', '불명')
            background = char.get('background', '불명')

            char_info = f"- {name} (실제 나이: {age}세, Youth age: {youth_age}세, {gender}): {personality}"
            if background and background != '불명':
                char_info += f"\n  배경: {background}"
            result.append(char_info)

        return '\n'.join(result)

    def save(self) -> bool:
        """
        데이터 저장
        장면 탭은 자동 저장되므로 별도 저장 불필요
        """
        return True  # 자동 저장됨
