"""
챕터 탭
챕터 목록 뷰어 및 JSON 에디터를 제공합니다.
원본 viewer_editor.py의 로직을 완전히 이식한 버전
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
from .base_tab import BaseTab
from utils.json_utils import format_json, safe_json_loads


class ChaptersTab(BaseTab):
    """챕터 탭 클래스 - 원본 로직 완전 이식"""

    def get_tab_name(self) -> str:
        return "챕터"

    def create_ui(self):
        """
        UI 생성
        원본 create_chapters_tab() 메서드의 로직을 완전히 이식
        - 상단: 전체 대본 생성 버튼
        - PanedWindow로 상하 분할 (뷰어/에디터)
        - 뷰어: 스크롤 가능한 Canvas에 챕터 카드들 표시
        - 에디터: JSON 편집기
        """
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)

        # 상단: 전체 대본 생성 버튼
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        generate_all_btn = ttk.Button(
            button_frame,
            text="🔄 전체 대본 생성",
            command=self._generate_all_scripts
        )
        generate_all_btn.pack(side=tk.LEFT, padx=5)

        # PanedWindow로 크기 조절 가능하게 (상하 분할)
        paned_vertical = ttk.PanedWindow(self.frame, orient=tk.VERTICAL)
        paned_vertical.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # 상단: 좌우 분할 영역
        top_container = ttk.Frame(paned_vertical)
        paned_vertical.add(top_container, weight=2)
        top_container.columnconfigure(0, weight=1)
        top_container.rowconfigure(0, weight=1)

        # 좌우 분할 PanedWindow
        paned_horizontal = ttk.PanedWindow(top_container, orient=tk.HORIZONTAL)
        paned_horizontal.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 왼쪽: 챕터 목록 뷰어
        chapters_list_frame = ttk.LabelFrame(paned_horizontal, text="챕터 목록", padding=10)
        paned_horizontal.add(chapters_list_frame, weight=2)
        chapters_list_frame.columnconfigure(0, weight=1)
        chapters_list_frame.rowconfigure(0, weight=1)

        # 스크롤 가능한 뷰어 (Canvas + Scrollbar)
        self.canvas_viewer = tk.Canvas(chapters_list_frame)
        self.scrollbar_viewer = ttk.Scrollbar(
            chapters_list_frame,
            orient="vertical",
            command=self.canvas_viewer.yview
        )
        self.chapters_viewer_frame = ttk.Frame(self.canvas_viewer)

        # Canvas 스크롤 영역 설정
        self.chapters_viewer_frame.bind(
            "<Configure>",
            lambda e: self.canvas_viewer.configure(scrollregion=self.canvas_viewer.bbox("all"))
        )

        self.canvas_viewer.create_window((0, 0), window=self.chapters_viewer_frame, anchor="nw")
        self.canvas_viewer.configure(yscrollcommand=self.scrollbar_viewer.set)

        # 마우스 휠 이벤트 바인딩 (Canvas와 모든 자식 위젯에)
        self._bind_initial_mousewheel()

        # Canvas와 Scrollbar 배치
        self.canvas_viewer.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scrollbar_viewer.grid(row=0, column=1, sticky=(tk.N, tk.S))
        chapters_list_frame.columnconfigure(0, weight=1)
        chapters_list_frame.rowconfigure(0, weight=1)

        # 오른쪽: 대본 표시 영역
        script_display_frame = ttk.LabelFrame(paned_horizontal, text="대본 뷰어", padding=10)
        paned_horizontal.add(script_display_frame, weight=1)
        script_display_frame.columnconfigure(0, weight=1)
        script_display_frame.rowconfigure(1, weight=1)

        # 챕터 번호 표시
        self.script_chapter_label = ttk.Label(
            script_display_frame,
            text="챕터를 선택하세요",
            font=("맑은 고딕", 11, "bold")
        )
        self.script_chapter_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # 대본 내용 표시 (읽기 전용)
        self.script_viewer = scrolledtext.ScrolledText(
            script_display_frame,
            width=60,
            height=40,
            wrap=tk.WORD,
            font=("맑은 고딕", 10),
            state=tk.DISABLED
        )
        self.script_viewer.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 현재 선택된 챕터 번호 추적
        self.current_selected_chapter_num = None

        # 하단: 원본 JSON 에디터
        editor_frame = ttk.LabelFrame(paned_vertical, text="원본 JSON 에디터", padding=10)
        paned_vertical.add(editor_frame, weight=1)
        editor_frame.columnconfigure(0, weight=1)
        editor_frame.rowconfigure(0, weight=1)

        self.editor = scrolledtext.ScrolledText(
            editor_frame,
            width=120,
            height=30,
            wrap=tk.WORD,  # 줄바꿈 활성화
            font=("Consolas", 10)
        )
        self.editor.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.editor.bind('<KeyRelease>', lambda e: self.mark_unsaved())

        # PanedWindow 참조 저장 (마우스 휠 재바인딩용)
        self.paned = paned_vertical

    def _bind_initial_mousewheel(self):
        """
        초기 마우스 휠 이벤트 바인딩
        원본 create_chapters_tab() 내부의 마우스 휠 바인딩 로직
        """
        def on_mousewheel(event):
            """마우스 휠 스크롤 처리"""
            self.canvas_viewer.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"

        def bind_mousewheel_to_widget(widget):
            """위젯과 모든 자식 위젯에 재귀적으로 마우스 휠 바인딩"""
            widget.bind("<MouseWheel>", on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_to_widget(child)

        # Canvas에 직접 바인딩
        self.canvas_viewer.bind("<MouseWheel>", on_mousewheel)
        self.canvas_viewer.bind("<Enter>", lambda e: self.canvas_viewer.focus_set())

        # Frame과 모든 자식 위젯에 바인딩
        bind_mousewheel_to_widget(self.chapters_viewer_frame)

    def update_display(self):
        """
        화면 업데이트
        원본 update_chapters_display() 메서드의 로직을 완전히 이식
        """
        # 기존 위젯 제거
        for widget in self.chapters_viewer_frame.winfo_children():
            widget.destroy()

        chapters = self.project_data.get_chapters()

        if not chapters:
            ttk.Label(
                self.chapters_viewer_frame,
                text="챕터 정보가 없습니다.",
                font=("맑은 고딕", 11)
            ).pack(pady=20)
            self.editor.delete(1.0, tk.END)
            self.editor.insert(1.0, "[]")
            return

        # 뷰어에 챕터 정보 표시
        for idx, chapter in enumerate(chapters):
            self._create_chapter_widget(idx, chapter)

        # 마우스 휠 이벤트 재바인딩 (새로 생성된 위젯들에)
        self._rebind_mousewheel()

        # 에디터에 JSON 표시
        self.editor.delete(1.0, tk.END)
        json_str = format_json(chapters)
        self.editor.insert(1.0, json_str)

    def _create_chapter_widget(self, idx: int, chapter: dict):
        """
        챕터 뷰어 위젯 생성
        원본 create_chapter_viewer_widget() 메서드의 로직을 완전히 이식

        각 챕터를 카드 형식으로 표시:
        - 챕터 번호와 제목
        - 요약 (스크롤 가능한 텍스트)
        - 분위기
        """
        num = chapter.get('chapter_number', idx + 1)
        frame = ttk.LabelFrame(
            self.chapters_viewer_frame,
            text=f"챕터 {num}",
            padding=15
        )
        frame.pack(fill=tk.X, padx=15, pady=10)

        # 제목
        title_frame = ttk.Frame(frame)
        title_frame.pack(fill=tk.X, pady=5)
        ttk.Label(
            title_frame,
            text="제목:",
            font=("맑은 고딕", 10, "bold"),
            width=12
        ).pack(side=tk.LEFT)
        ttk.Label(
            title_frame,
            text=chapter.get('title', ''),
            font=("맑은 고딕", 10)
        ).pack(side=tk.LEFT)

        # 요약 (스크롤 가능한 텍스트)
        summary_frame = ttk.Frame(frame)
        summary_frame.pack(fill=tk.X, pady=5)
        ttk.Label(
            summary_frame,
            text="요약:",
            font=("맑은 고딕", 10, "bold"),
            width=12
        ).pack(side=tk.LEFT, anchor=tk.N)

        summary_text = scrolledtext.ScrolledText(
            summary_frame,
            width=80,
            height=6,
            wrap=tk.WORD,
            font=("맑은 고딕", 10),
            state=tk.DISABLED
        )
        summary_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 요약 내용 삽입 (읽기 전용으로 설정하기 전에)
        summary_text.config(state=tk.NORMAL)
        summary_text.insert(1.0, chapter.get('summary', ''))
        summary_text.config(state=tk.DISABLED)

        # 분위기
        mood_frame = ttk.Frame(frame)
        mood_frame.pack(fill=tk.X, pady=5)
        ttk.Label(
            mood_frame,
            text="분위기:",
            font=("맑은 고딕", 10, "bold"),
            width=12
        ).pack(side=tk.LEFT)
        ttk.Label(
            mood_frame,
            text=chapter.get('mood', ''),
            font=("맑은 고딕", 10)
        ).pack(side=tk.LEFT)

        # 대본 생성 버튼
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        generate_btn = ttk.Button(
            button_frame,
            text="📝 대본 생성",
            command=lambda n=num: self._generate_script_for_chapter(n),
            width=15
        )
        generate_btn.pack(side=tk.LEFT, padx=5)
        
        # 대본 보기 버튼 (오른쪽 영역에 표시)
        view_script_btn = ttk.Button(
            button_frame,
            text="👁️ 대본 보기",
            command=lambda n=num: self._show_script_for_chapter(n),
            width=15
        )
        view_script_btn.pack(side=tk.LEFT, padx=5)

    def _rebind_mousewheel(self):
        """
        마우스 휠 이벤트 재바인딩
        원본 _bind_mousewheel_to_chapters_viewer() 메서드의 로직을 완전히 이식

        새로 생성된 위젯들에 마우스 휠 이벤트를 다시 바인딩합니다.
        PanedWindow 구조를 탐색하여 Canvas를 찾아 바인딩합니다.
        """
        # PanedWindow에서 Canvas 찾기
        if hasattr(self, 'paned'):
            for pane_name in self.paned.panes():
                pane = self.paned.nametowidget(pane_name)
                for child in pane.winfo_children():
                    if isinstance(child, tk.Canvas):
                        # Canvas 참조 저장
                        canvas = child

                        def on_mousewheel(event):
                            """마우스 휠 스크롤 처리"""
                            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                            return "break"

                        def bind_to_widget(w):
                            """위젯과 모든 자식 위젯에 재귀적으로 마우스 휠 바인딩"""
                            w.bind("<MouseWheel>", on_mousewheel)
                            for c in w.winfo_children():
                                bind_to_widget(c)

                        # Canvas에 직접 바인딩
                        canvas.bind("<MouseWheel>", on_mousewheel)
                        canvas.bind("<Enter>", lambda e, c=canvas: c.focus_set())

                        # chapters_viewer_frame과 모든 자식 위젯에 바인딩
                        bind_to_widget(self.chapters_viewer_frame)
                        return

    def _generate_script_for_chapter(self, chapter_num: int):
        """
        특정 챕터의 대본 생성
        Args:
            chapter_num: 챕터 번호
        """
        self._generate_script(chapter_num, show_message=True)

    def _generate_script(self, chapter_num: int, show_message: bool = True) -> bool:
        """
        챕터 대본 생성 (내부 함수)
        scripts_tab.py의 _generate_script() 로직을 재사용

        Args:
            chapter_num: 챕터 번호
            show_message: 완료 메시지 표시 여부

        Returns:
            생성 성공 여부
        """
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
            if show_message:
                messagebox.showerror("오류", f"챕터 {chapter_num}을 찾을 수 없습니다.")
            return False

        # 시놉시스 정보
        synopsis = self.project_data.get_synopsis()

        # 인물 정보
        characters = self.project_data.get_characters()
        characters_info = self._format_characters_for_prompt(characters)

        # 이전 챕터 대본 (연속성 유지)
        previous_script = ""
        if chapter_num > 1:
            prev_chapter = None
            for ch in chapters:
                if ch.get('chapter_number') == chapter_num - 1:
                    prev_chapter = ch
                    break
            if prev_chapter and prev_chapter.get('script'):
                prev_script_full = prev_chapter.get('script', '')
                # 이전 대본의 마지막 1000자만 포함
                if len(prev_script_full) > 1000:
                    prev_script_full = "..." + prev_script_full[-1000:]
                previous_script = prev_script_full

        # LLM 호출
        try:
            script = self.content_generator.generate_script(
                chapter,
                synopsis,
                characters_info,
                previous_script
            )

            if not script:
                if show_message:
                    messagebox.showerror("오류", "대본 생성에 실패했습니다.")
                return False

            # 챕터 데이터에 대본 저장
            chapter['script'] = script.strip()
            chapter['script_length'] = len(script.strip())
            chapter['script_generated_at'] = datetime.now().isoformat()

            # 데이터 업데이트
            chapters[chapter_index] = chapter
            self.project_data.set_chapters(chapters)

            # 파일에 즉시 자동 저장
            try:
                # 단일 챕터만 저장
                single_chapter_list = [chapter]
                self.file_service.save_chapters(single_chapter_list)
            except Exception as save_error:
                print(f"경고: 대본은 생성되었으나 저장 중 오류 발생: {save_error}")

            # 화면 업데이트
            self.update_display()
            
            # 오른쪽 대본 영역 업데이트
            self._update_script_display(chapter_num)

            if show_message:
                messagebox.showinfo("완료", f"챕터 {chapter_num}의 대본이 생성되고 자동 저장되었습니다.\n글자 수: {len(script.strip())}자")

            return True

        except Exception as e:
            if show_message:
                messagebox.showerror("오류", f"대본 생성 중 오류 발생:\n{e}")
            return False

    def _generate_all_scripts(self):
        """
        모든 챕터의 대본 생성
        scripts_tab.py의 _generate_all_chapters() 로직을 재사용
        """
        chapters = self.project_data.get_chapters()
        if not chapters:
            messagebox.showwarning("경고", "챕터 정보가 없습니다.")
            return

        # 확인 대화상자
        result = messagebox.askyesno(
            "대본 일괄 생성",
            f"{len(chapters)}개 챕터의 대본을 모두 생성하시겠습니까?\n\n"
            f"이 작업은 시간이 걸릴 수 있습니다."
        )
        if not result:
            return

        # 모든 챕터 대본 생성
        success_count = 0
        for ch in chapters:
            chapter_num = ch.get('chapter_number', 0)
            if chapter_num > 0:
                if self._generate_script(chapter_num, show_message=False):
                    success_count += 1

        messagebox.showinfo("완료", f"{success_count}/{len(chapters)}개 챕터의 대본이 생성되었습니다.")
        self.update_display()  # 화면 업데이트

    def _show_script_for_chapter(self, chapter_num: int):
        """
        특정 챕터의 대본을 오른쪽 영역에 표시
        Args:
            chapter_num: 챕터 번호
        """
        self._update_script_display(chapter_num)

    def _update_script_display(self, chapter_num: int):
        """
        오른쪽 대본 표시 영역 업데이트
        Args:
            chapter_num: 챕터 번호
        """
        # 챕터 찾기
        chapters = self.project_data.get_chapters()
        chapter = None
        for ch in chapters:
            if ch.get('chapter_number') == chapter_num:
                chapter = ch
                break

        if not chapter:
            return

        # 현재 선택된 챕터 번호 저장
        self.current_selected_chapter_num = chapter_num

        # 챕터 번호 라벨 업데이트
        chapter_title = chapter.get('title', '')
        if chapter_title:
            self.script_chapter_label.config(text=f"챕터 {chapter_num}: {chapter_title}")
        else:
            self.script_chapter_label.config(text=f"챕터 {chapter_num}")

        # 대본 내용 업데이트
        script = chapter.get('script', '')
        self.script_viewer.config(state=tk.NORMAL)
        self.script_viewer.delete(1.0, tk.END)
        
        if script:
            self.script_viewer.insert(1.0, script)
        else:
            self.script_viewer.insert(1.0, f"챕터 {chapter_num}의 대본이 아직 생성되지 않았습니다.\n\n'대본 생성' 버튼을 눌러 자동 생성하세요.")
        
        self.script_viewer.config(state=tk.DISABLED)

    def _format_characters_for_prompt(self, characters: list) -> str:
        """
        인물 정보를 프롬프트용 텍스트로 포맷팅
        scripts_tab.py의 로직을 재사용
        """
        if not characters:
            return "등장인물 정보 없음"

        result = []
        for char in characters:
            name = char.get('name', '알 수 없음')
            age = char.get('age', '불명')
            gender = char.get('gender', '불명')
            personality = char.get('personality', '불명')
            background = char.get('background', '불명')

            char_info = f"- {name} ({age}세, {gender}): {personality}"
            if background and background != '불명':
                char_info += f"\n  배경: {background}"
            result.append(char_info)

        return '\n'.join(result)

    def save(self) -> bool:
        """
        데이터 저장
        JSON 에디터의 내용을 파싱하여 챕터 데이터로 저장
        """
        json_str = self.editor.get(1.0, tk.END).strip()
        if json_str:
            chapters = safe_json_loads(json_str)
            if chapters is not None:
                self.project_data.set_chapters(chapters)
                return self.file_service.save_chapters(chapters)
        return False
